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