"""Module to set/manage the bots status/activity messages
other Modules can add to activities list (status.activities.append()) if they have their own activities
"""
import traceback
import hikari
import lightbulb as commands
import random, os, sys
import logging

class Loader(commands.Loader):
    async def remove_from_client(self, client: commands.Client) -> None:
        #unload / close db connections here?
        logger.info('Removing status Extension')
        return await super().remove_from_client(client)
    
    async def add_to_client(self, client:commands.Client) -> None:
        logger.info('adding status extension')
        # await register_commands()
        await super().add_to_client(client)
        
loader = Loader()
logger = logging.getLogger("status")

activities = [
    hikari.Activity(name="the code for changes", type= hikari.ActivityType.WATCHING),
    hikari.Activity(name="Testing", state="test", type= hikari.ActivityType.CUSTOM),
    hikari.Activity(name="I'm still under development uwu", state=">w<", type= hikari.ActivityType.CUSTOM),
    hikari.Activity(name="a popular youtube video...", state="such waow", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', type= hikari.ActivityType.STREAMING),
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
        hikari.Activity(name="a popular youtube video...", state="you definitely haven't seen this one before!", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', type= hikari.ActivityType.STREAMING),
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
    logger.debug("Trying to change status")
    act = random.choice(activities)
    stat = random.choice(status)
    try:
        await bot.update_presence(activity=act, status= stat)
        logger.debug("changed status")
    except:
        logger.debug("change failed. trying again next time")
