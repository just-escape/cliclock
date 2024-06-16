from enum import Enum

from django.db import models
from django import forms


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
    status = models.CharField(
        max_length=64, choices=[(i.value, i.value) for i in InstanceStatus]
    )
    modal_title = models.CharField(
        max_length=128, verbose_name="Modal title (status != PLAYING)"
    )
    modal_text = models.TextField(verbose_name="Modal text (status != PLAYING)")

    def __str__(self):
        return f"Instance {self.name}"


class InstanceForm(forms.ModelForm):
    class Meta:
        model = Instance
        fields = "__all__"


class Item(models.Model):
    name = models.CharField(max_length=64)
    name_en = models.CharField(max_length=64)
    description = models.TextField()
    description_en = models.TextField()
    image = models.ImageField(upload_to="item")

    def __str__(self):
        return f"Item {self.name}"


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = "__all__"


class PuzzleKind(Enum):
    KEY_RIDDLE_BOUNTY = "KEY_RIDDLE_BOUNTY"
    KEY_BOUNTY = "KEY_BOUNTY"
    BOUNTY = "BOUNTY"


class Puzzle(models.Model):
    slug = models.SlugField(max_length=64, unique=True, db_index=True)
    kind = models.CharField(
        max_length=64, choices=[(k.value, k.value) for k in PuzzleKind]
    )
    name = models.CharField(max_length=64)
    name_en = models.CharField(max_length=64)
    picture = models.ImageField(upload_to="puzzle")
    intro = models.TextField()
    intro_en = models.TextField()
    keys = models.ManyToManyField(Item, related_name="keys_puzzles", blank=True)
    consumable_keys = models.ManyToManyField(
        Item, related_name="consumable_keys_puzzles", blank=True
    )
    riddle = models.TextField()
    riddle_en = models.TextField()
    answer = models.CharField(max_length=64)
    answer_en = models.CharField(max_length=64)
    final = models.TextField()
    final_en = models.TextField()
    bounty = models.ManyToManyField(Item, related_name="bounty_puzzles", blank=True)

    def __str__(self):
        return f"Puzzle {self.name}"


class PuzzleForm(forms.ModelForm):
    class Meta:
        model = Puzzle
        fields = "__all__"


class Player(models.Model):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=64)
    avatar = models.ImageField(upload_to="character")
    team = models.CharField(
        max_length=64, choices=[(t.value, t.value) for t in PlayerTeam]
    )
    nth_place = models.IntegerField(null=True, default=None)

    def __str__(self):
        return f"Player {self.name}"


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = "__all__"


class PlayerItem(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    position = models.IntegerField(db_index=True)

    def __str__(self):
        return f"PlayerItem {self.player} - {self.item.name}"


class PlayerItemForm(forms.ModelForm):
    class Meta:
        model = PlayerItem
        fields = "__all__"


class PlayerPuzzleStatus(Enum):
    OBSERVED = "OBSERVED"
    UNLOCKED = "UNLOCKED"
    SOLVED = "SOLVED"


class PlayerPuzzle(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=64,
        choices=[(status.value, status.value) for status in PlayerPuzzleStatus],
        db_index=True,
    )
    is_displayed = models.BooleanField(default=False)

    def __str__(self):
        return f"PlayerPuzzle {self.player} - {self.puzzle.name}"


class PlayerPuzzleForm(forms.ModelForm):
    class Meta:
        model = PlayerPuzzle
        fields = "__all__"


class TradeStatus(Enum):
    TRADING = "TRADING"
    ACCEPTED = "ACCEPTED"


class Trade(models.Model):
    peer_a = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="peer_a_trade"
    )
    peer_b = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="peer_b_trade"
    )
    status_a = models.CharField(
        max_length=64, choices=[(status.value, status.value) for status in TradeStatus]
    )
    status_b = models.CharField(
        max_length=64, choices=[(status.value, status.value) for status in TradeStatus]
    )
    player_items_a = models.ManyToManyField(
        PlayerItem, related_name="peer_a_player_item", blank=True
    )
    player_items_b = models.ManyToManyField(
        PlayerItem, related_name="peer_b_player_item", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = "__all__"
