"""Module to set/manage the bots status/activity messages
other Modules can add to activities list (status.activities.append()) if they have their own activities
"""
import traceback
import hikari
import lightbulb as commands
import random, os, sys

loader = commands.Loader()

activities = [
    hikari.Activity(name="the code for changes", type= hikari.ActivityType.WATCHING),
    hikari.Activity(name="Testing", state="test", type= hikari.ActivityType.CUSTOM),
    hikari.Activity(name="I'm still under development uwu", state="your mom x3", type= hikari.ActivityType.CUSTOM),
    hikari.Activity(name="a popular youtube video...", state="your mom x3", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', type= hikari.ActivityType.STREAMING),
]
status = [
    hikari.presences.Status.DO_NOT_DISTURB
]

mode = "testing"
statusswitchminutes = 1
try:
    mode = sys.argv[1]
except:
    pass
mode = mode.lower()
if mode == "guardian":
    activities = [
        hikari.Activity(name="Guarding the Den (Discord Server)", type=hikari.ActivityType.CUSTOM),
        hikari.Activity(name="you yap", type= hikari.ActivityType.WATCHING),
        hikari.Activity(name="a popular youtube video...", state="gottem", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', type= hikari.ActivityType.STREAMING),
        hikari.Activity(name="flying in circles", type=hikari.ActivityType.CUSTOM),
        hikari.Activity(name="Definitely not sleeping", type=hikari.ActivityType.CUSTOM),
        hikari.Activity(name="Being Alert", type=hikari.ActivityType.CUSTOM),
        hikari.Activity(name="I am not distractable by petting :}", type=hikari.ActivityType.CUSTOM),
        hikari.Activity(name="with subroutines", type=hikari.ActivityType.PLAYING),
        hikari.Activity(name="Board", type=hikari.ActivityType.CUSTOM),
        hikari.Activity(name="the dragon 🐉", type=hikari.ActivityType.CUSTOM),
    ]
    status = [
        hikari.presences.Status.ONLINE,
    ]
    statusswitchminutes = 5

@loader.task(commands.uniformtrigger(minutes=statusswitchminutes), max_failures=-1, auto_start=True)
async def bot_status(bot:hikari.GatewayBot):
    if mode == "testing": print("Trying to change status")
    act = random.choice(activities)
    stat = random.choice(status)
    try:
        await bot.update_presence(activity=act, status= stat)
        if mode == "testing": print("changed status")
    except:
        if mode == "testing":
            traceback.print_exception()
            print("trying again later")
