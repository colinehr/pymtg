from enum import Enum
from fuzzywuzzy import process
from sqlalchemy import (Column, Date, Float, String, UniqueConstraint,
                        ForeignKey, Integer)
from database import Base, Session
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, Unicode
import json
import util


class _ColorSet(TypeDecorator):

    impl = Unicode

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        return set([Color(x) for x in json.loads(value)])


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

    @classmethod
    def get(cls, set_code: str, number: str):
        session = Session()
        q = session.query(cls).filter(cls.set == set_code)\
                              .filter(cls.collector_number == number)
        printing_obj = q.first()
        session.close()
        return printing_obj

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

    def is_regular(self) -> bool:
        regular_set_types = ('core',
                             'expansion',
                             'masters',
                             'draft_innovation')
        return self.set_type in regular_set_types


class Color(Enum):
    WHITE = 'W'
    BLUE = 'U'
    BLACK = 'B'
    RED = 'R'
    GREEN = 'G'
