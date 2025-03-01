from datetime import datetime

def event_report(events, team, year, events_to_scout):
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Events for {team} in {year}:",
                "emoji": True
            }
        }
    ]
    events.sort(key=lambda x: datetime.fromisoformat(x.get("start_date")))
    for event in events:
        start = datetime.fromisoformat(event.get("start_date"))
        end = datetime.fromisoformat(event.get("end_date"))
        when = "Upcoming"
        if start < datetime.now() < end:
            when = "Live"
        elif end < datetime.now():
            when = "Past"
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*({when}) {start.strftime('%b %d')}-{end.strftime('%d') if start.month==end.month else end.strftime('%b %d')} - <{event.get('website')}|{event.get('name')}> ({event.get('key')}):*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{event.get('address')}"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Get Directions",
                        "emoji": True
                    },
                    "value": "click_me_123",
                    "url": f"{event.get('gmaps_url')}",
                    "action_id": "button-action"
                }
            }
        ])
    blocks.extend([
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Events set to be scouted: {', '.join(events_to_scout)}"
            }
        }
    ])
    return blocks

def match_scouting_schedule(shift_str):
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Your match scouting schedule for {datetime.now().strftime('%b %d')}:",
                "emoji": True
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": shift_str
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "You will be notified ~7 minutes before the start of your shifts, and match info will be provided."
            }
        }
    ]
    return blocks

def scouting_reminder(game, team, alliance_member):
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*You will scout {game}:* {team} ({alliance_member})"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "App Link",
                    "emoji": True
                },
                "value": "click_me_123",
                "url": "https://google.com",
                "action_id": "button-action"
            }
        }
    ]
    return blocks

def match_announcement(team, match_str, predicted_time):
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Upcoming match for {team} at {datetime.fromtimestamp(predicted_time).strftime('%b %d')}:",
                "emoji": True
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{match_str}*"
            }
        }
    ]
    return blocks
