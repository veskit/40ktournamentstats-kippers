import requests
import json


def fetch_for_event(event_id: str):
    body = {
        "_method": "GET",
        "include": "army,subEvent,user",
        "where": {
            "event": {"__type": "Pointer", "className": "Event", "objectId": event_id}
        },
    }
    headers = {
        "x-parse-client-version": "i1.19.0",
        "content-type": "application/json; charset=utf-8",
        "x-parse-application-id": "LVIMo8NuYgHLlaNNWQmZSJ6XbH6yqX5882yd6o1s",
        "x-parse-client-key": "MF4zADrzOFYpb1XoyfoXqrZbhUi6hIeMFJ9ZTtM5",
    }
    url = "https://api.bestcoastpairings.com/parse/classes/Player"
    resp = requests.post(url, json=body, headers=headers)
    return resp.json()


def filter_player_lists(event: dict):
    out = []
    players = event["results"]
    for player in players:
        if player.get("dropped"):
            continue
        user = player.get("user", {})
        name = f'{user.get("firstName","")} {user.get("lastName","")}'.strip()
        army_name = player.get("army", {}).get("name", "")
        list_url = player.get("armyList")

        out.append({"player": name, "army_name": army_name, "list_url": list_url})
    return out


def write_to_file(player_lists):
    with open("lists_cache/2.json", "w") as fp:
        json.dump(player_lists, fp)


def main():
    event = fetch_for_event("A6IlTb3bxD")
    player_lists = filter_player_lists(event)
    write_to_file(player_lists)


if __name__ == "__main__":
    main()
