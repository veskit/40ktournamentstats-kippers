import os
import bcp
import pygsheets

bcp = bcp.BcpCache()
client = pygsheets.authorize(service_account_env_var="GSHEETS_SERVICE_ACCOUNT")


def fetch_bcp_data(event_id):
    players = bcp.fetch_players_from_event(event_id)
    pairings = bcp.fetch_pairings_for_event(event_id)

    players = sorted(
        players,
        key=lambda x: (x.get("numWins", 0), x.get("battlePoints", 0)),
        reverse=True,
    )

    # Match up pairings with players
    for player in players:
        player_id = player["userId"]
        player_pairings = []

        # Find pairings for player
        for pairing in pairings:
            if player_id == pairing.get("player1", {}).get(
                "userId", None
            ) or player_id == pairing.get("player2", {}).get("userId", None):
                player_pairings.append(pairing)

        player["pairings"] = sorted(player_pairings, key=lambda x: x["round"])

    return players, pairings


def update_gsheet_with_roster(roster):
    sheet = client.open_by_url(
        f"https://docs.google.com/spreadsheets/d/{os.environv['SHEET_URL']}/edit?usp=sharing"
    )
    worksheet = sheet.sheet1
    updated_values = []
    # Name	Email	Faction	Battle Points	Wins	Battle Points SoS	Wins Extended SoS	Dropped	Opponent 1	Opponent 2	Opponent 3
    ranking = 1
    for player in roster:
        row = [
            f"{player['firstName']} {player['lastName']}",
            player.get("army", {}).get("name", "Unknown"),
            player.get("battlePoints", 0),
            player.get("numWins", 0),
            player.get("FFGBattlePointsSoS", 0),
            player.get("extendedNumWinsSoS", 0),
        ]
        for pairing in player.get("pairings", []):
            player1 = pairing.get("player1", None)
            player2 = pairing.get("player2", None)
            if player1 is None or player2 is None:
                row.append("BYE")
            elif player1.get("userId", None) == player.get("userId", None):
                row.append(
                    f"{player2.get('firstName', '')} {player2.get('lastName', '')}"
                )
            elif player2.get("userId", None) == player.get("userId", None):
                row.append(
                    f"{player1.get('firstName', '')} {player1.get('lastName', '')}"
                )
            else:
                row.append("???")
        updated_values.append(row)
        ranking += 1

    worksheet.update_values("A2", updated_values)


def main():
    event_id = "ipqL1rmDYd"
    players, pairings = fetch_bcp_data(event_id)
    print(f"Got {len(players)} players")
    update_gsheet_with_roster(players)


main()
