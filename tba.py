import requests
import pprint
import datetime


gen_headers = lambda tba_key: {
    "X-TBA-Auth-Key": tba_key
}


def get_events(team, tba_key, year):
    headers = gen_headers(tba_key)
    url = f"https://www.thebluealliance.com/api/v3/team/{team}/events/{year}"
    return requests.get(url, headers=headers).json()

def get_match(match_key, tba_key):
    headers = gen_headers(tba_key)
    url = f"https://www.thebluealliance.com/api/v3/match/{match_key}"
    return requests.get(url, headers=headers).json()
