import os

from django.dispatch import receiver
from django.db import models
from django import forms

from scenario.web_socket import web_socket_notifier as wsn, MessageType
from scenario.business_rules import get_inventory_from_items


class Scenario(models.Model):
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"Scenario {self.name}"


class ScenarioForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = '__all__'


class Instance(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Instance {self.name} ({self.scenario})"


class InstanceForm(forms.ModelForm):
    class Meta:
        model = Instance
        fields = '__all__'


class Item(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    description = models.TextField()
    image = models.ImageField(upload_to="item")

    def __str__(self):
        return f"Item {self.name} ({self.scenario})"


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


class Character(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    avatar = models.ImageField(upload_to="character")
    klass = models.CharField(max_length=64, verbose_name="Class")
    starting_money = models.IntegerField()
    has_reputation = models.BooleanField(default=False)
    starting_reputation = models.IntegerField()
    starting_items = models.ManyToManyField(Item, blank=True)

    def __str__(self):
        return f"Character {self.name} ({self.scenario})"


@receiver(models.signals.post_delete, sender=Character)
def auto_delete_avatar_on_character_delete(sender, instance, **kwargs):
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)


@receiver(models.signals.pre_save, sender=Character)
def auto_delete_avatar_on_charater_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Character.objects.get(pk=instance.pk).avatar
    except Character.DoesNotExist:
        return False

    new_file = instance.avatar
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = '__all__'


class Puzzle(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    description = models.TextField()
    picture = models.ImageField(upload_to="puzzle")
    keys = models.ManyToManyField(Item, related_name="keys_puzzles", blank=True)
    answer = models.CharField(max_length=64)
    bounty = models.ManyToManyField(Item, related_name="bounty_puzzles", blank=True)

    def __str__(self):
        return f"Puzzle {self.name} ({self.scenario})"


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


class Player(models.Model):
    slug = models.SlugField(max_length=64, unique=True)
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    money = models.IntegerField()
    reputation = models.IntegerField()

    def __str__(self):
        return f"Player {self.character.name} ({self.instance.name})"


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = '__all__'


class PlayerItem(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, null=True, blank=True, on_delete=models.CASCADE)
    position = models.IntegerField()

    def __str__(self):
        return f"PlayerItem {self.player} - {self.item.name}"


class PlayerItemForm(forms.ModelForm):
    class Meta:
        model = PlayerItem
        fields = '__all__'


class PlayerPuzzle(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    status = models.CharField(max_length=64)
    is_displayed = models.BooleanField(default=False)

    def __str__(self):
        return f"PlayerPuzzle {self.player.character} - {self.puzzle.name}"


class PlayerPuzzleForm(forms.ModelForm):
    class Meta:
        model = PlayerPuzzle
        fields = '__all__'


@receiver(models.signals.post_save, sender=Player)
def notify_update_player(sender, instance, **kwargs):
    channel = instance.slug
    data = {
        "name": instance.character.name,
        "avatar": instance.character.avatar.url,
        "klass": instance.character.klass,
        "money": instance.money,
        "reputation": instance.reputation if instance.character.has_reputation else None,
    }

    wsn.notify(channel, {"type": MessageType.PUT_PLAYER, "data": data})


@receiver(models.signals.post_save, sender=PlayerItem)
def notify_update_inventory(sender, instance, **kwargs):
    player_items = scenario.models.PlayerItem.objects.filter(player=instance.player).all()
    inventory = get_inventory_from_items([x for x in player_items if x.puzzle is None], 12)

    channel = instance.player.slug

    wsn.notify(channel, {"type": MessageType.PUT_INVENTORY, "data": inventory})
