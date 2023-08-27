from django.shortcuts import render
import scenario
from django.http import JsonResponse
from scenario.business_rules import get_inventory_from_items


def get_scenario_data(request, instance_slug):
    instance = scenario.models.Instance.objects.filter(slug=instance_slug).get()
    items = scenario.models.Item.objects.filter(scenario=instance.scenario).all()
    puzzles = scenario.models.Puzzle.objects.filter(scenario=instance.scenario).all()

    scenario_data = {
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "image": item.image.url,
            } for item in items
        ],
        "puzzles": [
            {
                "id": puzzle.id,
                "name": puzzle.name,
                "description": puzzle.description,
                "picture": puzzle.picture.url,
                "keys": [x.id for x in puzzle.keys.all()],
                "answer": puzzle.answer,
                "bounty": [x.id for x in puzzle.bounty.all()],
            } for puzzle in puzzles
        ]
    }

    return JsonResponse(scenario_data)


def get_player_data(request, player_slug):
    player = scenario.models.Player.objects.filter(slug=player_slug).select_related('character').first()
    player_items = scenario.models.PlayerItem.objects.filter(player=player).all()
    player_puzzles = scenario.models.PlayerPuzzle.objects.filter(player=player).all()

    inventory = get_inventory_from_items([x for x in player_items if x.puzzle is None], 12)

    log = [
        {
            "puzzle_id": player_puzzle.puzzle_id,
            "status": player_puzzle.status,
        } for player_puzzle in player_puzzles
    ]

    # should not be more than one
    displayed_puzzles = [x for x in player_puzzles if x.is_displayed]
    displayed_puzzle = displayed_puzzles[0] if displayed_puzzles else None

    player_data = {
        "player": {
            "name": player.character.name,
            "avatar": player.character.avatar.url,
            "klass": player.character.klass,
            "money": player.money,
            "reputation": player.reputation if player.character.has_reputation else None,
        },
        "inventory": inventory,
        "displayed_puzzle": displayed_puzzle,
        "log": log,
    }

    return JsonResponse(player_data)
