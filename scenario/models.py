import os
from enum import Enum

from django.dispatch import receiver
from django.db import models
from django import forms

from scenario.web_socket import web_socket_notifier as wsn, MessageType
from scenario import business_rules
import logging

logger = logging.getLogger()


class InstanceStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    VOTING = "VOTING"
    FINISHED = "FINISHED"


class Instance(models.Model):
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=64)
    status = models.CharField(max_length=64, choices=[(i.value, i.value) for i in InstanceStatus])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Instance {self.name}"


class InstanceForm(forms.ModelForm):
    class Meta:
        model = Instance
        fields = '__all__'


@receiver(models.signals.post_save, sender=Instance)
def notify_update_instance(sender, instance, **kwargs):
    players = Player.objects.filter(instance=instance)

    for p in players:
        business_rules.notify_instance(p, instance)

    if instance.status != InstanceStatus.PLAYING.value:
        for trade in Trade.objects.all():
            trade.delete()
            business_rules.notify_no_trade(trade.peer_a, trade.peer_b)


class Item(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    image = models.ImageField(upload_to="item")

    def __str__(self):
        return f"Item {self.name}"


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


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'


@receiver(models.signals.post_save, sender=Item)
def notify_update_item(sender, instance, **kwargs):
    player_items = PlayerItem.objects.filter(item=instance).all()
    players = Player.objects.filter(id__in=[x.player_id for x in player_items])

    for p in players:
        business_rules.notify_inventory(p)


class PuzzleKind(Enum):
    KEY_RIDDLE_BOUNTY = "KEY_RIDDLE_BOUNTY"
    BOUNTY = "BOUNTY"


class Puzzle(models.Model):
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=64)
    description = models.TextField()
    picture = models.ImageField(upload_to="puzzle")
    kind = models.CharField(max_length=64, choices=[(k.value, k.value) for k in PuzzleKind])
    keys = models.ManyToManyField(Item, related_name="keys_puzzles", blank=True)
    answer = models.CharField(max_length=64)
    bounty = models.ManyToManyField(Item, related_name="bounty_puzzles", blank=True)
    is_final = models.BooleanField(default=False)

    def __str__(self):
        return f"Puzzle {self.name}"


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


class PuzzleForm(forms.ModelForm):
    class Meta:
        model = Puzzle
        fields = '__all__'


@receiver(models.signals.post_save, sender=Puzzle)
def notify_update_puzzle(sender, instance, **kwargs):
    player_puzzles = PlayerPuzzle.objects.filter(puzzle=instance, is_displayed=True)
    players = Player.objects.filter(id__in=[x.player_id for x in player_puzzles])

    for p in players:
        business_rules.notify_displayed_puzzle(p)


class PlayerRole(Enum):
    NPC = "NPC"
    LEADER = "LEADER"
    DETECTIVE = "DETECTIVE"
    NEGOTIATOR = "NEGOTIATOR"
    ARTIST = "ARTIST"


class PlayerTeam(Enum):
    SHERLOCK = "SHERLOCK"
    MORIARTY = "MORIARTY"
    NEUTRAL = "NEUTRAL"


class Player(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=64)
    avatar = models.ImageField(upload_to="character")
    role = models.CharField(max_length=64, choices=[(r.value, r.value) for r in PlayerRole])
    team = models.CharField(max_length=64, choices=[(t.value, t.value) for t in PlayerTeam])
    money = models.IntegerField()
    reputation = models.IntegerField(verbose_name="Reputation (ARTIST)")

    def __str__(self):
        return f"Player {self.name}"


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


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = '__all__'


@receiver(models.signals.post_save, sender=Player)
def notify_update_player(sender, instance, **kwargs):
    business_rules.notify_player(instance)


