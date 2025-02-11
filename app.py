import requests
import datetime
import slack_sdk
import traceback
import flask
from flask import render_template
from slackeventsapi import SlackEventAdapter
import json
import pathlib
import gsheets
from pathlib import Path
from config import bot_token, secret, channel
from werkzeug.exceptions import HTTPException
import re


client = slack_sdk.WebClient(token=bot_token)
app = flask.Flask(__name__)
events = SlackEventAdapter(secret, "/slack/events", app)
data_file = Path(__file__).parent.resolve()/Path("data.json")
user_data = {}
if pathlib.Path(data_file).exists():
    user_data = json.load(open(data_file, "r"))


client.chat_postMessage(channel=channel, text=":information_source: bot is online")


def send_dm(user, message):
    response = client.conversations_open(users=user)
    channel_id = response["channel"]["id"]
    client.chat_postMessage(channel=channel_id, text=message)
send_dm("U06FG6G6SNL", "get scouting bitch")


def report(message):
    client.chat_postMessage(channel=channel, text=message)


@app.route("/commands/command", methods=["POST"])
def command():
    pass


@app.errorhandler(HTTPException)
def handle_exception(e):
    headers = str(flask.request.headers).strip()
    data = flask.request.data.decode("utf-8").strip()
    method = flask.request.method
    path = flask.request.path
    http_version = flask.request.environ.get("SERVER_PROTOCOL", "HTTP/1.1")
    report(f":x: [{datetime.datetime.now()}] {e.code} {e.description}"
           + (f"\n\n-- TRACEBACK: --\n\n{traceback.format_exc().strip()}" if e.code == 500 else "")
           + f"\n\n-- REQUEST: --\n\n{method} {http_version} {path}"
           + (f"\n\n-- REQUEST HEADERS: --\n\n{headers}" if headers else "")
           + (f"\n\n-- REQUEST DATA: --\n\n{data}" if data else ""))
    return ":x: Something went wrong, please try again later."


if __name__ == "__main__":
    pass  # app.run("localhost", port=8080, debug=True)
