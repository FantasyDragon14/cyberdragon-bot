"""Module for testing stuff
"""
import os
import sys
import hikari
import lightbulb as commands
import asyncio
import sqlite3
import logging

import Util.utils as Utils #this is my own module
import Util.data as Data

#from bot import dev

class CustomLoader(commands.Loader):
    async def remove_from_client(self, client: commands.Client) -> None:
        #unload / close db connections here?
        logger.info('Removing Testing Extension')
        return await super().remove_from_client(client)
    
    async def add_to_client(self, client:commands.Client) -> None:
        logger.info('adding testing extension')
        await register_commands() #all current joined guilds
        await super().add_to_client(client)

# loader = CustomLoader()
loader = CustomLoader()
logger = logging.getLogger("testing")

# db = sqlite3.connect(os.path.join(".", Util.data.folder_data, Util.data.folder_misc, "test.db"))

group = commands.Group('testing', 'all testing commands')

@group.register
class test(
    commands.SlashCommand,
    name="test",
    description="a test command",
    
    #hooks=[dev]
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context) -> None:
        logger.info('test command was invoked')
        logger.debug("test running")
        response = await ctx.respond(f"{ctx.member.mention}test running...", user_mentions=True)
        await asyncio.sleep(10)
        await ctx.edit_response(response, "test complete")
        logger.debug("test complete")

@group.register
class get_channel_info_CMD(
    commands.SlashCommand,
    name="channelsinfo",
    description="get info on all of a guilds channels",
    hooks=[commands.prefab.owner_only],
):
    @commands.invoke
    async def get_info(self, ctx:commands.Context) -> None:
        await ctx.defer()
        logger.info("Channelinfo:")
        msg = ""
        guild = ctx.member.get_guild()
        await asyncio.sleep(1)
        msg += str(guild) + ": " + str(type(guild)) + ", channels:"
        channels = guild.get_channels()
        msg += "\n" + str(channels) + "...\n"
        for channel in channels:
            msg += str(channel) + str(type(channel)) + str(channels[channel]) + str(type(channels[channel])) + "\n"
        logger.info(msg)
        # messages = Util.utils.split_message(msg)
        messages = [msg[:900]]
        await ctx.respond(messages[0])
        
@group.register
class HelloWorld(
    commands.SlashCommand,
    name="hello-world",
    description="Makes the bot say hello world"
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context) -> None:
        await ctx.respond("Hello World!")
        
class non_global_CMD(
    commands.SlashCommand,
    name="test-noglobal",
    description='to test non-global commands',
):
    @commands.invoke
    async def pong(self, ctx:commands.Context) -> None:
        await ctx.defer()
        await ctx.respond('non-globuli')
        
class guild_specific_CMD(
    commands.SlashCommand,
    name="test-guild",
    description='to test guild-specific commands',
):
    @commands.invoke
    async def pong(self, ctx:commands.Context) -> None:
        await ctx.defer()
        await ctx.respond('congrats: this guild is special!')
            
async def register_commands(guild_ids:list=[]):
    if len(guild_ids) < 1:
        guilds_it = Data.bot.rest.fetch_my_guilds()
        async for guild in guilds_it:
            guild_ids.append(guild.id)
    print(guild_ids)
    loader.command(command=group) #This works, but it's global
    
    loader.command(command=non_global_CMD, guilds=guild_ids) #trying to have a command for all guilds, but not global (ik i could use hooks to fail in DM, this is just for testing)
    loader.command(command=guild_specific_CMD, guilds=[559366749762617344]) #trying a command for only one guild
