#!/usr/bin/env python3

"""
Usage: python3 pomodoro.py <timer_type> <timer_action>

Arguments:
- timer_type: The type of timer to control (pomodoro, short-break, long-break)
- timer_action: The action to perform on the timer (start, pause, resume, skip)
"""
from requests import post
import syslog
import json
import sys
import os

# Read token and url from ~/.PomodoroHomeAssistant JSON file
with open(os.path.expanduser("~/.PomodoroHomeAssistant")) as f:
    config = json.load(f)
    TOKEN = config["token"]
    url = config["url"]

# Check if token and url are valid
if not TOKEN:
    # log to syslog and raise exception
    msg = "Missing token"
    syslog.syslog(syslog.LOG_ERR, msg)
    raise Exception(msg)
if not url:
    # log to syslog and raise exception
    msg = "Missing url"
    syslog.syslog(syslog.LOG_ERR, msg)
    raise Exception(msg)

# Define a mapping of program arguments to entity_id values
argument_mapping = {
    "pomodoro": {
        "start": "scene.pomodoro_enabled",
        "pause": "scene.pomodoro_suspended",
        "resume": "scene.pomodoro_enabled",
        "skip": "scene.normal",
    },
    "short-break": {
        "start": "scene.pomodoro_pause_short",
        "pause": "scene.pomodoro_suspended",
        "resume": "scene.pomodoro_pause_short",
        "skip": "scene.normal",
    },
    "long-break": {
        "start": "scene.pomodoro_pause_long",
        "pause": "scene.pomodoro_suspended",
        "resume": "scene.pomodoro_pause_long",
        "skip": "scene.normal",
    },
}

url = f"{url}/api/services/scene/turn_on"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "content-type": "application/json",
}

# check if arguments are valid
if sys.argv[1] not in argument_mapping:
    raise "Invalid program argument"
if sys.argv[2] not in argument_mapping[sys.argv[1]]:
    # check if arguments are valid
    if sys.argv[1] not in argument_mapping:
        msg = "Invalid program argument: " + sys.argv[1]
        syslog.syslog(syslog.LOG_ERR, msg)
        raise Exception(msg)
    if sys.argv[2] not in argument_mapping[sys.argv[1]]:
        msg = "Invalid program argument: "+ sys.argv[2]
        syslog.syslog(syslog.LOG_ERR, msg)
        raise Exception(msg)

# Set the entity_id value from the argument mapping
data = {}
data["entity_id"] = argument_mapping[sys.argv[1]][sys.argv[2]]

syslog.syslog(syslog.LOG_INFO, f"{sys.argv[1:]} --> {data}\n")

# Send the request
response = post(url, headers=headers, json=data)
print(response.text)
