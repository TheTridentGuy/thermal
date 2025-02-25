import datetime
import slack_sdk
import traceback
import flask
from slackeventsapi import SlackEventAdapter
from werkzeug.exceptions import HTTPException
from prisma import Prisma
import datetime
import tba
import block_kit_templates as bkt


from config import bot_token, secret, main_channel, log_channel, tba_key, team


client = slack_sdk.WebClient(token=bot_token)
app = flask.Flask(__name__)
events = SlackEventAdapter(secret, "/slack/events", app)
db = Prisma()
db.connect()


# BEGIN DEBUG DATA
DEBUG = True
if DEBUG:
    if not db.shift.find_first():
        db.shift.create(data={"shift_id": "A", "start": datetime.datetime.now(), "end": datetime.datetime.now()+datetime.timedelta(hours=8)})
    else:
        db.shift.update(where={"shift_id": "A"}, data={"start": datetime.datetime.now(), "end": datetime.datetime.now()+datetime.timedelta(hours=8)})
    if not db.scout.find_first():
        db.scout.create(data={"slack_id": "U06FG6G6SNL", "shifts": ["A"]})
    else:
        db.scout.update(where={"slack_id": "U06FG6G6SNL"}, data={"shifts": ["A"]})
# END DEBUG DATA

def send_dm(user, text, blocks):
    response = client.conversations_open(users=user)
    channel_id = response["channel"]["id"]
    return client.chat_postMessage(channel=channel_id, text=text, blocks=blocks)


def log_message(message):
    client.chat_postMessage(channel=log_channel, text=message)


@app.route("/commands/command", methods=["POST"])
def command():
    pass

def send_greeting(scout_id):
    print(scout_id)
    print(db.scout.find_first(where={"slack_id": scout_id}))
    print(db.scout.find_many())
    scout = db.scout.find_first(where={"slack_id": scout_id})
    print(scout.shifts)
    shifts = list(scout.shifts)
    message = bkt.greeting(shifts)
    send_dm(scout_id, "Here are your upcoming shifts:", message)
send_greeting("U06FG6G6SNL")

@app.route("/commands/events_available", methods=["POST"])
def events_available():
    year = datetime.datetime.now().year
    events = tba.get_events(team, tba_key, year)
    message = bkt.event_report(events, team, year)
    client.chat_postEphemeral(channel=main_channel, blocks=message, user="U06FG6G6SNL")
    return message
events_available()

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



log_message(f":information_source: [{datetime.datetime.now()}] App started successfully")



if __name__ == "__main__":
    app.run("localhost", port=8080, debug=True)
