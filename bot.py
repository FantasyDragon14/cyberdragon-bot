
import traceback
from dotenv import load_dotenv
import hikari
import lightbulb as commands
from lightbulb import tasks
import random
import os
from Util import data
from Util import utils
import Extensions

import Extensions.activityroles
import Extensions.testing

# Unix optimizations
# https://github.com/hikari-py/hikari#uvloop
if os.name != "nt":
    import uvloop

    uvloop.install()

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

intents = (
    hikari.Intents.GUILDS  # limbo
    | hikari.Intents.GUILD_MEMBERS  # limbo
    | hikari.Intents.GUILD_MESSAGES  # activity
    | hikari.Intents.GUILD_MESSAGE_TYPING  # activity
    | hikari.Intents.GUILD_VOICE_STATES  # activity
    | hikari.Intents.MESSAGE_CONTENT

    | hikari.Intents.ALL_DMS
)

bot = hikari.GatewayBot(token= token, intents= intents, logs= "DEBUG") #create bot.  logs= "DEBUG" | "TRACE_HIKARI"
client = commands.client_from_app(bot) #create lightbulb client from bot to use for lightbulb stuff
bot.subscribe(hikari.StartingEvent, client.start)

activities = [
    hikari.Activity(name="the code for changes", type= hikari.ActivityType.WATCHING),
    hikari.Activity(name="Testing", state="test", type= hikari.ActivityType.CUSTOM)
]

status = [
    hikari.presences.Status.DO_NOT_DISTURB
]

#tasks provided by lightbulb
#change the bots status every s=60 / m=1 minute
@client.task(commands.uniformtrigger(minutes=1))
async def bot_status():
    print("Trying to change status")
    act = random.choice(activities)
    stat = random.choice(status)
    try:
        await bot.update_presence(activity=act, status= stat)
        print("changed status")
    except:
        traceback.print_exception()
        print("trying again later")

    
#miru.install(bot) #if i should use miru

@bot.listen(hikari.StartingEvent) #execute before the bot connects to discord
async def on_starting(_: hikari.StartingEvent) -> None:
    # Load any extensions
    await client.load_extensions_from_package(Extensions)
    print("loaded Extensions, starting client:")
    # Start the bot - make sure commands are synced properly
    await client.start()
    print("started client")
    
@bot.listen(hikari.StartedEvent) #execute after the bot has started
async def on_started(_: hikari.StartedEvent) -> None:
    print("setting bot status")
    await bot.update_presence(activity= hikari.Activity(name="Testing", state="test", type= hikari.ActivityType.CUSTOM), status= hikari.presences.Status.DO_NOT_DISTURB)
    await client.sync_application_commands()
    
@commands.hook(commands.ExecutionSteps.CHECKS)
async def dev(self, pl: commands.ExecutionPipeline, _: commands.Context) -> None:
    print("checking dev privileges of " + str(_.user.id))
    if _.user.id not in utils.dev_ids:
        raise RuntimeError("only devs can use this command")

#register a reload-extensions command
@client.register
class reload_ext(
    commands.SlashCommand,
    name="reload_ext",
    description="reloads Extensions",
    hooks=[dev],
    
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context) -> None:
        await ctx.defer()
        mypath = "Extensions"
        extensions = []
        for f in os.listdir(mypath):
            if os.path.isfile(os.path.join(mypath, f)) and not f.startswith("_"):
                extensions.append(f)
        print("reloading extensions:")
        #extensions = [os.path.join(mypath, name) for name in extensions]
        extensions = [mypath+"."+name[:-3] for name in extensions]
        print(extensions)
        await client.reload_extensions(*extensions) 
        await ctx.respond("reloaded extensions, syncing commands")
        await client.sync_application_commands()
        print("complete")

#register a reload settings files command
#TODO 
        
bot.run() #run the bot