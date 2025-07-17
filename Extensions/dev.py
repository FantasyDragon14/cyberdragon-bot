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
        await register_commands([559366749762617344, 1392809678106267726, 1301156458553147393, 811920496202743809]) #all dev guilds
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
        to_load = []
        for f in os.listdir(mypath):
            if os.path.isfile(os.path.join(mypath, f)) and not f.startswith("_"):
                to_load.append(f)
        to_load = [mypath+"."+name[:-3] for name in to_load]
        loaded = [extension for extension in client._extensions]
        
        logger.debug('currently loaded:')
        logger.debug(loaded)
        
        logger.info("reloading extensions:")
        to_remove = []
        for extension in loaded:
            if extension not in to_load:
                to_remove.append(extension)
        try:
            await client.unload_extensions(*to_remove)
        except: pass
        logger.info('reloading ' + str(to_load))
        try:
            await client.reload_extensions(*to_load)
            await ctx.respond("reloaded extensions")
        except:
            await ctx.respond("reload had some errors, see log")
            logger.error()
        for guild in await Data.get_guilds(bot):
            Data.assert_guild_config(guild.id)
        
        await client.sync_application_commands()
        logger.info("reload complete")

# loader.command(group)
async def register_commands(guild_ids:list = []):
    guilds_async = Data.bot.rest.fetch_my_guilds()
    guilds_it = []
    async for guild in guilds_async:
        guilds_it.append(int(guild.id))
    for i, guild_id in enumerate(guild_ids):
        if guild_id not in guilds_it:
            guild_ids.pop(i)
    loader.command(command=group, guilds=guild_ids)