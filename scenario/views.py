import json
import logging
import datetime

import Levenshtein
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command

from scenario import business_rules
from scenario.business_rules import MessageLevel
from scenario.models import (
    Player,
    PlayerItem,
    Instance,
    InstanceStatus,
    PlayerPuzzle,
    Puzzle,
    PuzzleKind,
    PlayerPuzzleStatus,
    Trade,
    TradeStatus,
    Item,
)

logger = logging.getLogger()


def get_player_data(request, player_slug):
    logger.warning(f"gpd1 {player_slug}")
    player = Player.objects.filter(slug=player_slug).select_related("instance").first()
    if player is None:
        logger.warning(f"gpd2 {player_slug}")
        return JsonResponse({"ok": False})

    business_rules.notify_instance(player, player.instance)
    business_rules.notify_player(player)
    business_rules.notify_inventory(player)
    business_rules.notify_displayed_puzzle(player)

    logger.warning(f"gpd3 {player_slug}")
    return JsonResponse({"ok": True})


def reward_bounty(player_puzzle):
    bounty_items = player_puzzle.puzzle.bounty.all()

    PlayerItem.objects.filter(player=player_puzzle.player).update(
        position=F("position") + len(bounty_items)
    )

    for bounty_position, bounty_item in enumerate(player_puzzle.puzzle.bounty.all()):
        PlayerItem.objects.create(
            player=player_puzzle.player, item=bounty_item, position=bounty_position
        )


@transaction.atomic
def player_exist(request, player_slug):
    logger.warning(f"pe1 {player_slug}")
    player = Player.objects.filter(slug=player_slug).first()
    if player is None:
        logger.warning(f"pe2 {player_slug}")
        return JsonResponse({"exist": False, "name": ""})

    logger.warning(f"pe3 {player_slug}")
    return JsonResponse({"exist": True, "name": player.name})


@transaction.atomic
def display_puzzle(request, player_slug, puzzle_slug):
    logger.warning(f"dp1 {player_slug} {puzzle_slug}")
    instance = Instance.objects.filter(player__slug=player_slug).first()
    if instance is None:
        logger.warning(f"dp2 {player_slug} {puzzle_slug}")
        return JsonResponse({"ok": False})

    if instance.status != InstanceStatus.PLAYING.value:
        logger.warning(f"dp3 {player_slug} {puzzle_slug}")
        return JsonResponse({"ok": False})

    player_puzzle = PlayerPuzzle.objects.filter(
        player__slug=player_slug, puzzle__slug=puzzle_slug
    ).first()
    if player_puzzle is None:
        logger.warning(f"dp4 {player_slug} {puzzle_slug}")
        player = Player.objects.filter(slug=player_slug).first()
        puzzle = Puzzle.objects.filter(slug=puzzle_slug).first()

        if puzzle is None or player is None:
            logger.warning(f"dp5 {player_slug} {puzzle_slug}")
            return JsonResponse({"ok": False})

        if puzzle.kind == PuzzleKind.BOUNTY.value:
            status = PlayerPuzzleStatus.SOLVED.value
        else:
            status = PlayerPuzzleStatus.OBSERVED.value

        player_puzzle = PlayerPuzzle(
            player=player,
            puzzle=puzzle,
            status=status,
        )

        if puzzle.kind == PuzzleKind.BOUNTY.value:
            logger.warning(f"dp6 {player_slug} {puzzle_slug}")
            reward_bounty(player_puzzle)

    player_puzzle.is_displayed = True
    player_puzzle.save()  # Triggers notification

    logger.warning(f"dp7 {player_slug} {puzzle_slug}")
    return JsonResponse({"ok": True})


