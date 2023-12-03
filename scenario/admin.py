from django.contrib import admin

from scenario.models import (
    Instance,
    InstanceForm,
    Item,
    ItemForm,
    PuzzleForm,
    PlayerForm,
    Puzzle,
    Player,
    PlayerItem,
    PlayerPuzzle,
    Trade,
    PlayerPuzzleForm,
    PlayerItemForm,
    TradeForm,
)


class InstanceAdmin(admin.ModelAdmin):
    form = InstanceForm
    list_display = (
        "slug",
        "name",
        "status",
    )
    search_fields = (
        "slug",
        "name",
        "status",
        "modal_title",
        "modal_text",
    )


class ItemAdmin(admin.ModelAdmin):
    form = ItemForm
    list_display = (
        "name",
        "description",
        "image",
    )
    search_fields = (
        "name",
        "description",
    )


class PuzzleAdmin(admin.ModelAdmin):
    form = PuzzleForm
    list_display = (
        "slug",
        "kind",
        "name",
        "picture",
        "get_keys",
        "riddle",
        "answer",
        "get_bounty",
    )
    search_fields = (
        "slug",
        "kind",
        "name",
        "keys",
        "riddle",
        "answer",
        "bounty",
    )

    @admin.display(description="Keys")
    def get_keys(self, obj):
        return ", ".join([item.name for item in obj.keys.all()])

    @admin.display(description="Bounty")
    def get_bounty(self, obj):
        return ", ".join([item.name for item in obj.bounty.all()])


class PlayerAdmin(admin.ModelAdmin):
    form = PlayerForm
    list_display = (
        "instance",
        "slug",
        "name",
        "avatar",
        "team",
    )
    search_fields = (
        "instance",
        "slug",
        "name",
        "avatar",
        "team",
    )


class PlayerItemAdmin(admin.ModelAdmin):
    form = PlayerItemForm
    list_display = (
        "player",
        "item",
        "position",
    )
    search_fields = (
        "player",
        "item",
        "position",
    )


class PlayerPuzzleAdmin(admin.ModelAdmin):
    form = PlayerPuzzleForm
    list_display = (
        "player",
        "puzzle",
        "status",
        "is_displayed",
    )
    search_fields = (
        "player",
        "puzzle",
        "status",
    )


class TradeAdmin(admin.ModelAdmin):
    form = TradeForm
    list_display = (
        "peer_a",
        "peer_b",
        "status_a",
        "status_b",
        "get_player_items_a",
        "get_player_items_b",
    )
    search_fields = (
        "peer_a",
        "peer_b",
        "status_a",
        "status_b",
        "player_items_a",
        "player_items_b",
    )

    @admin.display(description="Player items A")
    def get_player_items_a(self, obj):
        return ", ".join(
            [str(item) for item in obj.player_items_a.select_related("item").all()]
        )

    @admin.display(description="Player items B")
    def get_player_items_b(self, obj):
        return ", ".join(
            [str(item) for item in obj.player_items_b.select_related("item").all()]
        )


admin.site.register(Instance, InstanceAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayerItem, PlayerItemAdmin)
admin.site.register(PlayerPuzzle, PlayerPuzzleAdmin)
admin.site.register(Trade, TradeAdmin)
