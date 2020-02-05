from mtg import Decklist, Set
from datetime import date
import json


class Draft(object):

    def __init__(self, decklist, card_set):
        self.decklist = decklist
        self.set = card_set
        self.games = []
        self.wins = 0
        self.losses = 0
        self.draws = 0

    @property
    def record(self):
        rec = str(self.wins) + "-" + str(self.losses)
        if self.draws > 0:
            rec += "-" + str(self.draws)
        return rec

    def add_game(self, game):
        self.games.append(game)
        if game.wins > game.losses:
            self.wins += 1
        elif game.wins < game.losses:
            self.losses += 1
        else:
            self.draws += 1

    def export_json(self):
        return json.dumps({"deck": self.decklist.as_dict(),
                           "record": self.record,
                           "games": [g.as_dict() for g in self.games]})


class Game(object):

    def __init__(self, decklist, day, wins, losses):
        self.decklist = decklist
        self.date = day
        self.wins = wins
        self.losses = losses

    def as_dict(self):
        return {"date": str(self.date),
                "wins": self.wins,
                "losses": self.losses}

    def export_json(self):
        return json.dumps(self.as_dict())

