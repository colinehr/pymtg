import sqlite3
import json
import re
import datetime

### TODO Inconsistent storage of file names

CARD_FILE = "data/scryfall-default-cards.json"
db_file = "data/cards.db"

def card_generator(f):
    with open(f, "r", encoding="utf-8") as json_file:
        for line in json_file:
            line = line.strip()
            if line[0] == '{':
                if line[-1] == ',':
                    line = line[:-1]
                try:
                    yield json.loads(line)
                except json.decoder.JSONDecodeError:
                    print(line)
                    raise

def convert_json_obj(s):
    s = s.decode('utf-8')
    if s == "None":
        return None
    return json.loads(s)

def connect():
    db = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    return db, c

def build():
    try:
        db, c = connect()
        cards = card_generator(CARD_FILE)
        cols = "(id text primary key, oracle_id text, name text, lang text, release_date date, layout text, mana_cost text, cmc real, type_line text, oracle_text text, power text, toughness text, loyalty text, colors list, color_identity list, card_faces list, set_code text, set_name text, set_type text, collector_number text, rarity text, flavor_text text, artist text, art_id text, price_usd real)"
        json_keys = ("id", "oracle_id", "name", "lang", "released_at", "layout", "mana_cost", "cmc", "type_line", "oracle_text", "power", "toughness", "loyalty", "colors", "color_identity", "card_faces", "set", "set_name", "set_type", "collector_number", "rarity", "flavor_text", "artist", "illustration_id", "price_usd")
        c = db.cursor()
        c.execute("DROP TABLE cards")
        c.execute("CREATE TABLE cards" + cols)
        for card in cards:
            for key in card:
                if type(card[key]) in (list, dict):
                    card[key] = json.dumps(card[key])                    
            cmd = "INSERT INTO cards VALUES (" + "?," * (len(json_keys) - 1) + "?)"
            c.execute(cmd, tuple((str(card.get(key)) for key in json_keys)))
        db.commit()
        db.close()
    except:
        db.close()
        raise

def card_named(name):
    db, c = connect()
    name = re.sub(r"'", r"''", name)    # escape single quotes
    try:
        c.execute("SELECT * FROM cards WHERE name == '" + name + "' ORDER BY release_date DESC")
    except:
        db.close()
        raise
    card = dict(c.fetchone())
    db.close()
    return card

def search(search_str, unique="cards"):
    # Connect to database
    db, c = connect()
    # Decide which editions of cards to return
    if unique == "cards":
        grouping = " GROUP BY oracle_id"
    elif unique == "art":
        grouping = " GROUP BY art_id"
    else:
        grouping = ""
    # Form the sqlite command
    try:
        c.execute("SELECT * FROM cards WHERE " + parse(search_str) + grouping)
    except:
        db.close()
        raise
    result = [dict(card) for card in c.fetchall()]
    db.close()
    return result

def parse(search_str):
    regexp = r"\w+[:=<>!]+\w+"
    tokens = re.findall(regexp, search_str)
    rest = re.sub(regexp, "", search_str).strip().split()
    result = []
    for token in tokens:
        result.append(parse_token(token))
    if len(rest) > 0:
        result.append("name LIKE '%" + '%'.join(rest) + "%'")
    return " AND ".join(result)

def parse_token(token):
    keywords = {"c:": "colors",
                "id:": "color_identity",
                "o:": "oracle_text",
                "t:": "type_line",
                "e:": "set_code"}
    for keyword in keywords:
        if re.match(keyword, token):
            return keywords[keyword] + " LIKE '%" + token[len(keyword):] + "%'"

def is_regular_set(set_type):
    return set_type == "core" or \
        set_type == "expansion" or \
        set_type == "masters" or \
        set_type == "draft_innovation" or \
        set_type == "commander"

class Query():

    keywords = {"o:": "oracle_text",
                "t:": "type_line"}

    def __init__(self, search_str):
        self.search_str = search_str
        regexp = r"(\w+[:=<>!]+)(\w+|\'[\w ]+\')"
        self.tokens = re.findall(regexp, search_str)
        self.tokens += re.sub(regexp, "", search_str).strip().split()

    def parse_default(keyword, query):
        return Query.keywords[keyword] + " LIKE '%" + query + "%'"

# begin main
#sqlite3.register_adapter(list, adapt_json_obj)
#sqlite3.register_adapter(dict, adapt_json_obj)
sqlite3.register_converter("list", convert_json_obj)
sqlite3.register_converter("dict", convert_json_obj)
#sqlite3.register_converter("text", convert_json_obj)

#print("building database...", end='')
#build()
#print("done")
