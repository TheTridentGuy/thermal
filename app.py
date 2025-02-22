import datetime
import slack_sdk
import traceback
import flask
from slackeventsapi import SlackEventAdapter
from werkzeug.exceptions import HTTPException
from prisma import Prisma
import datetime


from config import bot_token, secret, main_channel, log_channel


client = slack_sdk.WebClient(token=bot_token)
app = flask.Flask(__name__)
events = SlackEventAdapter(secret, "/slack/events", app)
db = Prisma()
db.connect()


client.chat_postMessage(channel=main_channel, text=":information_source: bot is online")

# BEGIN DEBUG DATA
DEBUG = True
if DEBUG:
    if not db.scout.find_first() and not db.shift.find_first():
        db.shift.create(data={"shift_id": "A", "start": datetime.datetime.now(), "end": datetime.datetime.now()+datetime.timedelta(hours=8)})
        db.scout.create(data={"slack_id": "U08CGRSBY14", "shiftShift_id": "A"})
    else:
        db.shift.update(where={"shift_id": "A"}, data={"start": datetime.datetime.now(), "end": datetime.datetime.now()+datetime.timedelta(hours=8)})
# END DEBUG DATA

def send_dm(user, message):
    response = client.conversations_open(users=user)
    channel_id = response["channel"]["id"]
    client.chat_postMessage(channel=channel_id, text=message)


def log_message(message):
    client.chat_postMessage(channel=log_channel, text=message)


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
    log_message(f":x: [{datetime.datetime.now()}] {e.code} {e.description}"
                + (f"\n\n-- TRACEBACK: --\n\n{traceback.format_exc().strip()}" if e.code == 500 else "")
                + f"\n\n-- REQUEST: --\n\n{method} {http_version} {path}"
                + (f"\n\n-- REQUEST HEADERS: --\n\n{headers}" if headers else "")
                + (f"\n\n-- REQUEST DATA: --\n\n{data}" if data else ""))
    return ":x: Something went wrong, please try again later."


if __name__ == "__main__":
    app.run("localhost", port=8080, debug=True)
