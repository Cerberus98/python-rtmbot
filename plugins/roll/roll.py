from __future__ import unicode_literals
from client import slack_client as sc

import random
import re

crontable = []
outputs = []

USAGE = """```Usage: !roll [diceroll]
ex: !roll 3d6
    !roll 2d4-2
    !roll 10d4+10```"""

def roll(input_dice):
    r = re.match('^([0-9]+)\s*d\s*([0-9]+)\s*([-+\/*x])?\s*([0-9]+)?\s*$', input_dice)
    result = 0
    rolls = []
    try:
        dice     = int(r.group(1))
        sides    = int(r.group(2))
    except AttributeError:
        return "Unknown dice input: %s\n%s" % (input_dice, USAGE)
    try:
        mod_type = r.group(3)
        mod      = int(r.group(4))
    except AttributeError:
        mod_type = ""
        mod = ""
    except TypeError:
        mod_type = ""
        mod = ""
    old_dice = dice

    while dice > 0:
        dice_roll = random.randint(1, sides)
        rolls.append(dice_roll)
        result += dice_roll
        dice -= 1

    if mod_type == '+':
        result += mod
    if mod_type == '*' or mod_type == 'x':
        result *= mod
    if mod_type == '/':
        result /= mod

    result = "%dd%d%s%s: (%s)%s%s = %d" % (old_dice, sides, mod_type, mod, '+'.join(str(x) for x in rolls), mod_type, mod, result)

    return result


def process_message(data):
    text = data.get("text")

    users = {x["id"]: x["name"] for x in sc.api_call("users.list")["members"]}

    r = re.match('!roll (.*?)$', text)
    try:
        result = "%s: %s" % (users[data["user"]], roll(r.group(1)))
        outputs.append([data["channel"], result])
    except AttributeError:
        return
