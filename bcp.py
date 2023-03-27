import os
from dataclasses import dataclass
import requests


BCP_BASE_URL = "https://lrs9glzzsf.execute-api.us-east-1.amazonaws.com/prod"
BCP_AUTH_CLIENT_ID = "6avfri6v9tgfe6fonujq07eu9c"
BCP_ACCESS_TOKEN = ""
BCP_ID_TOKEN = ""


class BcpCache:
    def __init__(self):
        self.access_token = None
        self.id_token = None

        self.cache = {}

        self.event_list = None
        self.event_list_time = None

    def login_to_bcp(self, username: str, password: str):
        print("Grabbing BCP auth token")
        url = "https://cognito-idp.us-east-1.amazonaws.com"
        payload = {
            "AuthFlow": "USER_PASSWORD_AUTH",
            "ClientId": BCP_AUTH_CLIENT_ID,
            "AuthParameters": {"USERNAME": username, "PASSWORD": password},
            "ClientMetadata": {},
        }
        headers = {
            "Content-Type": "application/x-amz-json-1.1",
            "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth",
        }
        response = requests.post(url, json=payload, headers=headers)
        body = response.json()
        auth_results = body["AuthenticationResult"]
        self.access_token = auth_results["AccessToken"]
        self.id_token = auth_results["IdToken"]

        # Fetch attributes
        # url = https://cognito-idp.us-east-1.amazonaws.com/

    def fetch_from_bcp(self, url: str):
        # if not self.access_token:
        #     self.login_to_bcp(os.environ["BCP_USERNAME"], os.environ["BCP_PASSWORD"])

        url = f"{BCP_BASE_URL}/{url}"
        if url in self.cache:
            return self.cache[url]
        # headers = {"Authorization": self.id_token}
        headers = {}
        response = requests.get(url, headers=headers)
        body = response.json()
        if response.ok:
            self.cache[url] = body
        else:
            print("Response not okay", url, response.text)
        return body

    def fetch_event_metadata(self, event_id: str):
        return self.fetch_from_bcp(
            f'events/{event_id}?inclPlayer=true&inclMetrics=true&userId={os.environ["BCP_USER_ID"]}'
        )

    def fetch_players_from_event(self, event_id: str):
        return self.fetch_from_bcp(
            f"players?eventId={event_id}&inclEvent=false&inclMetrics=true&inclArmies=true&inclTeams=true&limit=5000&metrics=[%22resultRecord%22,%22record%22,%22numWins%22,%22battlePoints%22,%22WHArmyPoints%22,%22numWinsSoS%22,%22FFGBattlePointsSoS%22,%22mfSwissPoints%22,%22pathToVictory%22,%22mfStrengthOfSchedule%22,%22marginOfVictory%22,%22extendedNumWinsSoS%22,%22extendedFFGBattlePointsSoS%22,%22_id%22]"
        )

    def fetch_pairings_for_event(self, event_id: str):
        return self.fetch_from_bcp(
            f"pairings?eventId={event_id}&sortField=round&smallGame=true"
        )
