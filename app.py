import slack_sdk
import traceback
import json
import flask
from flask import request
from werkzeug.exceptions import HTTPException
import datetime
import tba
import block_kit_templates as bkt


from config import bot_token, log_channel, admin_channel, tba_key, team, events_to_scout, announcement_channel, setup_link, shift_schedule_file, state_file


client = slack_sdk.WebClient(token=bot_token)
app = flask.Flask(__name__)
state = None
match_scouts = {}
match_scouting_shifts = {}
scouting_enabled = True
state_shift_schedule_variant_key = "shift_schedule_variant"
state_scouting_enabled_key = "scouting_enabled"
shift_schedule_variants_key = "shift_schedule_variants"
scouts_key = "match_scouts"


class State:
    def __init__(self, file):
        self._file = file
        self.state = {}
        self.load()

    def load(self):
        try:
            with open(self._file, "r") as f:
                self.state = json.loads(f.read())
        except FileNotFoundError:
            self.state = {}

    def save(self):
        with open(self._file, "w") as f:
            f.write(json.dumps(self.state))

def load_shift_info():
    # TODO: add ability to change schedule variant, plus support for default variant
    global match_scouting_shifts, match_scouts, state, scouting_enabled
    state = State(state_file)
    try:
        with open(shift_schedule_file) as f:
            data = json.load(f)
            match_scouts = data.get(scouts_key)
            shift_schedule_variants = data.get(shift_schedule_variants_key)
            state_variant = state.state.get(state_shift_schedule_variant_key)
            scouting_enabled = state.state.get(state_scouting_enabled_key, True)
            if state_variant:
                active_variant = state_variant
            else:
                active_variant = list(shift_schedule_variants.keys())[0]
            state.state[state_scouting_enabled_key] = scouting_enabled
            state.state[state_shift_schedule_variant_key] = active_variant
            state.save()
            match_scouting_shifts = shift_schedule_variants.get(active_variant)
            blocks = bkt.config_message(scouting_enabled, active_variant, list(shift_schedule_variants.keys()))
            client.chat_postMessage(channel=admin_channel, text=f"Config loaded, scouting is {'enabled' if scouting_enabled else 'disabled'}, and the current shift schedule variant is *{active_variant}*", blocks=blocks)
    except Exception as e:
        log_message_warn(format_log_warn(f"Failed to load shift schedules, this is probably bad. Check <#{log_channel}> for details."))
        log_message_info(format_log_info(f"Error loading shift schedules from file: {e}"))
        return
    if not match_scouts:
        log_message_warn(format_log_warn("No scout data found in shift schedule file. This is probably bad."))
    if not match_scouting_shifts:
        log_message_warn(format_log_warn("No shift data found in shift schedule file. This is probably bad."))
    log_message_info(format_log_info(f"Scout data loaded from {shift_schedule_file}: {match_scouts}"))
    log_message_info(format_log_info(f"Shift data loaded from {shift_schedule_file}: {match_scouting_shifts}"))

def send_dm(user, text, blocks):
    response = client.conversations_open(users=user)
    channel_id = response["channel"]["id"]
    return client.chat_postMessage(channel=channel_id, text=text, blocks=blocks)

def log_message_info(message):
    client.chat_postMessage(channel=log_channel, text=message)

def log_message_warn(message):
    client.chat_postMessage(channel=admin_channel, text=message)

def format_log_info(message):
    return f":information_source: [{datetime.datetime.now()}] {message}"

def format_log_warn(message):
    return f":warning: [{datetime.datetime.now()}] :warning: WARNING :warning:\n{message}"

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
        log_message_info(format_log_info(f"Sending schedule to <@{scout}>"))
        send_schedule(scout)

def process_match(match_data):
    full_match_data = tba.get_match(match_data.get("match_key"), tba_key)
    if f"frc{team}" in match_data.get("team_keys"):
        log_message_info(format_log_info(
            f"Upcoimg match for {team} at {match_data.get('event_key')}: {match_data.get('match_key')}, announcing..."))
        match_str = f"{full_match_data.get('comp_level').upper()}{full_match_data.get('match_number')}"
        blocks = bkt.match_announcement(team, match_str, full_match_data.get('predicted_time') if full_match_data.get(
            'predicted_time') else full_match_data.get('scheduled_time'))
        client.chat_postMessage(channel=announcement_channel, text=f"Match {match_str} is starting soon!", blocks=blocks)
    if match_data.get("event_key") in events_to_scout:
        predicted_start = datetime.datetime.fromtimestamp(match_data.get("predicted_time") if match_data.get("predicted_time") else match_data.get("scheduled_time"))
        log_message_info(format_log_info(
            f"Match {match_data.get('match_key')} at {match_data.get('event_key')} is starting soon, sending scouting reminders..."))
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
    log_message_info(
        format_log_info(f"Sending reminder to <@{scout_id}> to scout {team_num} ({alliance_member}) in {match_str}"))
    send_dm(scout_id, f"{match_str} is starting soon, get ready to scout {team_num} ({alliance_member})!", blocks)

