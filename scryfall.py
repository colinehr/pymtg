from datetime import datetime, timezone
import os.path
import requests
import time
import urllib.parse
import util


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
        self.data = self.request.json()


def get_bulk_data(data_type='default_cards'):
    bulk_data_list = Request('bulk-data').data['data']
    data_to_get = [d for d in bulk_data_list if d['type'] == data_type][0]
    # Check if bulk data has any changes from last download
    uri = data_to_get['permalink_uri']
    dest = os.path.join('data', uri.split('/')[-1])
    last_dl = datetime.fromtimestamp(os.path.getmtime(dest), timezone.utc)
    last_update = datetime.fromisoformat(data_to_get['updated_at'])
    if last_dl < last_update:
        util.download(uri, 'data')
    return dest
