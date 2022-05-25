import os
from html.parser import HTMLParser
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


BCP_BASE_URL = 'https://lrs9glzzsf.execute-api.us-east-1.amazonaws.com/prod'
BCP_AUTH_CLIENT_ID = '6avfri6v9tgfe6fonujq07eu9c'
BCP_ACCESS_TOKEN = ''
BCP_ID_TOKEN = ''


@dataclass
class ArmyList:
    name: str
    event: str
    list: str


def get_army_list_text_from_html(html) -> str:
    bs = BeautifulSoup(html.replace('<br>', '\n'), features="html.parser")
    army_list = bs.find(class_='list')
    return army_list.get_text()


class BcpCache:
    def __init__(self):
        self.access_token = None
        self.id_token = None

        self.cache = {}

        self.event_list = None
        self.event_list_time = None

    def login_to_bcp(self, username: str, password: str):
        print('Grabbing BCP auth token')
        url = 'https://cognito-idp.us-east-1.amazonaws.com'
        payload = {
            "AuthFlow": "USER_PASSWORD_AUTH",
            "ClientId": BCP_AUTH_CLIENT_ID,
            "AuthParameters": {"USERNAME": username, "PASSWORD": password},
            "ClientMetadata": {}
        }
        headers = {
            "Content-Type": 'application/x-amz-json-1.1',
            "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth",
        }
        response = requests.post(url, json=payload, headers=headers)
        body = response.json()
        auth_results = body['AuthenticationResult']
        self.access_token = auth_results['AccessToken']
        self.id_token = auth_results['IdToken']

        # Fetch attributes
        # url = https://cognito-idp.us-east-1.amazonaws.com/

    def fetch_from_bcp(self, url: str):
        if not self.access_token:
            self.login_to_bcp(
                os.environ['BCP_USERNAME'], os.environ['BCP_PASSWORD'])

        url = f'{BCP_BASE_URL}/{url}'
        if url in self.cache:
            return self.cache[url]
        response = requests.get(
            url, headers={'Authorization': self.id_token})
        body = response.json()
        if response.ok:
            self.cache[url] = body
        else:
            print('Response not okay', url, response.text)
        return body

    def fetch_event_metadata(self, event_id: str):
        return self.fetch_from_bcp(f'events/{event_id}?inclPlayer=true&inclMetrics=true&userId={os.environ["BCP_USER_ID"]}')

    def fetch_players_from_event(self, event_id: str):
        return self.fetch_from_bcp(f"players?eventId={event_id}&inclEvent=false&inclMetrics=true&inclArmies=true&inclTeams=true&limit=500&metrics=[%22resultRecord%22,%22record%22,%22numWins%22,%22battlePoints%22,%22WHArmyPoints%22,%22numWinsSoS%22,%22FFGBattlePointsSoS%22,%22mfSwissPoints%22,%22pathToVictory%22,%22mfStrengthOfSchedule%22,%22marginOfVictory%22,%22extendedNumWinsSoS%22,%22extendedFFGBattlePointsSoS%22,%22_id%22]")

    def fetch_list_for_player(self, army_list_id: str):
        response = self.fetch_from_bcp(
            f"armylists/{army_list_id}?inclList=true")
        if 'armyListHTML' not in response:
            print(f'armyListHTML not in army list response {army_list_id}')
            return None
        return get_army_list_text_from_html(response['armyListHTML'])

    def fetch_event_list_for_player(self, event_name: str, player_name: str) -> list[ArmyList]:
        self.refresh_event_list()
        filtered_events = filter(
            lambda e: event_name.lower() in e['name'].lower(), self.event_list)
        armies = []

        num_events = 0
        hidden_lists = 0
        for event in filtered_events:
            num_events += 1
            players = self.fetch_players_from_event(event['eventObjId'])
            for player in players:
                full_name = f"{player['firstName'].lower()} {player['lastName'].lower()}"
                lower_name = player_name.lower()
                if lower_name in full_name:
                    army_list_id = player['armyListId']
                    list = self.fetch_list_for_player(army_list_id)
                    if type(list) == str:
                        armies.append(ArmyList(
                            name=f"{player['firstName']} {player['lastName']}",
                            event=event['name'],
                            list=list,
                        ))
                    else:
                        hidden_lists += 1
                        continue

        return armies, num_events, hidden_lists

    def fetch_pairings_for_event(self, event_id: str):
        return self.fetch_from_bcp(f'pairings?eventId={event_id}&sortField=round&smallGame=true')

    def refresh_event_list(self, force_refresh=False):
        needs_refresh = force_refresh or self.event_list == None
        if not needs_refresh:
            return
        start_date = '2022-01-01'
        end_date = '2023-01-1'
        event_list = self.fetch_from_bcp(
            f'eventlistings?startDate={start_date}&endDate={end_date}&gameType=1')
        filter(lambda e: e.get('gameSystemName')
               == 'Warhammer 40k', event_list)
        self.event_list = event_list


# if __name__ == '__main__':
#     bcp = BcpCache()
#     bcp.fetch_event_list_for_player(
#         "US Open Seattle Warhammer 40,000 Grand Tournament", "Patrick Owens")