@app.route("/commands/command", methods=["POST"])
def command():
    pass

@app.route("/commands/send_schedules", methods=["POST"])
def send_schedules():
    user = request.values.get("user_id")
    channel = request.values.get("channel_id")
    if channel == admin_channel:
        log_message_info(format_log_info(f"Sending schedule notifications as requested by <@{user}>."))
        send_all_schedules()
        client.chat_postMessage(channel=channel, text="Schedule notifications sent.")
        return ""
    else:
        return f":x: You need to run this command from <#{admin_channel}>."

@app.route("/commands/how_we_doin", methods=["POST"])
def how_we_doin():
    event_data = tba.get_events(f"frc{team}", tba_key, datetime.datetime.now().year)
    for event in event_data:
        start = datetime.datetime.fromisoformat(event.get("start_date")).replace(hour=0, minute=0)
        end = datetime.datetime.fromisoformat(event.get("end_date")).replace(hour=23, minute=59)
        if start < datetime.datetime.now() < end:
            event_key = event.get("key")
            match_data = tba.get_matches_simple(f"frc{team}", event_key, tba_key)
            status = tba.get_status(f"frc{team}", event_key, tba_key)
            match_str = ""
            for match in match_data:
                match_str += f"*{match.get('comp_level').upper()}{match.get('match_number')}*: {datetime.datetime.fromtimestamp(match.get('time')).strftime('%H:%M')}\n"
            wins = status.get("qual", {}).get("ranking", {}).get("record", {}).get("wins", 0)
            losses = status.get("qual", {}).get("ranking", {}).get("record", {}).get("losses", 0)
            ties = status.get("qual", {}).get("ranking", {}).get("record", {}).get("ties", 0)
            rank = status.get("qual", {}).get("ranking", {}).get("rank", 0)
            blocks = bkt.match_report(event.get("name"), match_str, team, rank, wins, losses, ties)
            client.chat_postEphemeral(channel=request.values.get("channel_id"), text=f"Matches for {team} at {event.get('name')}. {team} is currently ranked #{rank} ({wins}-{losses}-{ties}).", blocks=blocks, user=request.values.get("user_id"))
            return ""
    return f":x: No ongoing events found for {team}."

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
    log_message_info(format_log_info(f"Received TBA webhook: {data}"))
    if data.get("message_type") == "verification":
        message  = f"Received TBA webhook verification key: `{data.get('message_data').get('verification_key')}`"
        client.chat_postMessage(channel=admin_channel, text=message)
        log_message_info(format_log_info(message))
    elif data.get("message_type") == "upcoming_match":
        process_match(data.get("message_data"))
    elif data.get("message_type") == "ping":
        log_message_info(format_log_info("Received TBA webhook ping..."))
        client.chat_postMessage(channel=admin_channel, text=f"Recieved TBA webhook ping, webhook is working.")
    else:
        log_message_info(format_log_info(f"Unknown TBA webhook type: {data}"))
    return ""

@app.errorhandler(HTTPException)
def handle_exception(e):
    headers = str(flask.request.headers).strip()
    data = flask.request.data.decode("utf-8").strip()
    method = flask.request.method
    path = flask.request.path
    http_version = flask.request.environ.get("SERVER_PROTOCOL", "HTTP/1.1")
    log_message_info(f":x: [{datetime.datetime.now()}] {e.code} {e.description}"
                     + (f"\n\n-- TRACEBACK: --\n\n{traceback.format_exc().strip()}" if e.code == 500 else "")
                     + f"\n\n-- REQUEST: --\n\n{method} {http_version} {path}"
                     + (f"\n\n-- REQUEST HEADERS: --\n\n{headers}" if headers else "")
                     + (f"\n\n-- REQUEST DATA: --\n\n{data}" if data else ""))
    return ":x: Something went wrong, please try again later."


load_shift_info()
log_message_info(format_log_info("App successfully initialized."))

if __name__ == "__main__":
    log_message_info(format_log_info("Starting server in __main__ block..."))
    app.run("localhost", port=8080, debug=True)
