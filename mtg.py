#!/usr/bin/env python

import database
import argparse

from enum import Enum
from fuzzywuzzy import process
from sqlalchemy import (Column, Date, Float, String, UniqueConstraint,
                        ForeignKey, Integer, exc)
from database import Base, Session
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, Unicode
from datetime import date
import json
import util
import scryfall
import warnings
from collections import Counter


class _ColorSet(TypeDecorator):

    impl = Unicode

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return "[]"

    def process_result_value(self, value, dialect):
        if value is not None:
            return set([Color(x) for x in json.loads(value)])
        return set()


class Card(Base):
    """Class for representing Magic cards.

    Each member of the Card class represents an abstract Magic card represented
    in Oracle, NOT a physical printing of a card (see the card.Printing class).
    So for example two cards with the same name are represented by the same
    Card class member.

    The most common way to initialize a Card object is with the Card.named
    class method.

    Attributes:
        oracle_id (str): Unique id from Scryfall for this card.
        name (str): Name of this card.
        cmc (float): Converted mana cost of this card. (Some silver-bordered
            cards have fractional CMCs.)
        mana_cost (str): String representation of the card's mana cost symbols.
        colors (Set[Color]): Set of the colors of this card as defined by the
            Magic rules (only colors of symbols in the mana cost or any color
            indicator).
        color_identity (Set[Color]): Set of the colors in the card's color
            identity.
        type_line (str): Type line of the card.
        oracle_text (str): The most up-to-date oracle text of the card.
        power (str): Power of the card, if any.
        toughness (str): Toughness of the card, if any.
        loyalty (str): Starting loyalty of the card, if any.
        printings (List[Printing]): List of all physical printings of this
            card, represented by Printing objects.

    """

    __tablename__ = 'cards'
    __table_args__ = (
        UniqueConstraint("oracle_id", sqlite_on_conflict='REPLACE'),
    )
    session = Session()

    oracle_id = Column(String, primary_key=True)
    cmc = Column(Float)
    name = Column(String, nullable=False)
    colors = Column(_ColorSet)
    color_identity = Column(_ColorSet, nullable=False)
    oracle_text = Column(String)
    loyalty = Column(String)
    mana_cost = Column(String)
    power = Column(String)
    toughness = Column(String)
    type_line = Column(String, nullable=False)
    # faces = relationship("Face", primaryjoin=f"Face.name.in_({_parse_faces(Card.name)})")
    printings = relationship("Printing",
                             lazy='joined', innerjoin=True, backref='card')

    @classmethod
    def named(cls, name, exact=False, session=session):
        """Factory method for returning a Card object of the given name.

        Args:
            name (str): The name of the card to return.
            exact (bool): Invokes fuzzy matching of name if false.
                Defaults to false.

        """
        if not exact:
            name = cls.autocomplete(name)
        return session.query(cls).filter(cls.name == name).first()

    @classmethod
    def from_scryfall(cls, data):
        # data['faces'] = [Face.from_scryfall(face)
        #                  for face in data.get('card_faces')]
        col_names = [c.name for c in Card.__table__.columns]
        return Card(**util.restriction(data, col_names))

    @classmethod
    def all_names(cls):
        """Returns a list containing the names of every card in the game."""
        q = cls.session.query(cls.__table__.columns['name']).distinct()
        return sorted([name[0] for name in q.all()])

    @classmethod
    def autocomplete(cls, name: str) -> str:
        """Fuzzy matcher for card names.

        Args:
            name (str): String to match.

        Returns:
            str: The closest actual card name to argument.

        """
        names = cls.all_names()
        matchers = (util.shortest_exact_match,
                    util.shortest_starting_match,
                    util.shortest_token_match)
        for matcher in matchers:
            match = matcher(name, names)
            if match is not None:
                return match
        return process.extractOne(name, cls.all_names())[0]

    def is_in_set(self, set_code):
        """Test for if the Card has been printed in a particular set.

        Args:
            set_code (str): Code of set to check for printing.

        Returns:
            bool: True if Card has been printed in the set.

        """
        return any([p.set_code == set_code for p in self.printings])

    def representative(self):
        """Returns the newest 'regular' printing of the card."""
        sorted_printings = sorted(self.printings,
                                  key=lambda p: p.set.release_date,
                                  reverse=True)
        regular_printings = [p for p in sorted_printings if p.set.is_regular()]
        if len(regular_printings) > 0:
            return regular_printings[0]
        else:
            return sorted_printings[0]

    def __repr__(self):
        return f"Card.named('{self.name}')"

    def __str__(self):
        output =  f"""{self.name:<40} {self.mana_cost}\n{self.type_line}\n{self.oracle_text:<40}"""
        return output

    def __hash__(self):
        return self.oracle_id.__hash__()

    def __eq__(self, other):
        return self.oracle_id == other.oracle_id

    @staticmethod
    def _parse_faces(name):
        return name.split(" // ")


class Face(Base):

    __tablename__ = 'faces'
    __table_args__ = (
        UniqueConstraint("name", sqlite_on_conflict='REPLACE'),
    )
    name = Column(String, nullable=False, primary_key=True)
    type_line = Column(String)
    oracle_text = Column(String)
    mana_cost = Column(String)
    colors = Column(_ColorSet)
    color_indicator = Column(_ColorSet)
    power = Column(String)
    toughness = Column(String)
    flavor_text = Column(String)

    @classmethod
    def from_scryfall(self, data):
        col_names = [c.name for c in Face.__table__.columns]
        return Face(**util.restriction(data, col_names))


class MultifacedCard(Card):
    pass


class Token(Card):
    pass


