from django.shortcuts import render
import scenario
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_POST
from scenario.web_socket import web_socket_notifier as wsn, MessageType
import logging
from scenario import business_rules

logger = logging.getLogger()


def get_scenario_data(request, instance_slug):
    instance = scenario.models.Instance.objects.filter(slug=instance_slug).get()

    items_data = business_rules.get_scenario_items_data(instance.scenario)
    puzzles_data = business_rules.get_scenario_puzzles_data(instance.scenario)

    scenario_data = {
        "items": items_data,
        "puzzles": puzzles_data,
    }

    return JsonResponse(scenario_data)


def get_player_data(request, player_slug):
    player = scenario.models.Player.objects.filter(slug=player_slug).select_related('character').first()
    player_items = scenario.models.PlayerItem.objects.filter(player=player).order_by('position').all()
    player_puzzles = scenario.models.PlayerPuzzle.objects.filter(player=player).all()

    inventory = [{"id": x.id, "item_id": x.item_id} for x in player_items if x.puzzle is None]

    log = [
        {
            "puzzle_id": player_puzzle.puzzle_id,
            "status": player_puzzle.status,
        } for player_puzzle in player_puzzles
    ]

    # should not be more than one
    displayed_puzzle = {}
    for player_puzzle in player_puzzles:
        if player_puzzle.is_displayed:
            displayed_puzzle["puzzle_id"] = player_puzzle.puzzle_id
            displayed_puzzle["status"] = player_puzzle.status

    logger.warning(displayed_puzzle)

    player_data = {
        "player": {
            "name": player.character.name,
            "avatar": player.character.avatar.url,
            "klass": player.character.klass,
            "money": player.money,
            "reputation": player.reputation if player.character.has_reputation else None,
        },
        "inventory": inventory,
        "displayed_puzzle": displayed_puzzle,
        "log": log,
    }

    return JsonResponse(player_data)


@transaction.atomic
def display_puzzle(request, player_slug, puzzle_slug):
    player_puzzle = scenario.models.PlayerPuzzle.objects.filter(player__slug=player_slug, puzzle__slug=puzzle_slug).first()
    if player_puzzle is None:
        return JsonResponse({"ok": False})

    player_puzzle.is_displayed = True
    player_puzzle.save()  # Triggers notification

    return JsonResponse({"ok": True})


@transaction.atomic
def move_item(request, player_slug):
    player = scenario.models.Player.objects.filter(slug=player_slug).first()
    if player is None:
        return JsonResponse({"ok": False})

    # moved_item_id = request.POST["id"]
    # new_index = request.GET["new_index"]
    moved_item_id = 1
    new_index = 2

    player_items = list(scenario.models.PlayerItem.objects.filter(player=player).order_by('position').all())

    moved_item = [x for x in player_items if x.id == moved_item_id]
    if moved_item:
        player_items.remove(moved_item[0])
        player_items.insert(new_index, moved_item[0])

    for index, player_item in enumerate(player_items):
        scenario.models.PlayerItem.objects.filter(id=player_item.id).update(position=index)

    new_player_items = scenario.models.PlayerItem.objects.filter(player=player).order_by('position').all()
    inventory = [{"id": x.id, "item_id": x.item_id} for x in new_player_items if x.puzzle is None]

    wsn.notify(channel, {"type": MessageType.PUT_INVENTORY, "data": inventory})

    return JsonResponse({"ok": True})
