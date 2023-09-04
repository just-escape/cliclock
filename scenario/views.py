import json
from django.shortcuts import render
import scenario
from django.http import JsonResponse
from django.db import transaction
from scenario.web_socket import web_socket_notifier as wsn, MessageType
import logging
from scenario import business_rules
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger()


def get_player_data(request, player_slug):
    player = scenario.models.Player.objects.filter(slug=player_slug).select_related('character').first()
    if player is None:
        return JsonResponse({"ok": False})

    business_rules.notify_player(player)
    business_rules.notify_inventory(player)
    business_rules.notify_displayed_puzzle(player)

    return JsonResponse({"ok": True})


@transaction.atomic
def player_exist(request, player_slug):
    player = scenario.models.Player.objects.filter(slug=player_slug).select_related('character').first()
    if player is None:
        return JsonResponse({"exist": False, "name": ""})

    return JsonResponse({"exist": True, "name": player.character.name})


@transaction.atomic
def display_puzzle(request, player_slug, puzzle_slug):
    player_puzzle = scenario.models.PlayerPuzzle.objects.filter(player__slug=player_slug, puzzle__slug=puzzle_slug).first()
    if player_puzzle is None:
        player = scenario.models.Player.objects.filter(slug=player_slug).first()
        puzzle = scenario.models.Puzzle.objects.filter(slug=puzzle_slug).first()

        if puzzle is None or player is None:
            return JsonResponse({"ok": False})

        player_puzzle = scenario.models.PlayerPuzzle(
            player=player,
            puzzle=puzzle,
            status=scenario.models.PlayerPuzzleStatus.OBSERVED.value,
        )

    player_puzzle.is_displayed = True
    player_puzzle.save()  # Triggers notification

    return JsonResponse({"ok": True})


@transaction.atomic
@csrf_exempt
def unlock_puzzle(request, player_slug, puzzle_slug):
    player_puzzle = scenario.models.PlayerPuzzle.objects.filter(player__slug=player_slug, puzzle__slug=puzzle_slug).first()
    if player_puzzle is None:
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    key_as_player_items = post_data.get("key_as_player_items")
    if key_as_player_items is None:
        return JsonResponse({"ok": False})

    player_item_ids = [x["id"] for x in key_as_player_items]
    player_items = scenario.models.PlayerItem.objects.filter(id__in=player_item_ids).all()

    if len(player_items) != len(key_as_player_items):
        # Something is wrong or the player might want to glitch
        return JsonResponse({"ok": False})

    if player_puzzle.status != scenario.models.PlayerPuzzleStatus.OBSERVED.value:
        return JsonResponse({"ok": False})

    puzzle_keys = sorted([x.id for x in player_puzzle.puzzle.keys.all()])

    provided_keys = sorted([x['item_id'] for x in key_as_player_items])
    if provided_keys != puzzle_keys:
        return JsonResponse({"ok": False})

    player_puzzle.status = scenario.models.PlayerPuzzleStatus.UNLOCKED.value
    player_puzzle.save()

    # Remove keys from inventory
    player_items.delete()

    return JsonResponse({"ok": True})


@transaction.atomic
@csrf_exempt
def solve_puzzle(request, player_slug, puzzle_slug):
    player_puzzle = scenario.models.PlayerPuzzle.objects.filter(player__slug=player_slug, puzzle__slug=puzzle_slug).select_related('player').select_related('puzzle').first()
    if player_puzzle is None:
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    answer = post_data.get("answer")
    if answer is None:
        return JsonResponse({"ok": False})

    if player_puzzle.status != scenario.models.PlayerPuzzleStatus.UNLOCKED.value:
        return JsonResponse({"ok": False})

    if answer != player_puzzle.puzzle.answer:
        return JsonResponse({"ok": False})

    player_puzzle.status = scenario.models.PlayerPuzzleStatus.SOLVED.value
    player_puzzle.save()

    # Reward the bounty
    position_for_bounty = 0
    last_item_in_inventory = scenario.models.PlayerItem.objects.filter(player=player_puzzle.player).order_by('-position').first()
    if last_item_in_inventory:
        position_for_bounty = last_item_in_inventory.position + 1

    for bounty_item in player_puzzle.puzzle.bounty.all():
        scenario.models.PlayerItem.objects.create(player=player_puzzle.player, item=bounty_item, position=position_for_bounty)
        position_for_bounty += 1

    return JsonResponse({"ok": True})


@transaction.atomic
@csrf_exempt
def move_item(request, player_slug):
    player = scenario.models.Player.objects.filter(slug=player_slug).first()
    if player is None:
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    moved_item_id = post_data.get("id")
    new_index = post_data.get("new_index")
    if moved_item_id is None or new_index is None:
        return JsonResponse({"ok": False})

    player_items = list(scenario.models.PlayerItem.objects.filter(player=player).order_by('position').all())

    moved_item = [x for x in player_items if x.id == moved_item_id]
    if moved_item:
        player_items.remove(moved_item[0])
        player_items.insert(new_index, moved_item[0])

    for index, player_item in enumerate(player_items):
        scenario.models.PlayerItem.objects.filter(id=player_item.id).update(position=index)

    business_rules.notify_inventory(player)

    return JsonResponse({"ok": True})
