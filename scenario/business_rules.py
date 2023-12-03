import enum
import os
from scenario.models import (
    PlayerPuzzleStatus,
    PlayerItem,
    PlayerPuzzle,
    Instance,
    InstanceStatus,
    Player,
    Trade,
    Item,
    Puzzle,
    TradeStatus,
    PlayerTeam,
)
from scenario.web_socket import web_socket_notifier as wsn, MessageType
from django.dispatch import receiver
from django.db import models


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
        "team": player.team,
    }

    channel = player.slug
    wsn.notify(channel, {"type": MessageType.PUT_PLAYER, "data": data})


@receiver(models.signals.post_save, sender=Instance)
def notify_update_instance(sender, instance, **kwargs):
    players = Player.objects.filter(instance=instance)

    for p in players:
        notify_instance(p, instance)

    if instance.status != InstanceStatus.PLAYING.value:
        for trade in Trade.objects.all():
            trade.delete()
            notify_no_trade(trade.peer_a, trade.peer_b)


@receiver(models.signals.post_delete, sender=Item)
def auto_delete_image_on_item_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=Item)
def auto_delete_image_on_item_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Item.objects.get(pk=instance.pk).image
    except Item.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


@receiver(models.signals.post_save, sender=Item)
def notify_update_item(sender, instance, **kwargs):
    player_items = PlayerItem.objects.filter(item=instance).all()
    players = Player.objects.filter(id__in=[x.player_id for x in player_items])

    for p in players:
        notify_inventory(p)


@receiver(models.signals.post_delete, sender=Puzzle)
def auto_delete_picture_on_puzzle_delete(sender, instance, **kwargs):
    if instance.picture:
        if os.path.isfile(instance.picture.path):
            os.remove(instance.picture.path)


@receiver(models.signals.pre_save, sender=Puzzle)
def auto_delete_picture_on_puzzle_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Puzzle.objects.get(pk=instance.pk).picture
    except Puzzle.DoesNotExist:
        return False

    new_file = instance.picture
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


@receiver(models.signals.post_save, sender=Puzzle)
def notify_update_puzzle(sender, instance, **kwargs):
    player_puzzles = PlayerPuzzle.objects.filter(puzzle=instance, is_displayed=True)
    players = Player.objects.filter(id__in=[x.player_id for x in player_puzzles])

    for p in players:
        notify_displayed_puzzle(p)


@receiver(models.signals.post_delete, sender=Player)
def auto_delete_avatar_on_player_delete(sender, instance, **kwargs):
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)


@receiver(models.signals.pre_save, sender=Player)
def auto_delete_avatar_on_player_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Player.objects.get(pk=instance.pk).avatar
    except Player.DoesNotExist:
        return False

    new_file = instance.avatar
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


@receiver(models.signals.post_save, sender=Player)
def notify_update_player(sender, instance, **kwargs):
    notify_player(instance)


@receiver(models.signals.post_save, sender=PlayerItem)
def notify_update_inventory(sender, instance, **kwargs):
    notify_inventory(instance.player)


@receiver(models.signals.pre_save, sender=PlayerPuzzle)
def toggle_player_puzzle_not_displayed(sender, instance, **kwargs):
    if not instance.is_displayed:
        return

    PlayerPuzzle.objects.filter(player=instance.player).all().update(is_displayed=False)


@receiver(models.signals.post_save, sender=PlayerPuzzle)
def notify_update_player_puzzle(sender, instance, **kwargs):
    if not instance.is_displayed:
        return

    notify_displayed_puzzle(instance.player)


@receiver(models.signals.pre_save, sender=Trade)
def on_trade_pre_save(sender, instance, **kwargs):
    if instance.pk:
        return

    # Just making sure
    already_existing_trades = Trade.objects.filter(
        peer_a__in=[instance.peer_a, instance.peer_b]
    ) | Trade.objects.filter(peer_b__in=[instance.peer_a, instance.peer_b])

    for trade in already_existing_trades:
        trade.delete()


def trade_peer_items(player_items, new_owner, duplicate=False):
    position_for_new_item = 0
    last_item_in_inventory = (
        PlayerItem.objects.filter(player=new_owner).order_by("-position").first()
    )
    if last_item_in_inventory:
        position_for_new_item = last_item_in_inventory.position + 1

    if duplicate:
        for player_item in player_items:
            PlayerItem.objects.create(
                player=new_owner, item=player_item.item, position=position_for_new_item
            )
            position_for_new_item += 1
    else:
        for player_item in player_items:
            player_item.player = new_owner
            player_item.position = position_for_new_item
            player_item.save()
            position_for_new_item += 1


