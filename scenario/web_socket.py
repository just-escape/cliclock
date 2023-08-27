import json
import requests
import logging
import enum


logger = logging.getLogger()


class MessageType(str, enum.Enum):
    PUT_PLAYER = "put_player"
    PUT_INVENTORY = "put_inventory"


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, dt.datetime):
            return obj.isoformat()
        elif isinstance(obj, dt.date):
            return obj.isoformat()
        else:
            return super().default(obj)


class WebSocketNotifier:
    def __init__(self):
        self.enabled = True
        self.url = "http://localhost:31300/notify"

    def notify(self, channel, message):
        logger.info(f"Pushing on channel='{channel}' the message='{message}'")
        if not self.enabled:
            logger.info("Notifications are disabled: aborting push")

        data = {'channel': channel, 'message': message}

        try:
            json_data = json.dumps(data, cls=CustomJsonEncoder)
        except TypeError:
            logger.error(f"An error occurred while trying to encode '{data}' in json: aborting", exc_info=True)

        try:
            requests.post(
                self.url,
                data=json_data,
                headers={'Content-Type': 'application/json'},
            )
        except requests.RequestException:
            logger.error("An error occurred while trying to push the notification: aborting", exc_info=True)


web_socket_notifier = WebSocketNotifier()