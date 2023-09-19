import json
from django.shortcuts import render
import scenario
from django.http import JsonResponse
from django.db import transaction
from scenario.web_socket import web_socket_notifier as wsn, MessageType
import logging
from scenario import business_rules
from django.views.decorators.csrf import csrf_exempt
import Levenshtein

logger = logging.getLogger()


def get_player_data(request, player_slug):
    player = scenario.models.Player.objects.filter(slug=player_slug).select_related('instance').first()
    if player is None:
        return JsonResponse({"ok": False})

    business_rules.notify_instance(player, player.instance)
    business_rules.notify_player(player)
    business_rules.notify_inventory(player)
    business_rules.notify_displayed_puzzle(player)

    return JsonResponse({"ok": True})


def reward_bounty(player_puzzle):
    position_for_bounty = 0
    last_item_in_inventory = scenario.models.PlayerItem.objects.filter(player=player_puzzle.player).order_by('-position').first()
    if last_item_in_inventory:
        position_for_bounty = last_item_in_inventory.position + 1

    for bounty_item in player_puzzle.puzzle.bounty.all():
        scenario.models.PlayerItem.objects.create(player=player_puzzle.player, item=bounty_item, position=position_for_bounty)
        position_for_bounty += 1


@transaction.atomic
def player_exist(request, player_slug):
    player = scenario.models.Player.objects.filter(slug=player_slug).first()
    if player is None:
        return JsonResponse({"exist": False, "name": ""})

    return JsonResponse({"exist": True, "name": player.name})


@transaction.atomic
def display_puzzle(request, player_slug, puzzle_slug):
    instance = scenario.models.Instance.objects.filter(player__slug=player_slug).first()
    if instance is None:
        return JsonResponse({"ok": False})

    if instance.status != scenario.models.InstanceStatus.PLAYING.value:
        return JsonResponse({"ok": False})

    player_puzzle = scenario.models.PlayerPuzzle.objects.filter(player__slug=player_slug, puzzle__slug=puzzle_slug).first()
    if player_puzzle is None:
        player = scenario.models.Player.objects.filter(slug=player_slug).first()
        puzzle = scenario.models.Puzzle.objects.filter(slug=puzzle_slug).first()

        if puzzle is None or player is None:
            return JsonResponse({"ok": False})

        if puzzle.kind == scenario.models.PuzzleKind.BOUNTY.value:
            status = scenario.models.PlayerPuzzleStatus.SOLVED.value
        else:
            status = scenario.models.PlayerPuzzleStatus.OBSERVED.value

        player_puzzle = scenario.models.PlayerPuzzle(
            player=player,
            puzzle=puzzle,
            status=status,
        )

        if puzzle.kind == scenario.models.PuzzleKind.BOUNTY.value:
            reward_bounty(player_puzzle)

    player_puzzle.is_displayed = True
    player_puzzle.save()  # Triggers notification

    return JsonResponse({"ok": True})


@transaction.atomic
@csrf_exempt
def unlock_puzzle(request, player_slug, puzzle_slug):
    instance = scenario.models.Instance.objects.filter(player__slug=player_slug).first()
    if instance is None:
        return JsonResponse({"ok": False})

    if instance.status != scenario.models.InstanceStatus.PLAYING.value:
        return JsonResponse({"ok": False})

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
    instance = scenario.models.Instance.objects.filter(player__slug=player_slug).first()
    if instance is None:
        return JsonResponse({"ok": False})

    if instance.status != scenario.models.InstanceStatus.PLAYING.value:
        return JsonResponse({"ok": False})

    player_puzzle = scenario.models.PlayerPuzzle.objects.filter(player__slug=player_slug, puzzle__slug=puzzle_slug).select_related('player').select_related('puzzle').first()
    if player_puzzle is None:
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    answer = post_data.get("answer")
    if answer is None:
        return JsonResponse({"ok": False})

    if player_puzzle.status != scenario.models.PlayerPuzzleStatus.UNLOCKED.value:
        return JsonResponse({"ok": False})

    if Levenshtein.distance(answer.lower(), player_puzzle.puzzle.answer.lower()) > 1:
        return JsonResponse({"ok": False})

    player_puzzle.status = scenario.models.PlayerPuzzleStatus.SOLVED.value
    player_puzzle.save()

    reward_bounty(player_puzzle)

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


@transaction.atomic
@csrf_exempt
def trade_start(request):
    post_data = json.loads(request.body)
    peer_slug = post_data.get("peer_slug")
    my_slug = post_data.get("my_slug")

    peer = scenario.models.Player.objects.filter(slug=peer_slug).select_related('instance').first()
    me = scenario.models.Player.objects.filter(slug=my_slug).select_related('instance').first()

    if peer is None or me is None:
        return JsonResponse({"ok": False})

    if peer == me:
        return JsonResponse({"ok": False})

    if peer.instance != me.instance:
        return JsonResponse({"ok": False})

    if me.instance.status != scenario.models.InstanceStatus.PLAYING.value:
        return JsonResponse({"ok": False})

    if not (
            peer.role in [scenario.models.PlayerRole.NPC.value, scenario.models.PlayerRole.NEGOTIATOR.value] or
            me.role in [scenario.models.PlayerRole.NPC.value, scenario.models.PlayerRole.NEGOTIATOR.value]
    ):
        if (
            (peer.team == scenario.models.PlayerTeam.STERLING.value and me.team == scenario.models.PlayerTeam.BLACKTHORN.value) or
            (peer.team == scenario.models.PlayerTeam.BLACKTHORN.value and me.team == scenario.models.PlayerTeam.STERLING.value)
        ):
            business_rules.notify_message(peer, "Vous ne pouvez échanger qu'avec des marchands ou des membres de votre équipe")
            business_rules.notify_message(me, "Vous ne pouvez échanger qu'avec des marchands ou des membres de votre équipe")
            business_rules.notify_no_trade(peer, me)
            return JsonResponse({"ok": False})

    new_trade = scenario.models.Trade(
        peer_a=peer,
        peer_b=me,
        status_a=scenario.models.TradeStatus.TRADING.value,
        status_b=scenario.models.TradeStatus.TRADING.value,
    )
    new_trade.save()

    return JsonResponse({"ok": True})


