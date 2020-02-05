# import scryfall
import warnings
from sqlalchemy import exc, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine('sqlite:///data/cards_test.db')
Session = sessionmaker(bind=engine)


def initialize(verbose=False):
    Base.metadata.drop_all(engine)
    if verbose:
        print("Creating tables...", end='', flush=True)
    Base.metadata.create_all(engine)
    if verbose:
        print("done")
    # update(verbose)


# def update(verbose=False):
#     if verbose:
#         print("Downloading card data...", end='', flush=True)
#     scryfall.get_bulk_data('default_cards')
#     if verbose:
#         print("done")
#         print("Downloading set data...", end='', flush=True)
#     sets = scryfall.Request('sets').data
#     if verbose:
#         print("done")
#         print("Populating database...", end='', flush=True)
#     session = Session()
#     bulk = scryfall.bulk_data_generator('data/scryfall-default-cards.json')
#     session.add_all(sets)
#     session.add_all(bulk)
#     with warnings.catch_warnings():
#         warnings.simplefilter('ignore', category=exc.SAWarning)
#         session.commit()
#     session.close()
#     if verbose:
#         print("done")
