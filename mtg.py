#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
#import database
#import argparse


Base = declarative_base()
engine = create_engine('sqlite:///data/cards_test.db')
Session = sessionmaker(bind=engine)


from card import (Card, Printing, Set)


# __all__ = ['cards', 'database', 'scryfall']

#if __name__ == "__main__":
#    parser = argparse.ArgumentParser()
#    parser.add_argument("action", help="Action you want to perform")
#    args = parser.parse_args()
#    if args.action == "update":
#        database.update(True)
#    elif args.action == "card":
#        pass

