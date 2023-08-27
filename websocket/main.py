import time
import json
import typing
import logging
from logging.handlers import RotatingFileHandler

import pydantic

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import WebSocketRoute, Route
from starlette.responses import JSONResponse


ORIGINS = ['*']

LOG_LEVEL = 'DEBUG'
LOG_FILE = 'ws.log'

root_logger = logging.getLogger()
logger = logging.getLogger('ws')


def configure_logging():
    # Root logger
    root_logger.setLevel(LOG_LEVEL)

    stream_handler = logging.StreamHandler()

    root_logger.addHandler(stream_handler)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=104857600, backupCount=10)

    logger.addHandler(file_handler)
    logger.setLevel(LOG_LEVEL)


configure_logging()


class UserNotifyData(pydantic.BaseModel):
    channel: pydantic.StrictStr
    message: typing.Any


async def user_notify(request):
    logger.info("URL {} has been called from {}".format(request.url, request.client.host))

    if request.headers.get('Content-Type', '').lower() != 'application/json':
        message = "Content-Type header is not 'application/json'"
        logger.error(message)
        return JSONResponse({'ok': False, 'error_message': message})

    request_data = await request.json()
    if type(request_data) is not dict:
        message = "Request body is not a JSON object"
        logger.error(message)
        return JSONResponse({'ok': False, 'error_message': message})

    try:
        validated_data = UserNotifyData(**request_data)
    except pydantic.ValidationError:
        message = "Validation error"
        logger.error(message)
        return JSONResponse({'ok': False, 'error_message': message})
    else:
        cleaned_data = validated_data.dict()

    channel = cleaned_data['channel']
    message = cleaned_data['message']
    logger.debug("destination_channel={}, message={}".format(channel, message))

    has_message_been_delivered, error_message = await App.notify(channel, message)

    return JSONResponse({'ok': True, 'delivered': has_message_been_delivered, 'error_message': error_message})


class App(WebSocketEndpoint):
    ws_key_2_websocket = {}
    channels = {}

    async def on_connect(self, websocket):
        await websocket.accept()

        ws_key = websocket.headers['sec-websocket-key']
        sid = websocket.path_params['sid']

        logger.info("Websocket {} connected to channel {}".format(ws_key, sid))

        self.reference(ws_key, websocket)
        self.subscribe(ws_key, sid)

    def reference(self, ws_key, websocket):
        self.ws_key_2_websocket[ws_key] = websocket

    def dereference(self, ws_key):
        self.ws_key_2_websocket.pop(ws_key)

    def subscribe(self, ws_key, channel):
        if channel not in self.channels:
            self.channels[channel] = set()
        self.channels[channel].add(ws_key)

    def unsubscribe_from_all_channels(self, ws_key, websocket):
        channels_to_delete = []
        for channel, subscribers in self.channels.items():
            subscribers.discard(ws_key)

            # Clean to avoid having a growing list of empty channels
            if not self.channels[channel]:
                channels_to_delete.append(channel)

        for channel in channels_to_delete:
            self.channels.pop(channel)

    @classmethod
    async def notify(cls, channel, message):
        if channel not in cls.channels:
            message = "No websocket is currently subscribing to channel '{}': skipping".format(channel)
            logger.warning(message)
            return False, message

        json_message = json.dumps(message)

        logger.debug("Sending message '{}' to {} client(s)".format(json_message, len(cls.channels[channel])))
        for ws_key in cls.channels[channel]:
            logger.debug("Sending to ws {}".format(ws_key))
            await cls.ws_key_2_websocket[ws_key].send_text(json_message)

        return True, ""

    async def on_disconnect(self, websocket, close_code):
        ws_key = websocket.headers['sec-websocket-key']
        logger.info("Websocket {} disconnected".format(ws_key))

        self.unsubscribe_from_all_channels(ws_key, websocket)
        self.dereference(ws_key)


middleware = [
    Middleware(CORSMiddleware, allow_origins=[ORIGINS], allow_methods=['get', 'post', 'options'], allow_headers=['*']),
]


routes = [
    Route("/notify", user_notify, methods=['POST']),
    WebSocketRoute("/wss/{sid}", App),
]

app = Starlette(routes=routes, middleware=middleware)

