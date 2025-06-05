"""Module for testing stuff
"""
import os
import sys
import hikari
import lightbulb as commands
import asyncio
import sqlite3

import Util

#from bot import dev

class CustomLoader(commands.Loader):
    pass
    async def remove_from_client(self, client: commands.Client) -> None:
        #unload / close db connections here?
        return await super().remove_from_client(client)


loader = commands.Loader()

db = sqlite3.connect(os.path.join(".", Util.data.folder_data, Util.data.folder_misc, "test.db"))

@loader.command
class test(
    commands.SlashCommand,
    name="test",
    description="a test command",
    
    #hooks=[dev]
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context) -> None:
        print("test running")
        response = await ctx.respond(f"{ctx.member.mention}test running...", user_mentions=True)
        await asyncio.sleep(10)
        await ctx.edit_response(response, "test complete")
        print("test complete")


@loader.command
class HelloWorld(
    commands.SlashCommand,
    name="hello-world",
    description="Makes the bot say hello world"
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context) -> None:
        await ctx.respond("Hello World!")

@loader.command
class get_channel_info_CMD(
    commands.SlashCommand,
    name="channelsinfo",
    description="get info on all of a guilds channels",
    hooks=[commands.prefab.owner_only],
):
    @commands.invoke
    async def get_info(self, ctx:commands.Context) -> None:
        await ctx.defer()
        print("why...")
        msg = ""
        guild = ctx.member.get_guild()
        await asyncio.sleep(1)
        msg += str(guild) + ": " + str(type(guild)) + ", channels:"
        channels = guild.get_channels()
        msg += "\n" + str(channels) + "...\n"
        for channel in channels:
            msg += str(channel) + str(type(channel)) + str(channels[channel]) + str(type(channels[channel])) + "\n"
        print(msg)
        messages = Util.utils.split_message(msg)
        await ctx.respond(messages[0])