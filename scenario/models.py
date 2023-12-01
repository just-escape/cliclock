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


class PlayerTeam(Enum):
    SHERLOCK = "SHERLOCK"
    MORIARTY = "MORIARTY"
    NEUTRAL = "NEUTRAL"


class Instance(models.Model):
    slug = models.SlugField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=64)
    status = models.CharField(max_length=64, choices=[(i.value, i.value) for i in InstanceStatus])
    modal_title = models.CharField(max_length=128, verbose_name="Modal title (status != PLAYING)")
    modal_text = models.TextField(verbose_name="Modal text (status != PLAYING)")
    victory = models.CharField(max_length=64, choices=[(t.value, t.value) for t in PlayerTeam], blank=True, null=True)

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
    slug = models.SlugField(max_length=64, unique=True, db_index=True)
    kind = models.CharField(max_length=64, choices=[(k.value, k.value) for k in PuzzleKind])
    name = models.CharField(max_length=64)
    picture = models.ImageField(upload_to="puzzle")
    keys = models.ManyToManyField(Item, related_name="keys_puzzles", blank=True)
    riddle = models.TextField()
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


class Player(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=64)
    avatar = models.ImageField(upload_to="character")
    team = models.CharField(max_length=64, choices=[(t.value, t.value) for t in PlayerTeam])

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
    position = models.IntegerField(db_index=True)

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
    status = models.CharField(max_length=64, choices=[(status.value, status.value) for status in PlayerPuzzleStatus], db_index=True)
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


def check_victory(solved_player_puzzle, instance):
    final_puzzles = Puzzle.objects.filter(is_final=True)
    final_puzzle_ids = set(x.id for x in final_puzzles)
    if not final_puzzle_ids:
        # Special case with no final puzzle configured, we don't want to mess up with the game state
        return

    solved_final_puzzles = PlayerPuzzle.objects.filter(puzzle__in=[fp.id for fp in final_puzzles], status=PlayerPuzzleStatus.SOLVED.value).select_related('player')
    solved_final_puzzles_list = [x for x in solved_final_puzzles]
    solved_final_puzzles_list.append(solved_player_puzzle)

    puzzles_solved_by_team_SHERLOCK = [x for x in solved_final_puzzles_list if x.player.team == PlayerTeam.SHERLOCK.value]
    puzzles_solved_by_team_MORIARTY = [x for x in solved_final_puzzles_list if x.player.team == PlayerTeam.MORIARTY.value]

    unique_puzzles_solved_by_team_SHERLOCK = set(x.puzzle_id for x in puzzles_solved_by_team_SHERLOCK)
    unique_puzzles_solved_by_team_MORIARTY = set(x.puzzle_id for x in puzzles_solved_by_team_MORIARTY)

    if unique_puzzles_solved_by_team_SHERLOCK == final_puzzle_ids:
        logger.warning("cv1, victory for sherlock")
        instance.victory = PlayerTeam.SHERLOCK.value
        instance.save()
    elif unique_puzzles_solved_by_team_MORIARTY == final_puzzle_ids:
        logger.warning("cv2, victory for moriarty")
        instance.victory = PlayerTeam.MORIARTY.value
        instance.save()
    else:
        logger.warning("cv3")
        instance.victory = None
        instance.save()


@receiver(models.signals.pre_save, sender=PlayerPuzzle)
def toggle_player_puzzle_not_displayed(sender, instance, **kwargs):
    should_victory_be_checked = False

    try:
        old_instance = PlayerPuzzle.objects.get(id=instance.id)
    except PlayerPuzzle.DoesNotExist:
        if instance.status == PlayerPuzzleStatus.SOLVED.value and instance.puzzle.is_final:
            should_victory_be_checked = True
    else:
        if instance.status == PlayerPuzzleStatus.SOLVED.value and old_instance.status != PlayerPuzzleStatus.SOLVED.value and instance.puzzle.is_final:
            should_victory_be_checked = True

    if should_victory_be_checked:
        check_victory(instance, instance.player.instance)

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
    player_items_b = models.ManyToManyField(PlayerItem, related_name="peer_b_player_item", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = '__all__'


@receiver(models.signals.pre_save, sender=Trade)
def on_trade_pre_save(sender, instance, **kwargs):
    if instance.pk:
        return

    # Just making sure
    already_existing_trades = Trade.objects.filter(peer_a__in=[instance.peer_a, instance.peer_b]) | Trade.objects.filter(peer_b__in=[instance.peer_a, instance.peer_b])

    for trade in already_existing_trades:
        trade.delete()


def trade_peer_items(player_items, new_owner, duplicate=False):
    position_for_new_item = 0
    last_item_in_inventory = PlayerItem.objects.filter(player=new_owner).order_by('-position').first()
    if last_item_in_inventory:
        position_for_new_item = last_item_in_inventory.position + 1

    if duplicate:
        for player_item in player_items:
            new_player_item = PlayerItem.objects.create(player=new_owner, item=player_item.item, position=position_for_new_item)
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
        trade_peer_items(instance.player_items_a.all(), instance.peer_b, duplicate=instance.peer_a.team == PlayerTeam.NEUTRAL.value)
        trade_peer_items(instance.player_items_b.all(), instance.peer_a, duplicate=instance.peer_b.team == PlayerTeam.NEUTRAL.value)

        business_rules.notify_inventory(instance.peer_a)
        business_rules.notify_inventory(instance.peer_b)
        business_rules.notify_no_trade(instance.peer_a, instance.peer_b)

    else:
        business_rules.notify_trade(instance)
