import enum
import scenario
from scenario.web_socket import web_socket_notifier as wsn, MessageType


class MessageLevel(enum.Enum):
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"


def notify_message(player, content, level=MessageLevel.ERROR):
    data = {
        "content": content,
        "level": level.value,
    }

    channel = player.slug
    wsn.notify(channel, {"type": MessageType.PUSH_MESSAGE, "data": data})


def notify_instance(player, instance):
    data = {
        "status": instance.status,
        "title": instance.modal_title,
        "text": instance.modal_text,
    }

    channel = player.slug
    wsn.notify(channel, {"type": MessageType.PUT_INSTANCE, "data": data})


def notify_player(player):
    data = {
        "name": player.name,
        "avatar": player.avatar.url,
        "role": player.role,
        "team": player.team,
        "money": player.money,
        "reputation": player.reputation if player.role == scenario.models.PlayerRole.ARTIST.value else None,
    }

    channel = player.slug
    wsn.notify(channel, {"type": MessageType.PUT_PLAYER, "data": data})


def serialize_item(item):
    return {
        "item_id": item.id,
        "image": item.image.url,
        "name": item.name,
        "description": item.description,
    }


def serialize_player_item(player_item):
    return {
        "id": player_item.id,
        "item_id": player_item.item_id,
        "image": player_item.item.image.url,
        "name": player_item.item.name,
        "description": player_item.item.description,
    }


def notify_inventory(player):
    player_items = scenario.models.PlayerItem.objects.filter(player=player).select_related('item').order_by('position').all()
    inventory = [serialize_player_item(x) for x in player_items]

    channel = player.slug
    wsn.notify(channel, {"type": MessageType.PUT_INVENTORY, "data": inventory})


def notify_displayed_puzzle(player):
    displayed_puzzle = scenario.models.PlayerPuzzle.objects.filter(player=player, is_displayed=True).select_related('puzzle').first()
    if displayed_puzzle is None:
        return

    data = {
        "puzzle_slug": displayed_puzzle.puzzle.slug,
        "puzzle_id": displayed_puzzle.puzzle_id,
        "status": displayed_puzzle.status,
        "kind": displayed_puzzle.puzzle.kind,
        "name": displayed_puzzle.puzzle.name,
        "picture": displayed_puzzle.puzzle.picture.url,
        "riddle": displayed_puzzle.puzzle.riddle,
    }

    if displayed_puzzle.status in [scenario.models.PlayerPuzzleStatus.UNLOCKED.value, scenario.models.PlayerPuzzleStatus.SOLVED.value]:
        keys = displayed_puzzle.puzzle.keys.order_by('id').all()
        data["keys"] = [serialize_item(x) for x in keys]
    if displayed_puzzle.status == scenario.models.PlayerPuzzleStatus.SOLVED.value:
        bounty = displayed_puzzle.puzzle.bounty.order_by('id').all()
        data["bounty"] = [serialize_item(x) for x in bounty]

    channel = player.slug
    wsn.notify(channel, {"type": MessageType.PUT_DISPLAYED_PUZZLE, "data": data})


def notify_trade(trade):
    serialized_player_items_a = [
        serialize_player_item(x) for x in trade.player_items_a.all()]
    serialized_player_items_b = [
        serialize_player_item(x) for x in trade.player_items_b.all()]

    peer_a_data = {
        "trade_id": trade.id,
        "my_money": trade.money_a,
        "my_status": trade.status_a,
        "my_items": serialized_player_items_a,
        "peer_name": trade.peer_b.name,
        "peer_money": trade.money_b,
        "peer_status": trade.status_b,
        "peer_items": serialized_player_items_b,
        "peer_slug": trade.peer_b.slug,
        "peer_role": trade.peer_b.role,
    }

    peer_b_data = {
        "trade_id": trade.id,
        "my_money": trade.money_b,
        "my_status": trade.status_b,
        "my_items": serialized_player_items_b,
        "peer_name": trade.peer_a.name,
        "peer_money": trade.money_a,
        "peer_status": trade.status_a,
        "peer_items": serialized_player_items_a,
        "peer_slug": trade.peer_a.slug,
        "peer_role": trade.peer_a.role,
    }

    peer_a_channel = trade.peer_a.slug
    wsn.notify(peer_a_channel, {"type": MessageType.PUT_TRADE, "data": peer_a_data})

    peer_b_channel = trade.peer_b.slug
    wsn.notify(peer_b_channel, {"type": MessageType.PUT_TRADE, "data": peer_b_data})


def notify_no_trade(peer_a, peer_b):
    peer_a_data = {
        "trade_id": None,
        "my_money": 0,
        "my_status": None,
        "my_items": [],
        "peer_name": "",
        "peer_money": 0,
        "peer_status": None,
        "peer_items": [],
        "peer_slug": "",
        "peer_role": "",
    }

    peer_b_data = {
        "trade_id": None,
        "my_money": 0,
        "my_status": None,
        "my_items": [],
        "peer_name": "",
        "peer_money": 0,
        "peer_status": None,
        "peer_items": [],
        "peer_slug": "",
        "peer_role": "",
    }

    peer_a_channel = peer_a.slug
    wsn.notify(peer_a_channel, {"type": MessageType.PUT_TRADE, "data": peer_a_data})

    peer_b_channel = peer_b.slug
    wsn.notify(peer_b_channel, {"type": MessageType.PUT_TRADE, "data": peer_b_data})
