import scenario
from scenario.web_socket import web_socket_notifier as wsn, MessageType


def notify_player(player):
    data = {
        "name": player.character.name,
        "avatar": player.character.avatar.url,
        "klass": player.character.klass,
        "money": player.money,
        "reputation": player.reputation if player.character.has_reputation else None,
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
        "status": displayed_puzzle.status,
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
