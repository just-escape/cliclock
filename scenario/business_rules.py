import scenario
from scenario.web_socket import web_socket_notifier as wsn, MessageType


def get_scenario_puzzles_data(s):
    puzzles = scenario.models.Puzzle.objects.filter(scenario=s).all()

    data = [
        {
            "id": puzzle.id,
            "name": puzzle.name,
            "description": puzzle.description,
            "picture": puzzle.picture.url,
        } for puzzle in puzzles
    ]

    return data


def notify_player(player):
    data = {
        "name": player.character.name,
        "avatar": player.character.avatar.url,
        "klass": player.character.klass,
        "money": player.money,
        "reputation": player.reputation if player.character.has_reputation else None,
    }

    channel = player.slug
    wsn.notify(channel, {"type": MessageType.PUT_INVENTORY, "data": data})


def notify_inventory(player):
    player_items = scenario.models.PlayerItem.objects.filter(player=player).select_related('item').all()
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
    displayed_puzzle = scenario.models.PlayerPuzzle.objects.filter(player=player, is_displayed=True).first()
    if displayed_puzzle is None:
        return

    data = {
        "puzzle_id": displayed_puzzle.puzzle_id,
        "status": displayed_puzzle.status,
    }

    channel = player.slug
    wsn.notify(channel, {"type": MessageType.PUT_DISPLAYED_PUZZLE, "data": data})
