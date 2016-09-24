""" Basic logging plugin that makes really terrible assumptions in order to log the messages sent by the bot. """
from __future__ import unicode_literals
from client import slack_client as sc

import time
import os


LAST_CHANNEL = None

def process_message(data):
    log(data)

def process_non_type_text(data):
    log(data)

def log(data):
    global LAST_CHANNEL

    logdir = os.environ["SLACK_LOGDIR"]
    botname = os.environ["SLACK_BOTNAME"]

    users = {x["id"]: x["name"] for x in sc.api_call("users.list")["members"]}
    channels = {x["id"]: x["name"] for x in sc.api_call("channels.list")["channels"]}
    # Direct Messages
    ims = {x["id"]: users[x["user"]] for x in sc.api_call("im.list")["ims"]}
    # Multi User Direct Messages and Private Groups
    groups = {x["id"]: x["name"] for x in sc.api_call("groups.list")["groups"]}

    try:
        user = users[data['user']]
    except KeyError:
        user = "*%s*" % (botname,)

    try:
        if data['channel'][0] == "C":
            channel = "#%s" % (channels[data['channel']],)
        elif data['channel'][0] == "D":
            channel = ims[data['channel']]
        elif data['channel'][0] == "G":
            channel = groups[data['channel']]
        elif data['channel'][0] == "U":
            channel = users[data['channel']]
        LAST_CHANNEL = channel
    except KeyError:
        if data.get('channel'):
            channel = data['channel']
        else:
            channel = LAST_CHANNEL

    with open("%s/%s" % (logdir, channel), 'a') as logfile:
        logfile.write("[%s] %s: %s\n" % (time.ctime(int(float((data['ts'])))), user, data['text']))
    return
