#extension for dev commands

import os
import sys
import hikari
import lightbulb as commands
import asyncio
import logging
import Util.data as Data

class Loader(commands.Loader):
    async def remove_from_client(self, client: commands.Client) -> None:
        #unload / close db connections here?
        logger.info('Removing Dev Extension')
        return await super().remove_from_client(client)
    
    async def add_to_client(self, client:commands.Client) -> None:
        logger.info('adding Dev extension')
        await super().add_to_client(client)
        
loader = Loader()

logger = logging.getLogger("dev")

group = commands.Group('dev', 'collection of developer commands')

@group.register
class Restart_Bot(
    commands.SlashCommand,
    name="restart",
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
        
@group.register
class reload_ext(
    commands.SlashCommand,
    name="reload",
    description="reloads Extensions",
    hooks=[commands.prefab.owner_only],
    
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context, client:commands.Client, bot:hikari.GatewayBot) -> None:
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
            await ctx.respond("reloaded extensions")
        except: await ctx.respond("reload had some errors, see log")
        for guild in await Data.get_guilds(bot):
            Data.assert_guild_config(guild.id)
        
        await client.sync_application_commands()
        logger.info("reload complete")
        
# loader.command(group)
loader.command(group)