@transaction.atomic
@csrf_exempt
def unlock_puzzle(request, player_slug, puzzle_slug):
    logger.warning(f"up1 {player_slug} {puzzle_slug}")
    instance = Instance.objects.filter(player__slug=player_slug).first()

    if instance is None:
        logger.warning(f"up2 {player_slug} {puzzle_slug}")
        return JsonResponse({"ok": False})

    if instance.status != InstanceStatus.PLAYING.value:
        logger.warning(f"up3 {player_slug} {puzzle_slug}")
        return JsonResponse({"ok": False})

    player_puzzle = (
        PlayerPuzzle.objects.filter(player__slug=player_slug, puzzle__slug=puzzle_slug)
        .select_related("puzzle")
        .first()
    )
    if player_puzzle is None:
        logger.warning(f"up4 {player_slug} {puzzle_slug}")
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    key_as_player_items = post_data.get("key_as_player_items")
    if key_as_player_items is None:
        logger.warning(f"up5 {player_slug} {puzzle_slug} {key_as_player_items}")
        return JsonResponse({"ok": False})

    player_item_ids = [x["id"] for x in key_as_player_items]
    player_items = PlayerItem.objects.filter(id__in=player_item_ids).all()

    if len(player_items) != len(key_as_player_items):
        logger.warning(f"up6 {player_slug} {puzzle_slug} {key_as_player_items}")
        # Something is wrong or the player might want to glitch
        return JsonResponse({"ok": False})

    if player_puzzle.status != PlayerPuzzleStatus.OBSERVED.value:
        logger.warning(f"up7 {player_slug} {puzzle_slug} {key_as_player_items}")
        return JsonResponse({"ok": False})

    consumable_keys = list(player_puzzle.puzzle.consumable_keys.all())
    puzzle_keys = sorted(
        [x.id for x in list(player_puzzle.puzzle.keys.all()) + consumable_keys]
    )

    provided_keys = sorted([x["item_id"] for x in key_as_player_items])
    if provided_keys != puzzle_keys:
        logger.warning(f"up8 {player_slug} {puzzle_slug} {key_as_player_items}")
        return JsonResponse({"ok": False})

    if player_puzzle.puzzle.kind == PuzzleKind.KEY_BOUNTY.value:
        status = PlayerPuzzleStatus.SOLVED.value
    else:
        status = PlayerPuzzleStatus.UNLOCKED.value

    player_puzzle.status = status
    player_puzzle.save()

    if player_puzzle.puzzle.kind == PuzzleKind.KEY_BOUNTY.value:
        logger.warning(f"up9 {player_slug} {puzzle_slug} {key_as_player_items}")
        reward_bounty(player_puzzle)

    # Remove only consumable keys from inventory
    for player_item in player_items:
        if player_item.item in consumable_keys:
            player_item.delete()

    logger.warning(f"up10 {player_slug} {puzzle_slug} {key_as_player_items}")
    return JsonResponse({"ok": True})


@transaction.atomic
@csrf_exempt
def solve_puzzle(request, player_slug, puzzle_slug):
    logger.warning(f"sp1 {player_slug} {puzzle_slug}")
    instance = Instance.objects.filter(player__slug=player_slug).first()
    if instance is None:
        logger.warning(f"sp2 {player_slug} {puzzle_slug}")
        return JsonResponse({"ok": False})

    if instance.status != InstanceStatus.PLAYING.value:
        logger.warning(f"sp3 {player_slug} {puzzle_slug}")
        return JsonResponse({"ok": False})

    player_puzzle = (
        PlayerPuzzle.objects.filter(player__slug=player_slug, puzzle__slug=puzzle_slug)
        .select_related("player")
        .select_related("puzzle")
        .first()
    )
    if player_puzzle is None:
        logger.warning(f"sp4 {player_slug} {puzzle_slug}")
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    answer = post_data.get("answer")
    if answer is None:
        logger.warning(f"sp5 {player_slug} {puzzle_slug} {answer}")
        return JsonResponse({"ok": False})

    if player_puzzle.status != PlayerPuzzleStatus.UNLOCKED.value:
        logger.warning(f"sp6 {player_slug} {puzzle_slug} {answer}")
        return JsonResponse({"ok": False})

    distance_fr = Levenshtein.distance(answer.lower(), player_puzzle.puzzle.answer.lower())
    distance_en = Levenshtein.distance(answer.lower(), player_puzzle.puzzle.answer_en.lower())
    if min(distance_fr, distance_en) > 1:
        logger.warning(f"sp7 {player_slug} {puzzle_slug} {answer}")
        return JsonResponse({"ok": False})

    player_puzzle.status = PlayerPuzzleStatus.SOLVED.value
    player_puzzle.save()

    reward_bounty(player_puzzle)

    logger.warning(f"sp8 {player_slug} {puzzle_slug} {answer}")
    return JsonResponse({"ok": True})


@transaction.atomic
@csrf_exempt
def move_item(request, player_slug):
    logger.warning(f"mi1 {player_slug}")
    player = Player.objects.filter(slug=player_slug).first()
    if player is None:
        logger.warning(f"mi2 {player_slug}")
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    moved_item_id = post_data.get("id")
    new_index = post_data.get("new_index")
    if moved_item_id is None or new_index is None:
        logger.warning(f"mi3 {player_slug} {moved_item_id} {new_index}")
        return JsonResponse({"ok": False})

    player_items = list(
        PlayerItem.objects.filter(player=player).order_by("position").all()
    )

    moved_item = [x for x in player_items if x.id == moved_item_id]
    if moved_item:
        player_items.remove(moved_item[0])
        player_items.insert(new_index, moved_item[0])

    for index, player_item in enumerate(player_items):
        PlayerItem.objects.filter(id=player_item.id).update(position=index)

    business_rules.notify_inventory(player)

    logger.warning(f"mi4 {player_slug} {moved_item_id} {new_index}")
    return JsonResponse({"ok": True})


