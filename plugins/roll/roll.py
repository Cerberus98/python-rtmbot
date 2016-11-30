#FIXME: Please clean me up. I am so very, very messy.
from __future__ import unicode_literals
from client import slack_client as sc

import random
import re

outputs = []

USAGE = """```Usage: !roll [diceroll]
ex: !roll 3d6
    !roll 2d4-2
    !roll 10d4+10```"""

def roll(input_dice):
    r = re.match('^([bw])?([0-9]+)\s*d\s*([0-9]+)\s*([-+\/*x])?\s*([0-9]+)?\s*$', input_dice)
    try:
        dice  = int(r.group(2))
        sides = int(r.group(3))
    except AttributeError:
        return "Unknown dice input: %s\n%s" % (input_dice, USAGE)
    try:
        mod_type = r.group(4)
        mod      = int(r.group(5))
    except AttributeError:
        mod_type = ""
        mod = ""
    except TypeError:
        mod_type = ""
        mod = ""
    bestworst = r.group(1)
    if bestworst:
        (r1, r1s) = _roll(dice, sides, mod_type, mod)
        (r2, r2s) = _roll(dice, sides, mod_type, mod)
        if bestworst == "b":
            result = r1s if r1 > r2 else r2s
            return "b%s" % (result,)
        else:
            result = r1s if r1 < r2 else r2s
            return "w%s" % (result,)
    else:
        return _roll(dice, sides, mod_type, mod)

def _roll(dice, sides, mod_type, mod):
    result = 0
    rolls = []
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

    result_str = "%dd%d%s%s: (%s)%s%s = %d" % (old_dice, sides, mod_type, mod, '+'.join(str(x) for x in rolls), mod_type, mod, result)

    return (result, result_str)

def do_rolls(raw):
    test = re.match('^([bw])?([0-9]+)\s*d\s*([0-9]+)\s*([-+\/*x])?\s*([0-9]+)?\s*$', raw)
    regex = re.finditer('([+-])?(\d+d\d+)', raw)
    rolls = []
    result = 0
    result_str = ""

    for x in regex:
        arith = x.group(1) if x.group(1) is not None else '+'
        rolls.append((arith, x.group(2)))

    for y in rolls:
        (value, string) = roll(y[1])
        if y[0] == '+':
            result += value
        if y[0] == '-':
            result -= value
        if result_str == "":
            result_str = "(%s)" % (string,)
        else:
            result_str += " %s (%s)" % (y[0], string)

    try:
        m = re.match('^.*([-+\/*x])(\d+)$', raw)
        if m.group(1) == '+':
            result += int(m.group(2))
        if m.group(1) == '-':
            result -= int(m.group(2))
        if m.group(1) == '*' or m.group(1) == 'x':
            result *= int(m.group(2))
        if m.group(1) == '/':
            result /= int(m.group(2))
        result_str += " %s %s" % (m.group(1), m.group(2))
    except AttributeError:
        pass

    result_str = "*%d* = %s" % (result, result_str)
    return (result, result_str)

def process_message(data):
    text = data.get("text")

    users = {x["id"]: x["name"] for x in sc.api_call("users.list")["members"]}

    r = re.match('^(.*)?!roll\s*(.*?)$', text, re.IGNORECASE)
    try:
        result = "%s: %s" % (users[data["user"]], do_rolls( r.group(2) )[1] )
        outputs.append([data["channel"], result])
    except AttributeError:
        return
