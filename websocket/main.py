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


ORIGINS = ["*"]

LOG_LEVEL = "DEBUG"
LOG_FILE = "ws.log"

root_logger = logging.getLogger()
logger = logging.getLogger("ws")


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


class SubscribeData(pydantic.BaseModel):
    client_id: pydantic.StrictStr
    channel: pydantic.StrictStr


class UnsubscribeData(pydantic.BaseModel):
    client_id: pydantic.StrictStr
    channel: pydantic.StrictStr


async def user_notify(request):
    logger.info(
        "URL {} has been called from {}".format(request.url, request.client.host)
    )

    request_data = await request.json()
    if not isinstance(request_data, dict):
        message = "Request body is not a JSON object"
        logger.error(message)
        return JSONResponse({"ok": False, "error_message": message})

    try:
        validated_data = UserNotifyData(**request_data)
    except pydantic.ValidationError:
        message = "Validation error"
        logger.error(message)
        return JSONResponse({"ok": False, "error_message": message})
    else:
        cleaned_data = validated_data.dict()

    channel = cleaned_data["channel"]
    message = cleaned_data["message"]
    logger.debug("destination_channel={}, message={}".format(channel, message))

    has_message_been_delivered, error_message = await App.notify(channel, message)

    return JSONResponse(
        {
            "ok": True,
            "delivered": has_message_been_delivered,
            "error_message": error_message,
        }
    )


async def subscribe(request):
    logger.info(
        "URL {} has been called from {}".format(request.url, request.client.host)
    )

    request_data = await request.json()
    if not isinstance(request_data, dict):
        message = "Request body is not a JSON object"
        logger.error(message)
        return JSONResponse({"ok": False, "error_message": message})

    try:
        validated_data = SubscribeData(**request_data)
    except pydantic.ValidationError:
        message = "Validation error"
        logger.error(message)
        return JSONResponse({"ok": False, "error_message": message})
    else:
        cleaned_data = validated_data.dict()

    client_id = cleaned_data["client_id"]
    channel = cleaned_data["channel"]

    App.subscribe(client_id, channel)

    return JSONResponse({"ok": True})


async def unsubscribe(request):
    logger.info(
        "URL {} has been called from {}".format(request.url, request.client.host)
    )

    request_data = await request.json()
    if not isinstance(request_data, dict):
        message = "Request body is not a JSON object"
        logger.error(message)
        return JSONResponse({"ok": False, "error_message": message})

    try:
        validated_data = UnsubscribeData(**request_data)
    except pydantic.ValidationError:
        message = "Validation error"
        logger.error(message)
        return JSONResponse({"ok": False, "error_message": message})
    else:
        cleaned_data = validated_data.dict()

    client_id = cleaned_data["client_id"]
    channel = cleaned_data["channel"]

    App.unsubscribe(client_id, channel)

    return JSONResponse({"ok": True})


async def get_stats(request):
    payload = {
        "client_id_2_websocket": {
            k: v.headers["sec-websocket-key"]
            for k, v in App.client_id_2_websocket.items()
        },
        "channels": {k: list(v) for k, v in App.channels.items()},
    }
    logger.info(payload)
    return JSONResponse(payload)


class App(WebSocketEndpoint):
    client_id_2_websocket = {}
    channels = {}

    async def on_connect(self, websocket):
        await websocket.accept()

        client_id = websocket.path_params["client_id"]

        logger.info("Websocket {} connected".format(client_id))

        self.reference(client_id, websocket)

    def reference(self, client_id, websocket):
        self.client_id_2_websocket[client_id] = websocket

    def dereference(self, client_id):
        self.client_id_2_websocket.pop(client_id)

    @classmethod
    def subscribe(cls, client_id, channel):
        if channel not in cls.channels:
            cls.channels[channel] = set()

        cls.channels[channel].add(client_id)

    @classmethod
    def unsubscribe(cls, client_id, channel):
        if channel not in cls.channels:
            return

        cls.channels[channel].discard(client_id)

        # Clean to avoid having a growing list of empty channels
        if not cls.channels[channel]:
            cls.channels.pop(channel)

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
            message = "No websocket is currently subscribing to channel '{}': skipping".format(
                channel
            )
            logger.warning(message)
            return False, message

        json_message = json.dumps(message)

        logger.debug(
            "Sending message '{}' to {} client(s)".format(
                json_message, len(cls.channels[channel])
            )
        )
        for client_id in cls.channels[channel]:
            logger.debug("Sending to ws {}".format(client_id))
            await cls.client_id_2_websocket[client_id].send_text(json_message)

        return True, ""

    async def on_disconnect(self, websocket, close_code):
        client_id = websocket.path_params["client_id"]
        logger.info("Websocket {} disconnected".format(client_id))

        self.unsubscribe_from_all_channels(client_id, websocket)
        self.dereference(client_id)


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=ORIGINS,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    ),
]


routes = [
    Route("/subscribe", subscribe, methods=["POST"]),
    Route("/unsubscribe", unsubscribe, methods=["POST"]),
    Route("/notify", user_notify, methods=["POST"]),
    Route("/get_stats", get_stats, methods=["GET"]),
    WebSocketRoute("/wss/{client_id}", App),
]

app = Starlette(routes=routes, middleware=middleware)
