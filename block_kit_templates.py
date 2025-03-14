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

def match_scouting_schedule(shift_str, setup_link):
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
        },
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*Please make sure you're signed into the scouting app!*"
			},
			"accessory": {
				"type": "button",
				"text": {
					"type": "plain_text",
					"text": "Go to scouting app",
					"emoji": True
				},
				"value": "click_me_123",
				"url": setup_link,
				"action_id": "button-action"
			}
		}
    ]
    return blocks

def scouting_reminder(game, team, alliance_member, app_link):
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Get ready scout {team} ({alliance_member}) in {game}*"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "App Link",
                    "emoji": True
                },
                "value": "click_me_123",
                "url": app_link,
                "action_id": "button-action"
            }
        }
    ]
    return blocks

def match_announcement(team, match_str, predicted_time):
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<!here> Upcoming match for {team} at {datetime.fromtimestamp(predicted_time).strftime('%b %d')}:*"
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
        },
		{
			"type": "divider"
		},
		{
			"type": "section",
			"text": {
				"type": "mrkdwn",
				"text": "*PIT CREW: Our robot should be in queue.*"
			}
		}
    ]
    return blocks

def match_report(event_name, match_str, team, ranking, wins, losses, ties):
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Matches for {team} at {event_name}",
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
                "text": f"{match_str}"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{team}* is currently ranked #{ranking} with a record of {wins}-{losses}-{ties} (W-L-T) in qualification matches."
            }
        }
    ]
    return blocks

def config_message(scouting_enabled, current_variant, available_variants):
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Configuration Loaded:*"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":white_check_mark: Scouting is enabled, scouting notifications will be sent out automatically." if scouting_enabled else ":x: Scouting is disabled, scouting notifications will not be sent."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f":information_source: Current schedule variant is *{current_variant}*."
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"Available schedule variants: {', '.join(['*'+variant+'*' for variant in available_variants])}"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"[{datetime.now().strftime('%d-%m-%Y %H:%M')}]"
            }
        }
    ]
    return blocks
