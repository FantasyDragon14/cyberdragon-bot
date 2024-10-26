
from dotenv import load_dotenv
import hikari
import lightbulb as commands
from lightbulb import tasks
import random
import os
import Extensions

from Util import utils

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
)

bot = hikari.GatewayBot(token= token, intents= intents, logs= "DEBUG") #create bot
client = commands.client_from_app(bot) #create lightbulb client from bot to use for lightbulb stuff

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
    print("Changing bot status")
    act = random.choice(activities)
    stat = random.choice(status)
    await bot.update_presence(activity=act, status= stat)
    
#miru.install(bot) #if i should use miru

@bot.listen(hikari.StartingEvent) #execute before the bot connects to discord
async def on_starting(_: hikari.StartingEvent) -> None:
    # Load any extensions
    await client.load_extensions_from_package(Extensions)
    # Start the bot - make sure commands are synced properly
    await client.start()
    
@bot.listen(hikari.StartedEvent) #execute after the bot has started
async def on_started(_: hikari.StartedEvent) -> None:
    print("setting bot status")
    await bot.update_presence(activity= hikari.Activity(name="Testing", state="test", type= hikari.ActivityType.CUSTOM), status= hikari.presences.Status.DO_NOT_DISTURB)
    
@commands.hook(commands.ExecutionSteps.CHECKS)
async def dev(self, pl: commands.ExecutionPipeline, _: commands.Context) -> None:
    print("checking dev privileges of " + str(_.user.id))
    if _.user.id not in utils.dev_ids:
        raise RuntimeError("only devs can use this command")

@client.register
class reload_ext(
    commands.SlashCommand,
    name="reload_ext",
    description="reloads Extensions",
    hooks=[dev]
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context) -> None:
        await ctx.defer()
        print("reloading extensions")
        await client.reload_extensions()
        await ctx.respond("reloaded extensions")
        print("complete")
        
    
    

bot.run() #run the bot