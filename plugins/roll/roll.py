from __future__ import unicode_literals
from client import slack_client as sc

import random
import re

outputs = []

USAGE = """```Usage: !roll [diceroll]
ex: !roll 3d6
    !roll 2d4-2
    !roll 10d4+1d6-1d8+2```"""

def roll(input_dice):
    r = re.match('^([bw])?([0-9]+)\s*d\s*([0-9]+)$', input_dice)
    dice  = int(r.group(2))
    sides = int(r.group(3))
    bestworst = r.group(1)
    if bestworst:
        (r1, r1s) = _roll(dice, sides)
        (r2, r2s) = _roll(dice, sides)
        (val, s) = (None, None)
        if bestworst == "b":
            if r1 > r2:
                val = r1
                s = "(%s) > ~(%s)~" % (r1s, r2s)
            else:
                val = r2
                s = "(%s) > ~(%s)~" % (r2s, r1s)
        else:
            if r1 < r2:
                val = r1
                s = "(%s) < ~(%s)~" % (r1s, r2s)
            else:
                val = r2
                s = "(%s) < ~(%s)~" % (r2s, r1s)
        return (val, s)
    else:
        return _roll(dice, sides)

def _roll(dice, sides):
    result = 0
    rolls = []
    old_dice = dice
    while dice > 0:
        dice_roll = random.randint(1, sides)
        rolls.append(dice_roll)
        result += dice_roll
        dice -= 1

    result_str = "%dd%d: (%s) = %d" % (old_dice, sides, '+'.join(str(x) for x in rolls), result)

    return (result, result_str)

def do_rolls(raw):
    test = re.match("""
        ^
            (
                \s*([+-])?\s*
                \s*([bw])?\s*
                \s*(\d+d\d+)\s*
            )+\s*
            (
                \s*([-+\/*x])?
                \s*([0-9]+)?\s*
            )?
        $""", raw, re.VERBOSE)
    regex = re.finditer('([+-])?([bw]?\d+d\d+)', raw)
    rolls = []
    result = 0
    result_str = ""

    if test is None:
        return (None, "Unknown roll: %s\n%s" % (raw, USAGE), None)

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
            if y[0] == '-':
                result_str = "-%s" % (result_str,)
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

    result_str = "%s = *%d*" % (result_str, result)
    return (result, result_str)

def process_message(data):
    text = data.get("text")

    users = {x["id"]: x["name"] for x in sc.api_call("users.list")["members"]}

    r = re.match('^(.*)?!roll\s*(.*?)$', text, re.IGNORECASE)
    result = "%s: %s" % (users[data["user"]], do_rolls( r.group(2) )[1] )
    outputs.append([data["channel"], result])
