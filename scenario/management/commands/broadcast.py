from django.core.management.base import BaseCommand, CommandError
from scenario import models as sm
from scenario.web_socket import web_socket_notifier as wsn, MessageType as MT


class Command(BaseCommand):
    help = "Broadcast something to all players"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--slug", nargs="+", type=str)
        parser.add_argument("-m", "--message", default="", type=str)
        parser.add_argument("-n", "--notification", default="reload", type=str)

    @staticmethod
    def notify_from_slug(slug, notification, message):
        if notification == "reload":
            wsn.notify(slug, {"type": MT.FORCE_RELOAD})
        elif notification == "info":
            wsn.notify(slug, {"type": MT.PUSH_MESSAGE, "data": {"content": message, "level": "info"}})
        elif notification == "success":
            wsn.notify(slug, {"type": MT.PUSH_MESSAGE, "data": {"content": message, "level": "success"}})
        elif notification == "error":
            wsn.notify(slug, {"type": MT.PUSH_MESSAGE, "data": {"content": message, "level": "error"}})
        else:
            print("Do nothing")

    def handle(self, *args, **options):
        """
        PUSH_MESSAGE = "push_message"
        PUT_INSTANCE = "put_instance"
        PUT_PLAYER = "put_player"
        PUT_INVENTORY = "put_inventory"
        PUT_DISPLAYED_PUZZLE = "put_displayed_puzzle"
        PUT_TRADE = "put_trade"
        FORCE_RELOAD = "force_reload"

        level = info / error / success
        """

        all_players = not bool(options["slug"])

        if all_players:
            for p in sm.Player.objects.all():
                self.notify_from_slug(p.slug, options["notification"], options["message"])

        else:
            for s in options["slug"]:
                self.notify_from_slug(s, options["notification"], options["message"])