@transaction.atomic
@csrf_exempt
def trade_accept(request, trade_id):
    trade = scenario.models.Trade.objects.filter(id=trade_id).first()

    if trade is None:
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    my_slug = post_data.get("my_slug")

    me = scenario.models.Player.objects.filter(slug=my_slug).first()

    if me is None:
        return JsonResponse({"ok": False})

    if trade.peer_a == me:
        trade.status_a = scenario.models.TradeStatus.ACCEPTED.value
        trade.save()
        if trade.status_b == scenario.models.TradeStatus.ACCEPTED.value:
            trade.delete()
        return JsonResponse({"ok": True})

    if trade.peer_b == me:
        trade.status_b = scenario.models.TradeStatus.ACCEPTED.value
        trade.save()
        if trade.status_a == scenario.models.TradeStatus.ACCEPTED.value:
            trade.delete()
        return JsonResponse({"ok": True})

    return JsonResponse({"ok": False})


@transaction.atomic
@csrf_exempt
def trade_withdraw(request, trade_id):
    trade = scenario.models.Trade.objects.filter(id=trade_id).first()

    if trade is None:
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    my_slug = post_data.get("my_slug")

    me = scenario.models.Player.objects.filter(slug=my_slug).first()

    if me is None:
        return JsonResponse({"ok": False})

    if trade.peer_a == me:
        trade.status_a = scenario.models.TradeStatus.TRADING.value
        trade.save()
        return JsonResponse({"ok": True})

    if trade.peer_b == me:
        trade.status_b = scenario.models.TradeStatus.TRADING.value
        trade.save()
        return JsonResponse({"ok": True})

    return JsonResponse({"ok": False})


@transaction.atomic
@csrf_exempt
def trade_update(request, trade_id):
    trade = scenario.models.Trade.objects.filter(id=trade_id).first()

    if trade is None:
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    my_slug = post_data.get("my_slug")
    my_item_ids = post_data.get("my_item_ids")
    my_money = int(post_data.get("my_money"))

    me = scenario.models.Player.objects.filter(slug=my_slug).first()

    if me is None:
        return JsonResponse({"ok": False})

    if trade.peer_a == me:
        trade.money_a = my_money
        trade.player_items_a.clear()
        trade.player_items_a.add(*my_item_ids)
        trade.save()
        return JsonResponse({"ok": True})

    if trade.peer_b == me:
        trade.money_b = my_money
        trade.player_items_b.clear()
        trade.player_items_b.add(*my_item_ids)
        trade.save()
        return JsonResponse({"ok": True})

    return JsonResponse({"ok": False})


@transaction.atomic
@csrf_exempt
def give_reputation(request, player_slug):
    player = scenario.models.Player.objects.filter(slug=player_slug).first()
    if player is None:
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    amount = post_data.get("amount")

    player.reputation += amount
    player.save()

    return JsonResponse({"ok": True})


@transaction.atomic
@csrf_exempt
def trade_cancel(request, trade_id):
    trade = scenario.models.Trade.objects.filter(id=trade_id).first()

    if trade is None:
        return JsonResponse({"ok": False})

    trade.delete()
    business_rules.notify_no_trade(trade.peer_a, trade.peer_b)

    return JsonResponse({"ok": True})


def serialize_player(p):
    return {
        "name": p.name,
        "slug": p.slug,
        "role": p.role,
        "team": p.team,
    }


def get_all_players(request):
    return JsonResponse({"players": [serialize_player(x) for x in scenario.models.Player.objects.all().order_by('team', 'role', 'name')]})


def serialize_puzzle(p):
    return {
        "slug": p.slug,
    }


def get_all_puzzles(request):
    return JsonResponse({"puzzles": [serialize_puzzle(x) for x in scenario.models.Puzzle.objects.all().order_by('slug')]})


def serialize_puzzle_for_stats(p):
    return {
        "id": p.id,
        "slug": p.slug,
        "name": p.name,
        "picture": p.picture.url,
        "is_final": p.is_final,
    }


def serialize_player_for_stats(p):
    return {
        "id": p.id,
        "name": p.name,
        "role": p.role,
        "team": p.team,
        "money": p.money,
        "reputation": p.reputation,
    }


def serialize_item_for_stats(i):
    return {
        "id": i.id,
        "name": i.name,
    }


def serialize_player_puzzle_for_stats(pp):
    return {
        "player_id": pp.player_id,
        "puzzle_id": pp.puzzle_id,
        "status": pp.status,
    }


def serialize_player_item_for_stats(pi):
    return {
        "player_id": pi.player_id,
        "item_id": pi.item_id,
    }


def get_all_stats(request):
    puzzles = [serialize_puzzle_for_stats(x) for x in scenario.models.Puzzle.objects.all()]
    items = [serialize_item_for_stats(x) for x in scenario.models.Item.objects.all()]

    players = [serialize_player_for_stats(x) for x in scenario.models.Player.objects.all()]
    player_puzzles = [serialize_player_puzzle_for_stats(x) for x in scenario.models.PlayerPuzzle.objects.all()]
    player_items = [serialize_player_item_for_stats(x) for x in scenario.models.PlayerItem.objects.all()]

    return JsonResponse({"puzzles": puzzles, "player_puzzles": player_puzzles, "player_items": player_items, "items": items, "players": players})
