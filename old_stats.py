import requests
import csv
import bcp

EVENT_IDS = [
    "7qsyCj6xKp", # Kippers Melee
    # "A6IlTb3bxD",  # Seattle open
    # 'PzYQG9wJXA', # Dallas open
]

SCORE_FIELDS = [
    "dropped",
    "numWins",
    "battlePoints",
]

AUTH = ""
userId = ""

bcp = bcp.BcpCache()


def fetch_players_from_region(event_id: str):
    url = f"https://lrs9glzzsf.execute-api.us-east-1.amazonaws.com/prod/players?eventId={event_id}&inclEvent=false&inclMetrics=true&inclArmies=true&inclTeams=true&limit=2000&metrics=[%22resultRecord%22,%22record%22,%22numWins%22,%22battlePoints%22,%22WHArmyPoints%22,%22numWinsSoS%22,%22FFGBattlePointsSoS%22,%22mfSwissPoints%22,%22pathToVictory%22,%22mfStrengthOfSchedule%22,%22marginOfVictory%22,%22extendedNumWinsSoS%22,%22extendedFFGBattlePointsSoS%22,%22_id%22]"
    response = requests.get(url, headers={"Authorization": AUTH})
    return response.json()


def get_event_data(event_id: str):
    print(f"Fetching {event_id}")
    # metadata = fetch_event_metadata(event_id)
    players = bcp.fetch_players_from_event(event_id)

    return "boop", players


def wl_to_str(wl):
    if wl == 2:
        return "W"
    elif wl == 1:
        return "T"
    elif wl == 0:
        return "L"
    else:
        return "?"


def get_all_players():
    num_dropped = 0
    num_has_army = 0
    all_players = []
    for event_id in EVENT_IDS:
        event_name, players = get_event_data(event_id)
        for player in players:
            if player["dropped"]:
                num_dropped += 1
                continue
            if "army" in player:
                num_has_army += 1
            player_out = {
                "name": player["firstName"] + " " + player["lastName"],
                "region": event_name,
                "army": player.get("army", {}).get("name"),
            }
            for f in SCORE_FIELDS:
                if f == "resultRecord":
                    player_out[f] = "".join([wl_to_str(i) for i in player.get(f)])
                else:
                    player_out[f] = player.get(f)
            all_players.append(player_out)
    print("num_dropped", num_dropped)
    print("num_has_army", num_has_army)
    print("num_players", len(all_players) - num_dropped)
    return all_players


def main():
    all_players = get_all_players()

    with open("players.csv", "w") as csvfile:
        fieldnames = all_players[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for player in all_players:
            writer.writerow(player)


if __name__ == "__main__":
    main()
