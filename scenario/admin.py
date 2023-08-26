from django.contrib import admin

import scenario


class ScenarioAdmin(admin.ModelAdmin):
    form = scenario.models.ScenarioForm
    list_display = (
        'slug',
        'name',
    )
    search_fields = (
        'slug',
        'name',
    )


class InstanceAdmin(admin.ModelAdmin):
    form = scenario.models.InstanceForm
    list_display = (
        'scenario',
        'slug',
        'name',
        'created_at',
    )
    search_fields = (
        'scenario',
        'slug',
        'name',
        'created_at',
    )


class ItemAdmin(admin.ModelAdmin):
    form = scenario.models.ItemForm
    list_display = (
        'scenario',
        'name',
        'description',
        'image',
    )
    search_fields = (
        'scenario',
        'name',
        'description',
    )


class CharacterAdmin(admin.ModelAdmin):
    form = scenario.models.CharacterForm
    list_display = (
        'scenario',
        'name',
        'avatar',
        'klass',
        'starting_money',
        'has_reputation',
        'starting_reputation',
        'get_starting_items',
    )
    search_fields = (
        'scenario',
        'name',
        'avatar',
        'klass',
        'starting_money',
        'starting_reputation',
        'starting_items',
    )

    @admin.display(description='Starting items')
    def get_starting_items(self, obj):
        return ", ".join([item.name for item in obj.starting_items.all()])


class PuzzleAdmin(admin.ModelAdmin):
    form = scenario.models.PuzzleForm
    list_display = (
        'scenario',
        'name',
        'description',
        'picture',
        'get_keys',
        'answer',
        'get_bounty',
    )
    search_fields = (
        'scenario',
        'name',
        'description',
        'keys',
        'answer',
        'bounty',
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
        'character',
        'money',
        'reputation',
    )
    search_fields = (
        'instance',
        'character',
        'money',
        'reputation',
    )


class PlayerItemAdmin(admin.ModelAdmin):
    form = scenario.models.PlayerItemForm
    list_display = (
        'player',
        'item',
        'puzzle',
        'position',
    )
    search_fields = (
        'player',
        'item',
        'puzzle',
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


admin.site.register(scenario.models.Scenario, ScenarioAdmin)
admin.site.register(scenario.models.Instance, InstanceAdmin)
admin.site.register(scenario.models.Item, ItemAdmin)
admin.site.register(scenario.models.Character, CharacterAdmin)
admin.site.register(scenario.models.Puzzle, PuzzleAdmin)
admin.site.register(scenario.models.Player, PlayerAdmin)
admin.site.register(scenario.models.PlayerItem, PlayerItemAdmin)
admin.site.register(scenario.models.PlayerPuzzle, PlayerPuzzleAdmin)
