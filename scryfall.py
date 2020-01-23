"""'Dumb' implementation of Scryfall's REST-like Magic API.

For more information about Scryfall's API, see https://scryfall.com/docs/api

    Typical usage example:

    scryfall.Request('/cards/search?color=U&cmc=3')

"""

from card import Card, Printing, Set
from collections import deque
from datetime import datetime, timezone, date
import os.path
import requests
import time
import urllib.parse
import util
import json


# TODO: cache data

class Request(object):

    last_request = datetime.fromordinal(1)

    def __init__(self, uri):
        api_url = 'https://api.scryfall.com'
        self.url = urllib.parse.urljoin(api_url, uri)
        timedelta = datetime.now() - Request.last_request
        if timedelta.seconds < 0.1:
            time.sleep(0.1 - timedelta.seconds)
        try:
            self.request = requests.get(self.url)
            self.request.raise_for_status()
        except requests.exceptions.HTTPError:
            raise Exception(self.request.json()['details'])
        finally:
            Request.last_request = datetime.now()
        self.data = parse(self.request.json())


class PaginatedList(object):
    """Iterator for list objects returned by Scryfall."""

    def __init__(self, scryfall_data):
        self.data = deque(scryfall_data['data'])
        self.has_more = scryfall_data['has_more']
        self.next_page = scryfall_data.get('next_page')

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.data) == 0:
            if self.has_more:
                next_page_request = Request(self.next_page).data
                self.__init__(next_page_request)
            else:
                raise StopIteration
        return parse(self.data.popleft())


def get_bulk_data(data_type='default_cards'):
    bulk_data = Request('bulk-data')
    bulk_data_list = bulk_data.data
    data_to_get = [d for d in bulk_data_list if d['type'] == data_type][0]
    # Check if bulk data has any changes from last download
    uri = data_to_get['permalink_uri']
    dest = os.path.join('data', uri.split('/')[-1])
    last_dl = datetime.fromtimestamp(os.path.getmtime(dest), timezone.utc)
    last_update = datetime.fromisoformat(data_to_get['updated_at'])
    if last_dl < last_update:
        util.download(uri, 'data')
    return dest


def parse(data):
    obj_type = data['object']
    if obj_type == 'list':
        return PaginatedList(data)
    if obj_type == 'card':
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
        printing_data['card'] = Card(**adapt_to_card(data))
        return Printing(**printing_data)
    if obj_type == 'set':
        return Set(**adapt_to_set(data))
    else:
        return data


def adapt_to_card(data):
    col_names = [c.name for c in Card.__table__.columns]
    return util.restriction(data, col_names)


def adapt_to_set(data):
    mapping = {'released_at': 'release_date'}
    data = util.convert(data, mapping)
    data['release_date'] = date.fromisoformat(data['release_date'])
    col_names = [c.name for c in Set.__table__.columns]
    return util.restriction(data, col_names)


def bulk_data_generator(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line[0] == '{':
                if line[-1] == ',':
                    line = line[:-1]
                try:
                    yield parse(json.loads(line))
                except json.decoder.JSONDecodeError:
                    print(line)
                    raise