class Printing(Base):
    """Class representing an actual, physical (or digital) printing of a card.

    Owing to their link to physical copies of cards, each Printing can be
    determined completely from the set it was printed in and its collector
    number in the set.

    """

    __tablename__ = 'printings'
    __table_args__ = (
        UniqueConstraint('id', sqlite_on_conflict='IGNORE'),
    )
    id = Column(String, primary_key=True)
    oracle_id = Column(String, ForeignKey("cards.oracle_id"))
    collector_number = Column(String)
    set_code = Column(String, ForeignKey('sets.code'))
    set = relationship('Set')
    watermark = Column(String)
    rarity = Column(String)
    image_uri = Column(String)
    flavor_text = Column(String)
    artist = Column(String)

    @classmethod
    def get(cls, set_code: str, number: str):
        session = Session()
        q = session.query(cls).filter(cls.set == set_code)\
                              .filter(cls.collector_number == number)
        printing_obj = q.first()
        session.close()
        return printing_obj

    @classmethod
    def from_scryfall(cls, data):
        printing_col_names = [c.name for c in Printing.__table__.columns]
        printing_data = util.convert(data, {'set': 'set_code'})
        try:
            if 'image_uris' in printing_data:
                printing_data['image_uri'] = printing_data['image_uris']['normal']
            else:
                printing_data['image_uri'] = None
        except KeyError:
            print(printing_data)
            raise
        printing_data = util.restriction(data, printing_col_names)
        printing_data['card'] = Card.from_scryfall(data)
        return Printing(**printing_data)

    def __repr__(self):
        return f"Printing.get({self.set_code}, {self.collector_number})"


class Set(Base):

    __tablename__ = 'sets'
    __table_args__ = (
        UniqueConstraint('id', sqlite_on_conflict='IGNORE'),
    )
    session = Session()

    id = Column(String, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String, unique=True)
    release_date = Column(Date, nullable=True)
    card_count = Column(Integer)
    set_type = Column(String)
    printings = relationship('Printing', back_populates='set')

    @classmethod
    def from_code(cls, code):
        q = cls.session.query(cls).filter(cls.code == code)
        return q.first()

    @classmethod
    def from_scryfall(cls, data):
        mapping = {'released_at': 'release_date'}
        data = util.convert(data, mapping)
        data['release_date'] = date.fromisoformat(data['release_date'])
        col_names = [c.name for c in Set.__table__.columns]
        return Set(**util.restriction(data, col_names))

    def is_regular(self) -> bool:
        regular_set_types = ('core',
                             'expansion',
                             'masters',
                             'draft_innovation')
        return self.set_type in regular_set_types


class Decklist(object):

    def __init__(self, main=None, side=None):
        self.mainboard = Counter(main)
        self.sideboard = Counter(side)
        self.format = None
        self.date = None

    def add(self, card_name, quantity=1):
        card = Card.named(card_name)
        self.mainboard.update({card: quantity})

    def add_sideboard(self, card_name, quantity=1):
        card = Card.named(card_name)
        self.sideboard.update({card: quantity})

    def colors(self):
        colors = set()
        for card in self.mainboard + self.sideboard:
            colors |= card.colors
        return colors

    def creatures(self):
        return [card for card in self.mainboard if "Creature" in card.type_line]

    def lands(self):
        return [card for card in self.mainboard if "Land" in card.type_line]

    def as_dict(self):
        mb = {c.name: q for (c, q) in self.mainboard.items()}
        sb = {c.name: q for (c, q) in self.sideboard.items()}
        return {"mainboard": mb, "sideboard": sb}

    def export_json(self):
        return json.dumps(self.as_dict())

    @classmethod
    def import_arena(cls, txt):
        dl = Decklist()
        txt = txt.strip()
        mb, sb = [l.split("\n")[1:] for l in txt.split("\n\n")]
        for elem in mb:
            elem_split = elem.split(' ')
            name = ' '.join(elem_split[1:-2])
            quantity = int(elem_split[0])
            dl.add(name, quantity)
        for elem in sb:
            elem_split = elem.split(' ')
            name = ' '.join(elem_split[1:-2])
            quantity = int(elem_split[0])
            dl.add_sideboard(name, quantity)
        return dl

    def __str__(self):
        result = ""
        mb = sorted(self.mainboard.items(),
                    key=lambda pair: pair[0].name)
        for card, quantity in mb:
            result += f"{quantity} {card.name}\n"
        result += "\nSideboard:\n"
        for card, quantity in self.sideboard.items():
            result += f"{quantity} {card.name}\n"
        return result


class Color(Enum):
    WHITE = 'W'
    BLUE = 'U'
    BLACK = 'B'
    RED = 'R'
    GREEN = 'G'


def update_sets(verbose=True):
    sets = scryfall.Request("sets").data
    session = Session()
    known_ids = [t[0] for t in session.query(Set.id).all()]
    for s in sets:
        if s['id'] not in known_ids:
            session.add(Set.from_scryfall(s))
            if verbose:
                print(f"New set: {s['name']} ({s['code']} [{s['card_count']} cards])")
    session.commit()
    session.close()


def update_cards(verbose=True):
    session = Session()
    bulk_data_uri = scryfall.get_bulk_data()
    bulk_data = scryfall.bulk_data_generator(bulk_data_uri)
    printings = (Printing.from_scryfall(p) for p in bulk_data)
    session.add_all(printings)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', category=exc.SAWarning)
        session.commit()
    session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="Action you want to perform")
    parser.add_argument("-n", "--name", type=str,
                        help="")
    parser.add_argument("-d", "--deck", type=str)
    args = parser.parse_args()
    if args.action == "initialize":
        database.initialize(verbose=True)
    elif args.action == "update":
        update_sets()
        update_cards()
    elif args.action == "card":
        if args.name:
            result = Card.named(args.name)
        print(result)
    elif args.action == "add":
        pass
