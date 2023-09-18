import requests
from pprint import pprint
from django.core.management.base import BaseCommand, CommandError
from scenario.web_socket import web_socket_notifier as wsn


class Command(BaseCommand):
    help = "Get WS Stats"

    def add_arguments(self, parser):
        parser.add_argument("-s", "--slug", nargs="+", type=str)

    def handle(self, *args, **options):
        r = requests.get(wsn.url.replace('notify', 'get_stats'))
        pprint(r.json())
