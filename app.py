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


from config import bot_token, secret, log_channel, admin_channel, tba_key, team, match_scouts, match_scouting_shifts, events_to_scout, announcement_channel, setup_link


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

def send_schedule(scout_id):
    scout = match_scouts.get(scout_id)
    shifts = match_scouting_shifts.get(scout.get("shift"))
    shift_str = ""
    for shift in shifts:
        start_hour = int(shift[0].split(":")[0])
        start_min = int(shift[0].split(":")[1])
        end_hour = int(shift[1].split(":")[0])
        end_min = int(shift[1].split(":")[1])
        start = datetime.datetime.now().replace(hour=start_hour, minute=start_min)
        end = datetime.datetime.now().replace(hour=end_hour, minute=end_min)
        shift_str += f"*<!date^{int(start.timestamp())}^"+"{time}"+f"|(time)> - <!date^{int(end.timestamp())}^"+"{time}"+f"|(time)>*: {scout.get('alliance').capitalize()} {scout.get('team')}\n"
    blocks = bkt.match_scouting_schedule(shift_str, setup_link)
    send_dm(scout_id, "Your match scouting schedule is here.", blocks)

def send_all_schedules():
    for scout in match_scouts.keys():
        log_message(format_log(f"Sending schedule to <@{scout}>"))
        send_schedule(scout)

def process_match(match_data):
    full_match_data = tba.get_match(match_data.get("match_key"), tba_key)
    if f"frc{team}" in match_data.get("team_keys"):
        log_message(format_log(f"Upcoimg match for {team} at {match_data.get('event_key')}: {match_data.get('match_key')}, announcing..."))
        match_str = f"{full_match_data.get('comp_level').upper()}{full_match_data.get('match_number')}"
        blocks = bkt.match_announcement(team, match_str, full_match_data.get('predicted_time') if full_match_data.get(
            'predicted_time') else full_match_data.get('scheduled_time'))
        client.chat_postMessage(channel=announcement_channel, text=f"Match {match_str} is starting soon!", blocks=blocks)
    if match_data.get("event_key") in events_to_scout:
        predicted_start = datetime.datetime.fromtimestamp(match_data.get("predicted_time") if match_data.get("predicted_time") else match_data.get("scheduled_time"))
        log_message(format_log(f"Match {match_data.get('match_key')} at {match_data.get('event_key')} is starting soon, sending scouting reminders..."))
        for scout_id in match_scouts.keys():
            scout = match_scouts.get(scout_id)
            for shift in match_scouting_shifts.get(scout.get("shift")):
                shift_start = datetime.datetime.now().replace(hour=int(shift[0].split(":")[0]), minute=int(shift[0].split(":")[1]))
                shift_end = datetime.datetime.now().replace(hour=int(shift[1].split(":")[0]), minute=int(shift[1].split(":")[1]))
                if shift_start < predicted_start < shift_end:
                    send_scouting_reminder(scout_id, full_match_data)
                    break

def send_scouting_reminder(scout_id, full_match_data):
    scout = match_scouts.get(scout_id)
    alliance = full_match_data.get("alliances").get(scout.get("alliance"))
    team_key = alliance.get("team_keys")[scout.get("team")-1]
    team_num = team_key[3:]
    match_str = f"{full_match_data.get('comp_level').upper()}{full_match_data.get('match_number')}"
    alliance_member = f"{scout.get('alliance').capitalize()} {scout.get('team')}"
    blocks = bkt.scouting_reminder(match_str, team_num, alliance_member)
    log_message(format_log(f"Sending reminder to <@{scout_id}> to scout {team_num} ({alliance_member}) in {match_str}"))
    send_dm(scout_id, f"{match_str} is starting soon, get ready to scout {team_num} ({alliance_member})!", blocks)


@app.route("/commands/command", methods=["POST"])
def command():
    pass

@app.route("/commands/send_schedules", methods=["POST"])
def send_schedules():
    user = request.values.get("user_id")
    channel = request.values.get("channel_id")
    if channel == admin_channel:
        log_message(format_log(f"Sending schedule notifications as requested by <@{user}>."))
        send_all_schedules()
        client.chat_postMessage(channel=channel, text="Schedule notifications sent.")
        return ""
    else:
        return f":x: You need to run this command from <#{admin_channel}>."

@app.route("/commands/events_available", methods=["POST"])
def events_available():
    year = datetime.datetime.now().year
    event_data = tba.get_events(f"frc{team}", tba_key, year)
    message = bkt.event_report(event_data, team, year, events_to_scout)
    print(request.values)
    client.chat_postEphemeral(channel=request.values.get("channel_id"), text=f"Events for {team}: {','.join([event.get('name') for event in event_data])}", blocks=message, user=request.values.get("user_id"))
    return ""

@app.route("/webhooks/tba", methods=["POST"])
def tba_webhook():
    data = json.loads(request.data)
    log_message(format_log(f"Received TBA webhook: {data}"))
    if data.get("message_type") == "verification":
        message  = f"Received TBA webhook verification key: `{data.get('message_data').get('verification_key')}`"
        client.chat_postMessage(channel=admin_channel, text=message)
        log_message(format_log(message))
    elif data.get("message_type") == "upcoming_match":
        process_match(data.get("message_data"))
    elif data.get("message_type") == "ping":
        log_message(format_log("Received TBA webhook ping..."))
        client.chat_postMessage(channel=admin_channel, text=f"Recieved TBA webhook ping, webhook is working.")
    else:
        log_message(format_log(f"Unknown TBA webhook type: {data}"))
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
