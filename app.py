import datetime
import slack_sdk
import traceback
import json
import flask
from flask import request
from slackeventsapi import SlackEventAdapter
from werkzeug.exceptions import HTTPException
import datetime
import tba
import block_kit_templates as bkt


from config import bot_token, secret, log_channel, admin_channel, tba_key, team, scouts


client = slack_sdk.WebClient(token=bot_token)
app = flask.Flask(__name__)
events = SlackEventAdapter(secret, "/slack/events", app)


def send_dm(user, text, blocks):
    response = client.conversations_open(users=user)
    channel_id = response["channel"]["id"]
    return client.chat_postMessage(channel=channel_id, text=text, blocks=blocks)

def log_message(message):
    client.chat_postMessage(channel=log_channel, text=message)

def format_log(message):
    return f":information_source: [{datetime.datetime.now()}] {message}"

def send_shifts(scout_id):
    shifts = scouts.get(scout_id).get("shifts")
    blocks = bkt.greeting(shifts)
    send_dm(scout_id, "Your scouting shifts are here.", blocks)

def send_all_shifts():
    for scout in scouts.keys():
        send_shifts(scout)
send_all_shifts()

@app.route("/commands/command", methods=["POST"])
def command():
    pass

@app.route("/commands/events_available", methods=["POST"])
def events_available():
    year = datetime.datetime.now().year
    events = tba.get_events(team, tba_key, year)
    message = bkt.event_report(events, team, year)
    client.chat_postEphemeral(channel=request.values.get("channel"), text=f"Events for {team}: {','.join([event.get('name') for event in events])}", blocks=message, user=request.values.get("user_id"))
    return ""

@app.route("/webhooks/tba", methods=["POST"])
def tba_webhook():
    data = json.loads(request.data)
    if data.get("message_type") == "verification":
        message  = f"Received TBA webhook verification key: `{data.get('message_data').get('verification_key')}`"
        client.chat_postMessage(channel=admin_channel, text=message)
        log_message(format_log(message))
    return ""

@app.errorhandler(HTTPException)
def handle_exception(e):
    headers = str(flask.request.headers).strip()
    data = flask.request.data.decode("utf-8").strip()
    method = flask.request.method
    path = flask.request.path
    http_version = flask.request.environ.get("SERVER_PROTOCOL", "HTTP/1.1")
    log_message(f":x: [{datetime.datetime.now()}] {e.code} {e.description}"
                + (f"\n\n-- TRACEBACK: --\n\n{traceback.format_exc().strip()}" if e.code == 500 else "")
                + f"\n\n-- REQUEST: --\n\n{method} {http_version} {path}"
                + (f"\n\n-- REQUEST HEADERS: --\n\n{headers}" if headers else "")
                + (f"\n\n-- REQUEST DATA: --\n\n{data}" if data else ""))
    return ":x: Something went wrong, please try again later."



log_message(format_log("Server started"))



if __name__ == "__main__":
    app.run("localhost", port=8080, debug=True)
