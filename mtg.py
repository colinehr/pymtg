from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()
engine = create_engine('sqlite:///data/cards_test.db')
Session = sessionmaker(bind=engine)

__all__ = ['cards', 'database', 'scryfall']