@transaction.atomic
@csrf_exempt
def trade_start(request):
    logger.warning("ts0")
    post_data = json.loads(request.body)
    peer_slug = post_data.get("peer_slug")
    my_slug = post_data.get("my_slug")
    logger.warning(f"ts1 {my_slug} {peer_slug}")

    peer = Player.objects.filter(slug=peer_slug).select_related("instance").first()
    me = Player.objects.filter(slug=my_slug).select_related("instance").first()

    if peer is None or me is None:
        logger.warning(f"ts2 {my_slug} {peer_slug}")
        return JsonResponse({"ok": False})

    if peer == me:
        logger.warning(f"ts3 {my_slug} {peer_slug}")
        return JsonResponse({"ok": False})

    if peer.instance != me.instance:
        logger.warning(f"ts4 {my_slug} {peer_slug}")
        return JsonResponse({"ok": False})

    if me.instance.status != InstanceStatus.PLAYING.value:
        logger.warning(f"ts5 {my_slug} {peer_slug}")
        return JsonResponse({"ok": False})

    new_trade = Trade(
        peer_a=peer,
        peer_b=me,
        status_a=TradeStatus.TRADING.value,
        status_b=TradeStatus.TRADING.value,
    )
    new_trade.save()

    logger.warning(f"ts6 {my_slug} {peer_slug}")
    return JsonResponse({"ok": True})


@transaction.atomic
@csrf_exempt
def trade_accept(request, trade_id):
    logger.warning(f"ta0 {trade_id}")
    trade = Trade.objects.filter(id=trade_id).first()

    if trade is None:
        logger.warning(f"ta1 {trade_id}")
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    my_slug = post_data.get("my_slug")
    logger.warning(f"ta2 {trade_id} {my_slug}")

    me = Player.objects.filter(slug=my_slug).first()

    if me is None:
        logger.warning(f"ta2 {trade_id} {my_slug}")
        return JsonResponse({"ok": False})

    if trade.peer_a == me:
        logger.warning(f"ta3 {trade_id} {my_slug}")
        trade.status_a = TradeStatus.ACCEPTED.value
        trade.save()
        if trade.status_b == TradeStatus.ACCEPTED.value:
            trade.delete()
            for player in [trade.peer_a, trade.peer_b]:
                business_rules.notify_message(
                    player, "trade_accepted", level=MessageLevel.SUCCESS
                )
        return JsonResponse({"ok": True})

    if trade.peer_b == me:
        logger.warning(f"ta4 {trade_id} {my_slug}")
        trade.status_b = TradeStatus.ACCEPTED.value
        trade.save()
        if trade.status_a == TradeStatus.ACCEPTED.value:
            trade.delete()
            for player in [trade.peer_a, trade.peer_b]:
                business_rules.notify_message(
                    player, "trade_accepted", level=MessageLevel.SUCCESS
                )
        return JsonResponse({"ok": True})

    logger.warning(f"ta5 {trade_id} {my_slug}")
    return JsonResponse({"ok": False})


@transaction.atomic
@csrf_exempt
def trade_withdraw(request, trade_id):
    logger.warning(f"tw1 {trade_id}")
    trade = Trade.objects.filter(id=trade_id).first()

    if trade is None:
        logger.warning(f"tw2 {trade_id}")
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    my_slug = post_data.get("my_slug")
    logger.warning(f"tw3 {trade_id} {my_slug}")

    me = Player.objects.filter(slug=my_slug).first()

    if me is None:
        logger.warning(f"tw4 {trade_id} {my_slug}")
        return JsonResponse({"ok": False})

    if trade.peer_a == me:
        logger.warning(f"tw5 {trade_id} {my_slug}")
        trade.status_a = TradeStatus.TRADING.value
        trade.save()
        return JsonResponse({"ok": True})

    if trade.peer_b == me:
        logger.warning(f"tw6 {trade_id} {my_slug}")
        trade.status_b = TradeStatus.TRADING.value
        trade.save()
        return JsonResponse({"ok": True})

    logger.warning(f"tw7 {trade_id} {my_slug}")
    return JsonResponse({"ok": False})


@transaction.atomic
@csrf_exempt
def flush_and_load_data(request):
    call_command('flush', '--no-input')
    call_command('loaddata', 'fixtures.json')
    with open(f"before_flush_{datetime.datetime.now().isoformat(timespec='seconds')}.json", "w+") as fh:
        call_command('dumpdata', "--indent", "2", stdout=fh)
    return JsonResponse({"ok": True})