@receiver(models.signals.post_save, sender=Trade)
def on_trade_post_save(sender, instance, **kwargs):
    if instance.status_a == instance.status_b == TradeStatus.ACCEPTED.value:
        trade_peer_items(
            instance.player_items_a.all(),
            instance.peer_b,
            duplicate=instance.peer_a.team == PlayerTeam.NEUTRAL.value,
        )
        trade_peer_items(
            instance.player_items_b.all(),
            instance.peer_a,
            duplicate=instance.peer_b.team == PlayerTeam.NEUTRAL.value,
        )

        notify_inventory(instance.peer_a)
        notify_inventory(instance.peer_b)
        notify_no_trade(instance.peer_a, instance.peer_b)

    else:
        notify_trade(instance)


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
    player_items = (
        PlayerItem.objects.filter(player=player)
        .select_related("item")
        .order_by("position")
        .all()
    )
    inventory = [serialize_player_item(x) for x in player_items]

    channel = player.slug
    wsn.notify(channel, {"type": MessageType.PUT_INVENTORY, "data": inventory})


def notify_displayed_puzzle(player):
    displayed_puzzle = (
        PlayerPuzzle.objects.filter(player=player, is_displayed=True)
        .select_related("puzzle")
        .first()
    )
    if displayed_puzzle is None:
        return

    data = {
        "puzzle_slug": displayed_puzzle.puzzle.slug,
        "puzzle_id": displayed_puzzle.puzzle_id,
        "status": displayed_puzzle.status,
        "kind": displayed_puzzle.puzzle.kind,
        "name": displayed_puzzle.puzzle.name,
        "n_keys": displayed_puzzle.puzzle.keys.count(),
        "picture": displayed_puzzle.puzzle.picture.url,
        "riddle": displayed_puzzle.puzzle.riddle,
    }

    if displayed_puzzle.status in [
        PlayerPuzzleStatus.UNLOCKED.value,
        PlayerPuzzleStatus.SOLVED.value,
    ]:
        keys = displayed_puzzle.puzzle.keys.order_by("id").all()
        data["keys"] = [serialize_item(x) for x in keys]
    if displayed_puzzle.status == PlayerPuzzleStatus.SOLVED.value:
        bounty = displayed_puzzle.puzzle.bounty.order_by("id").all()
        data["bounty"] = [serialize_item(x) for x in bounty]

    channel = player.slug
    wsn.notify(channel, {"type": MessageType.PUT_DISPLAYED_PUZZLE, "data": data})


def notify_trade(trade):
    serialized_player_items_a = [
        serialize_player_item(x) for x in trade.player_items_a.all()
    ]
    serialized_player_items_b = [
        serialize_player_item(x) for x in trade.player_items_b.all()
    ]

    peer_a_data = {
        "trade_id": trade.id,
        "my_status": trade.status_a,
        "my_items": serialized_player_items_a,
        "peer_name": trade.peer_b.name,
        "peer_status": trade.status_b,
        "peer_items": serialized_player_items_b,
        "peer_slug": trade.peer_b.slug,
    }

    peer_b_data = {
        "trade_id": trade.id,
        "my_status": trade.status_b,
        "my_items": serialized_player_items_b,
        "peer_name": trade.peer_a.name,
        "peer_status": trade.status_a,
        "peer_items": serialized_player_items_a,
        "peer_slug": trade.peer_a.slug,
    }

    peer_a_channel = trade.peer_a.slug
    wsn.notify(peer_a_channel, {"type": MessageType.PUT_TRADE, "data": peer_a_data})

    peer_b_channel = trade.peer_b.slug
    wsn.notify(peer_b_channel, {"type": MessageType.PUT_TRADE, "data": peer_b_data})


def notify_no_trade(peer_a, peer_b):
    peer_a_data = {
        "trade_id": None,
        "my_status": None,
        "my_items": [],
        "peer_name": "",
        "peer_status": None,
        "peer_items": [],
        "peer_slug": "",
    }

    peer_b_data = {
        "trade_id": None,
        "my_status": None,
        "my_items": [],
        "peer_name": "",
        "peer_status": None,
        "peer_items": [],
        "peer_slug": "",
    }

    peer_a_channel = peer_a.slug
    wsn.notify(peer_a_channel, {"type": MessageType.PUT_TRADE, "data": peer_a_data})

    peer_b_channel = peer_b.slug
    wsn.notify(peer_b_channel, {"type": MessageType.PUT_TRADE, "data": peer_b_data})