class PlayerItem(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    position = models.IntegerField()

    def __str__(self):
        return f"PlayerItem {self.player} - {self.item.name}"


class PlayerItemForm(forms.ModelForm):
    class Meta:
        model = PlayerItem
        fields = '__all__'


class PlayerPuzzleStatus(Enum):
    OBSERVED = "OBSERVED"
    UNLOCKED = "UNLOCKED"
    SOLVED = "SOLVED"


class PlayerPuzzle(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    status = models.CharField(max_length=64, choices=[(status.value, status.value) for status in PlayerPuzzleStatus])
    is_displayed = models.BooleanField(default=False)

    def __str__(self):
        return f"PlayerPuzzle {self.player} - {self.puzzle.name}"


class PlayerPuzzleForm(forms.ModelForm):
    class Meta:
        model = PlayerPuzzle
        fields = '__all__'


@receiver(models.signals.post_save, sender=Player)
def notify_update_player(sender, instance, **kwargs):
    business_rules.notify_player(instance)


@receiver(models.signals.post_save, sender=PlayerItem)
def notify_update_inventory(sender, instance, **kwargs):
    business_rules.notify_inventory(instance.player)


@receiver(models.signals.pre_save, sender=PlayerPuzzle)
def toggle_player_puzzle_not_displayed(sender, instance, **kwargs):
    if not instance.is_displayed:
        return

    PlayerPuzzle.objects.filter(player=instance.player).all().update(is_displayed=False)


@receiver(models.signals.post_save, sender=PlayerPuzzle)
def notify_update_player_puzzle(sender, instance, **kwargs):
    if not instance.is_displayed:
        return

    business_rules.notify_displayed_puzzle(instance.player)


class TradeStatus(Enum):
    TRADING = "TRADING"
    ACCEPTED = "ACCEPTED"


class Trade(models.Model):
    peer_a = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="peer_a_trade")
    peer_b = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="peer_b_trade")
    status_a = models.CharField(max_length=64, choices=[(status.value, status.value) for status in TradeStatus])
    status_b = models.CharField(max_length=64, choices=[(status.value, status.value) for status in TradeStatus])
    player_items_a = models.ManyToManyField(PlayerItem, related_name="peer_a_player_item", blank=True)
    money_a = models.IntegerField(default=0)
    player_items_b = models.ManyToManyField(PlayerItem, related_name="peer_b_player_item", blank=True)
    money_b = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = '__all__'


@receiver(models.signals.pre_save, sender=Trade)
def on_trade_pre_save(sender, instance, **kwargs):
    instance.money_a = max(0, min(instance.money_a, instance.peer_a.money))
    instance.money_b = max(0, min(instance.money_b, instance.peer_b.money))

    if instance.pk:
        return

    # Just making sure
    already_existing_trades = Trade.objects.filter(peer_a__in=[instance.peer_a, instance.peer_b]) | Trade.objects.filter(peer_b__in=[instance.peer_a, instance.peer_b])

    for trade in already_existing_trades:
        trade.delete()


def trade_peer_items(player_items, new_owner):
    position_for_new_item = 0
    last_item_in_inventory = PlayerItem.objects.filter(player=new_owner).order_by('-position').first()
    if last_item_in_inventory:
        position_for_new_item = last_item_in_inventory.position + 1

    for player_item in player_items:
        player_item.player = new_owner
        player_item.position = position_for_new_item
        player_item.save()
        position_for_new_item += 1


@receiver(models.signals.post_save, sender=Trade)
def on_trade_post_save(sender, instance, **kwargs):
    if instance.status_a == instance.status_b == TradeStatus.ACCEPTED.value:
        instance.peer_a.money += instance.money_b - instance.money_a
        instance.peer_a.save()

        instance.peer_b.money += instance.money_a - instance.money_b
        instance.peer_b.save()

        trade_peer_items(instance.player_items_a.all(), instance.peer_b)
        trade_peer_items(instance.player_items_b.all(), instance.peer_a)

        business_rules.notify_inventory(instance.peer_a)
        business_rules.notify_inventory(instance.peer_b)
        business_rules.notify_no_trade(instance.peer_a, instance.peer_b)

    else:
        business_rules.notify_trade(instance)
