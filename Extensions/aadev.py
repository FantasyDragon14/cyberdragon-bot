#extension for dev commands

import os
import sys
import hikari
import lightbulb as commands
import asyncio
import logging

loader = commands.Loader()

logger = logging.getLogger("dev")

@loader.command
class Restart_Bot(
    commands.SlashCommand,
    name="restart_completely",
    description="Restarts the bot completely for testing. needs dev privileges",
    hooks=[commands.prefab.owner_only],
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context, bot:hikari.GatewayBot) -> None:
        print("-------------------------------------------")
        print("\t\t\trestarting completely now!")
        print("-------------------------------------------")
        python = sys.executable
        await ctx.respond("restarting, done if I'm online again")
        #TODO: ability to edit this message to show the restart was successful
        os.execl(python, python, *sys.argv)
        
@loader.command
class reload_ext(
    commands.SlashCommand,
    name="reload_ext",
    description="reloads Extensions",
    hooks=[commands.prefab.owner_only],
    
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context, client:commands.Client) -> None:
        await ctx.defer()
        mypath = "Extensions"
        extensions = []
        for f in os.listdir(mypath):
            if os.path.isfile(os.path.join(mypath, f)) and not f.startswith("_"):
                extensions.append(f)
        logger.info("reloading extensions:")
        #extensions = [os.path.join(mypath, name) for name in extensions]
        extensions = [mypath+"."+name[:-3] for name in extensions]
        logger.info(extensions)
        try:
            await client.reload_extensions(*extensions)
            await ctx.respond("reloaded extensions, syncing commands")
        except: await ctx.respond("reload had some errors. syncing commands")
        
        await client.sync_application_commands()
        logger.info("reload complete")
        

#register a reload settings files command
#TODO 