@transaction.atomic
@csrf_exempt
def trade_update(request, trade_id):
    logger.warning(f"tu1 {trade_id}")
    trade = Trade.objects.filter(id=trade_id).first()

    if trade is None:
        logger.warning(f"tu2 {trade_id}")
        return JsonResponse({"ok": False})

    post_data = json.loads(request.body)
    my_slug = post_data.get("my_slug")
    my_item_ids = post_data.get("my_item_ids")
    logger.warning(f"tu3 {trade_id} {my_slug} {my_item_ids}")

    me = Player.objects.filter(slug=my_slug).first()

    if me is None:
        logger.warning(f"tu4 {trade_id} {my_slug} {my_item_ids}")
        return JsonResponse({"ok": False})

    if trade.peer_a == me:
        logger.warning(f"tu5 {trade_id} {my_slug} {my_item_ids}")
        trade.player_items_a.clear()
        trade.player_items_a.add(*my_item_ids)
        trade.save()
        return JsonResponse({"ok": True})

    if trade.peer_b == me:
        logger.warning(f"tu6 {trade_id} {my_slug} {my_item_ids}")
        trade.player_items_b.clear()
        trade.player_items_b.add(*my_item_ids)
        trade.save()
        return JsonResponse({"ok": True})

    logger.warning(f"tu7 {trade_id} {my_slug} {my_item_ids}")
    return JsonResponse({"ok": False})


@transaction.atomic
@csrf_exempt
def trade_cancel(request, trade_id):
    logger.warning(f"tc1 {trade_id}")
    trade = Trade.objects.filter(id=trade_id).first()

    if trade is None:
        logger.warning(f"tc2 {trade_id}")
        return JsonResponse({"ok": False})

    trade.delete()
    business_rules.notify_no_trade(trade.peer_a, trade.peer_b)

    for player in [trade.peer_a, trade.peer_b]:
        business_rules.notify_message(player, "trade_canceled")

    logger.warning(f"tc3 {trade_id}")
    return JsonResponse({"ok": True})


def serialize_player(p):
    return {
        "name": p.name,
        "slug": p.slug,
        "team": p.team,
    }


def get_all_players(request):
    return JsonResponse(
        {
            "players": [
                serialize_player(x)
                for x in Player.objects.all().order_by("team", "name")
            ]
        }
    )


def serialize_puzzle(p):
    return {
        "name": p.name,
        "slug": p.slug,
    }


def get_all_puzzles(request):
    return JsonResponse(
        {
            "puzzles": [
                serialize_puzzle(x) for x in Puzzle.objects.all().order_by("slug")
            ]
        }
    )


def serialize_puzzle_for_stats(p):
    return {
        "id": p.id,
        "slug": p.slug,
        "name": p.name,
        "picture": p.picture.url,
    }


def serialize_player_for_stats(p):
    return {
        "id": p.id,
        "slug": p.slug,
        "name": p.name,
        "team": p.team,
        "nth_place": p.nth_place,
        "avatar": p.avatar.url,
    }


def serialize_item_for_stats(i):
    return {
        "id": i.id,
        "name": i.name,
        "description": i.description,
        "image": i.image.url,
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


@csrf_exempt
def get_all_stats(request):
    post_data = json.loads(request.body)
    name = post_data.get("name") or ""
    teams = post_data.get("teams")

    logger.warning(f"name={name} teams={teams}")

    puzzles = [serialize_puzzle_for_stats(x) for x in Puzzle.objects.all()]
    items = [serialize_item_for_stats(x) for x in Item.objects.all()]

    player_qs = Player.objects.all()
    player_puzzle_qs = PlayerPuzzle.objects.all()
    player_item_qs = PlayerItem.objects.all()

    if name:
        player_qs = player_qs.filter(name__icontains=name)

    if teams:
        player_qs = player_qs.filter(team__in=teams)

    players = [serialize_player_for_stats(x) for x in player_qs]

    player_puzzle_qs = player_puzzle_qs.filter(player__in=[x["id"] for x in players])
    player_item_qs = player_item_qs.filter(player__in=[x["id"] for x in players])

    player_puzzles = [serialize_player_puzzle_for_stats(x) for x in player_puzzle_qs]
    player_items = [serialize_player_item_for_stats(x) for x in player_item_qs]

    return JsonResponse(
        {
            "puzzles": puzzles,
            "player_puzzles": player_puzzles,
            "player_items": player_items,
            "items": items,
            "players": players,
        }
    )
