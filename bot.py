"""
guardian mode for normal deployment (first arg)
testing mode for testing
"""
import traceback
from dotenv import load_dotenv
import hikari
import lightbulb as commands
from lightbulb import tasks
import random
import os
import sys
from Util import data
from Util import utils
import Extensions
import logging

# Unix optimizations
# https://github.com/hikari-py/hikari#uvloop
if os.name != "nt":
    import uvloop

    uvloop.install()

load_dotenv()

#change between Development and deployment version

mode = "testing"
loglevel = "DEBUG"
logger = None
try:
    mode = sys.argv[1]
except:
    pass
mode = mode.lower()
if mode == "guardian":
    token = os.getenv("DISCORD_TOKEN")
    loglevel = "INFO"
if mode == "testing":
    print('testing mode')
    token = os.getenv("DISCORD_TESTING")


# intents = (
    #     hikari.Intents.GUILDS  # limbo
    #     | hikari.Intents.GUILD_MEMBERS  # limbo
    #     | hikari.Intents.GUILD_MESSAGES  # activity
    #     | hikari.Intents.GUILD_MESSAGE_TYPING  # activity
    #     | hikari.Intents.GUILD_VOICE_STATES  # activity
    #     | hikari.Intents.MESSAGE_CONTENT
    #     | hikari.Intents.
    #     | hikari.Intents.ALL_DMS
    # )
intents = hikari.Intents.ALL
bot = hikari.GatewayBot(token= token, intents= intents, logs= loglevel) #create bot.  logs= "DEBUG" | "TRACE_HIKARI"
client = commands.client_from_app(bot) #create lightbulb client from bot to use for lightbulb stuff
bot.subscribe(hikari.StartingEvent, client.start)

#miru.install(bot) #if i should use miru

@bot.listen(hikari.StartingEvent) #execute before the bot connects to discord
async def on_starting(_: hikari.StartingEvent) -> None:
    logger = logging.getLogger("main")
    # Load any extensions
    await client.load_extensions_from_package(Extensions)
    logger.info("loaded Extensions, starting client:")
    # Start the bot - make sure commands are synced properly
    await client.start()
    logger.info("started client")

@bot.listen(hikari.StartedEvent) #execute after the bot has started
async def on_started(_: hikari.StartedEvent) -> None:
    logger = logging.getLogger("main")
    guilds = bot.rest.fetch_my_guilds()
    await data.check_guild_data(guilds)
    logger.info("### current guilds:")
    async for item in bot.rest.fetch_my_guilds():
        logger.info("### " + str(item))
    
    logger.info("setting bot status")
    await bot.update_presence(activity= hikari.Activity(name="Waking up", state="i just woke up", type= hikari.ActivityType.CUSTOM), status= hikari.presences.Status.IDLE)
    await client.sync_application_commands()
    logger.info("started completely")
    
@bot.listen(hikari.GuildJoinEvent)
async def on_new_join(event: hikari.GuildJoinEvent) -> None:
    data.check_guild_data([event.guild_id])

        
bot.run() #run the bot