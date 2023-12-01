from django.contrib import admin

import scenario


class InstanceAdmin(admin.ModelAdmin):
    form = scenario.models.InstanceForm
    list_display = (
        'slug',
        'name',
        'status',
        'victory',
    )
    search_fields = (
        'slug',
        'name',
        'status',
        'modal_title',
        'modal_text',
    )


class ItemAdmin(admin.ModelAdmin):
    form = scenario.models.ItemForm
    list_display = (
        'name',
        'description',
        'image',
    )
    search_fields = (
        'name',
        'description',
    )


class PuzzleAdmin(admin.ModelAdmin):
    form = scenario.models.PuzzleForm
    list_display = (
        'slug',
        'kind',
        'name',
        'picture',
        'get_keys',
        'riddle',
        'answer',
        'get_bounty',
        'is_final',
    )
    search_fields = (
        'slug',
        'kind',
        'name',
        'keys',
        'riddle',
        'answer',
        'bounty',
        'is_final',
    )

    @admin.display(description='Keys')
    def get_keys(self, obj):
        return ", ".join([item.name for item in obj.keys.all()])

    @admin.display(description='Bounty')
    def get_bounty(self, obj):
        return ", ".join([item.name for item in obj.bounty.all()])


class PlayerAdmin(admin.ModelAdmin):
    form = scenario.models.PlayerForm
    list_display = (
        'instance',
        'slug',
        'name',
        'avatar',
        'team',
    )
    search_fields = (
        'instance',
        'slug',
        'name',
        'avatar',
        'team',
    )


class PlayerItemAdmin(admin.ModelAdmin):
    form = scenario.models.PlayerItemForm
    list_display = (
        'player',
        'item',
        'position',
    )
    search_fields = (
        'player',
        'item',
        'position',
    )


class PlayerPuzzleAdmin(admin.ModelAdmin):
    form = scenario.models.PlayerPuzzleForm
    list_display = (
        'player',
        'puzzle',
        'status',
        'is_displayed',
    )
    search_fields = (
        'player',
        'puzzle',
        'status',
    )


class TradeAdmin(admin.ModelAdmin):
    form = scenario.models.TradeForm
    list_display = (
        'peer_a',
        'peer_b',
        'status_a',
        'status_b',
        'get_player_items_a',
        'get_player_items_b',
    )
    search_fields = (
        'peer_a',
        'peer_b',
        'status_a',
        'status_b',
        'player_items_a',
        'player_items_b',
    )

    @admin.display(description='Player items A')
    def get_player_items_a(self, obj):
        return ", ".join([str(item) for item in obj.player_items_a.select_related('item').all()])

    @admin.display(description='Player items B')
    def get_player_items_b(self, obj):
        return ", ".join([str(item) for item in obj.player_items_b.select_related('item').all()])


admin.site.register(scenario.models.Instance, InstanceAdmin)
admin.site.register(scenario.models.Item, ItemAdmin)
admin.site.register(scenario.models.Puzzle, PuzzleAdmin)
admin.site.register(scenario.models.Player, PlayerAdmin)
admin.site.register(scenario.models.PlayerItem, PlayerItemAdmin)
admin.site.register(scenario.models.PlayerPuzzle, PlayerPuzzleAdmin)
admin.site.register(scenario.models.Trade, TradeAdmin)
