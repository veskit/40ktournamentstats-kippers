from doctest import OutputChecker
import json
import requests
from bs4 import BeautifulSoup


ORIGINAL_FILE = "payload_original.json"
LATEST_FILE = "payload.json"


def get_army_list_text_from_html(html) -> str:
    bs = BeautifulSoup(html.replace("<br>", "\n"), features="html.parser")
    army_list = bs.find(class_="list")
    return army_list.get_text()


def load_file(filename: str):
    players = {}
    with open(filename, "r") as rp:
        payload = json.load(rp)

    for p in payload["results"]:
        user = p["user"]
        army = p.get("army", {})
        name = user.get("firstName", "") + " " + user.get("lastName", "")
        players[name] = {
            "name": name,
            "armyList": p.get("armyList", ""),
            "army": army.get("name"),
        }

    return players


def compare(original, latest):
    changes = []
    for p in latest.values():
        latest_name = p["name"]
        if latest_name not in original:
            changes.append({"action": "add", "player": p})
        else:
            original_player = original[latest_name]
            if original_player["armyList"] != p["armyList"]:
                changes.append(
                    {
                        "action": "change",
                        "player": p["name"],
                        "originalList": original_player["armyList"],
                        "newList": p["armyList"],
                    }
                )
    return changes


def get_list_from_url(url):
    response = requests.get(url)
    return get_army_list_text_from_html(response.text)


def diff_lists(changes):
    for c in changes:
        if c["action"] == "change":
            original_list = get_list_from_url(c["originalList"])
            new_list = get_list_from_url(c["newList"])


if __name__ == "__main__":
    original = load_file(ORIGINAL_FILE)
    latest = load_file(LATEST_FILE)
    diffs = compare(original, latest)
    with open("diffs.json", "w") as wp:
        json.dump(diffs, wp)
