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

    puzzles_data = business_rules.get_scenario_puzzles_data(instance.scenario)

    scenario_data = {
        "puzzles": puzzles_data,
    }

    return JsonResponse(scenario_data)


def get_player_data(request, player_slug):
    player = scenario.models.Player.objects.filter(slug=player_slug).select_related('character').first()
    if player is None:
        return JsonResponse({"ok": False})

    business_rules.notify_player(player)
    business_rules.notify_inventory(player)
    business_rules.notify_displayed_puzzle(player)

    return JsonResponse({"ok": True})


@transaction.atomic
def display_puzzle(request, player_slug, puzzle_slug):
    player_puzzle = scenario.models.PlayerPuzzle.objects.filter(player__slug=player_slug, puzzle__slug=puzzle_slug).first()
    if player_puzzle is None:
        return JsonResponse({"ok": False})

    player_puzzle.is_displayed = True
    player_puzzle.save()  # Triggers notification

    return JsonResponse({"ok": True})


@transaction.atomic
def unlock_puzzle(request, player_slug, puzzle_slug):
    player_puzzle = scenario.models.PlayerPuzzle.objects.filter(player__slug=player_slug, puzzle__slug=puzzle_slug).first()
    if player_puzzle is None:
        return JsonResponse({"ok": False})

    # TODO: try/catch
    # key_as_player_items = request.POST["key_as_player_items"]
    key_as_player_items = [{"id": 1, "item_id": 2}]

    player_item_ids = [x["id"] for x in key_as_player_items]
    player_items = scenario.models.PlayerItem.objects.filter(id__in=player_item_ids).all()

    if len(player_items) != len(key_as_player_items):
        # Something is wrong or the player might want to glitch
        return JsonResponse({"ok": False})

    if player_puzzle.status != scenario.models.PlayerPuzzleStatus.OBSERVED.value:
        return JsonResponse({"ok": False})

    puzzle_keys = sorted([x.id for x in player_puzzle.puzzle.keys.all()])

    if keys != puzzle_keys:
        return JsonResponse({"ok": False})

    player_puzzle.status = scenario.models.PlayerPuzzleStatus.UNLOCKED.value
    player_puzzle.save()

    # Remove keys from inventory
    player_items.delete()

    return JsonResponse({"ok": True})


@transaction.atomic
def solve_puzzle(request, player_slug, puzzle_slug):
    player_puzzle = scenario.models.PlayerPuzzle.objects.filter(player__slug=player_slug, puzzle__slug=puzzle_slug).first()
    if player_puzzle is None:
        return JsonResponse({"ok": False})

    # TODO: try/catch
    # answer = request.POST["answer"]
    answer = "abc"

    if player_puzzle.status != scenario.models.PlayerPuzzleStatus.UNLOCKED.value:
        return JsonResponse({"ok": False})

    if answer != player_puzzle.puzzle.answer:
        return JsonResponse({"ok": False})

    player_puzzle.status = scenario.models.PlayerPuzzleStatus.SOLVED.value
    player_puzzle.save()

    # Reward the bounty
    position_for_bounty = 0
    last_item_in_inventory = scenario.models.PlayerItem.objects.filter(player=player).order_by('-position').first()
    if last_item_in_inventory:
        position_for_bounty = last_item_in_inventory.position + 1

    for bounty_item in puzzle.bounty.all():
        scenario.models.PlayerItem.objects.create(player=player, item=bounty_item, position=position_for_bounty)
        position_for_bounty += 1

    return JsonResponse({"ok": True})


@transaction.atomic
def move_item(request, player_slug):
    player = scenario.models.Player.objects.filter(slug=player_slug).first()
    if player is None:
        return JsonResponse({"ok": False})

    # TODO: try/catch
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
    inventory = [{"id": x.id, "item_id": x.item_id} for x in new_player_items]

    channel = player.slug

    wsn.notify(channel, {"type": MessageType.PUT_INVENTORY, "data": inventory})

    return JsonResponse({"ok": True})
