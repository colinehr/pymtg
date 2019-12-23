import json
import requests
import os.path


def restriction(d, keys):
    """Return the dictionary that is the subdictionary of d over the specified
    keys"""
    return {key: d.get(key) for key in keys}


def generate_from_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line[0] == '{':
                if line[-1] == ',':
                    line = line[:-1]
                try:
                    yield json.loads(line)
                except json.decoder.JSONDecodeError:
                    print(line)
                    raise


def download(uri, filename='.'):
    if os.path.isdir(filename):
        filename = os.path.join(filename, uri.split('/')[-1])
    r = requests.get(uri)
    with open(filename, 'wb') as f:
        f.seek(0)
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)
        f.truncate()
    return filename


def shortest(str_list):
    if len(str_list) == 0:
        return None
    return sorted(str_list, key=len)[0]


def contains_all(s, l):
    for ss in l:
        if ss not in s:
            return False
    return True


def shortest_exact_match(s, l):
    return shortest([e for e in l if s.casefold() == e.casefold()])


def shortest_starting_match(s, l):
    return shortest([e for e in l if
                     e.casefold().startswith(s.casefold())])


def shortest_token_match(s, l):
    tokens = s.casefold().split()
    return shortest([e for e in l if contains_all(e.casefold(), tokens)])
