import scenario


def get_scenario_items_data(s):
    items = scenario.models.Item.objects.filter(scenario=s).all()

    data = [
        {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "image": item.image.url,
        } for item in items
    ]

    return data


def get_scenario_puzzles_data(s):
    puzzles = scenario.models.Puzzle.objects.filter(scenario=s).all()

    data = [
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

    return data
