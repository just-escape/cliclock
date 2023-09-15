import scenario
from scenario.web_socket import web_socket_notifier as wsn, MessageType


def notify_instance(player):
    data = {
        "status": "PLAYING",
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


def notify_inventory(player):
    player_items = scenario.models.PlayerItem.objects.filter(player=player).select_related('item').order_by('position').all()
    inventory = [
        {
            "id": x.id,
            "item_id": x.item_id,
            "image": x.item.image.url,
            "name": x.item.name,
            "description": x.item.description,
        } for x in player_items
    ]

    channel = player.slug
    wsn.notify(channel, {"type": MessageType.PUT_INVENTORY, "data": inventory})


def notify_displayed_puzzle(player):
    displayed_puzzle = scenario.models.PlayerPuzzle.objects.filter(player=player, is_displayed=True).select_related('puzzle').first()
    if displayed_puzzle is None:
        return

    data = {
        "name": displayed_puzzle.puzzle.name,
        "description": displayed_puzzle.puzzle.description,
        "picture": displayed_puzzle.puzzle.picture.url,
        "puzzle_id": displayed_puzzle.puzzle_id,
        "puzzle_slug": displayed_puzzle.puzzle.slug,
        "status": displayed_puzzle.status,
        "kind": displayed_puzzle.puzzle.kind,
    }

    if displayed_puzzle.status in [scenario.models.PlayerPuzzleStatus.UNLOCKED.value, scenario.models.PlayerPuzzleStatus.SOLVED.value]:
        keys = displayed_puzzle.puzzle.keys.order_by('id').all()
        data["keys"] = [
            {
                "item_id": x.id,
                "image": x.image.url,
                "name": x.name,
                "description": x.description,
            } for x in keys
        ]
    if displayed_puzzle.status == scenario.models.PlayerPuzzleStatus.SOLVED.value:
        bounty = displayed_puzzle.puzzle.bounty.order_by('id').all()
        data["bounty"] = [
            {
                "item_id": x.id,
                "image": x.image.url,
                "name": x.name,
                "description": x.description,
            } for x in bounty
        ]

    channel = player.slug
    wsn.notify(channel, {"type": MessageType.PUT_DISPLAYED_PUZZLE, "data": data})


def notify_trade(trade):
    peer_a_data = {
        "trade_id": trade.id,
        "my_money": trade.money_a,
        "my_status": trade.status_a,
        "my_items": [],
        "peer_name": trade.peer_b.name,
        "peer_money": trade.money_b,
        "peer_status": trade.status_b,
        "peer_items": [],
    }

    peer_b_data = {
        "trade_id": trade.id,
        "my_money": trade.money_b,
        "my_status": trade.status_b,
        "my_items": [],
        "peer_name": trade.peer_a.name,
        "peer_money": trade.money_a,
        "peer_status": trade.status_a,
        "peer_items": [],
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
    }

    peer_a_channel = peer_a.slug
    wsn.notify(peer_a_channel, {"type": MessageType.PUT_TRADE, "data": peer_a_data})

    peer_b_channel = peer_b.slug
    wsn.notify(peer_b_channel, {"type": MessageType.PUT_TRADE, "data": peer_b_data})
