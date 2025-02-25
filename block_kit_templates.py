from datetime import datetime

def event_report(events, team, year):
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
        if start < datetime.now() and end > datetime.now():
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
                    "text": f"*({when}) {start.strftime('%b %d')}-{end.strftime('%d') if start.month==end.month else end.strftime('%b %d')} - <{event.get('website')}|{event.get('name')}> (2025casf):*"
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
    return blocks

def greeting(shifts):
    blocks = [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": f"Your scouting shifts for {datetime.now().strftime('%b %d')}:",
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
				"text": f"{'\n'.join(['*'+shift.get('start').strftime('%I:%M %p')+'-'+shift.get('end').strftime('%I:%M %p')+'*' for shift in shifts])}"
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

def shift_message():
    blocks = [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Upcoming matches for you to scout:",
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
				"text": "*QM45:* 1678 (Red 3)"
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
