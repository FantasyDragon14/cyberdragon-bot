if __name__ == '__main__':
        print("You're not supposed to run this directly...")
        pass

print("In module Bot __package__, __name__ ==", __package__, __name__)

import asyncio
import datetime
import logging
import os
import traceback
import typing
import aiohttp
import discord
import re
from discord.ext import commands
from discord.ext import tasks
from aiohttp import ClientSession
from pathlib import Path
from .SaveHandler import cogsFolder_name, get_cogsfolder
from Cogs import Activity_Roles

customPrefix = "}"

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

class CustomBot (commands.Bot):
        client: aiohttp.ClientSession
        _uptime: datetime.datetime = datetime.datetime.now(datetime.UTC)
        
        def __init__(self, prefix: str = None):
                
                self.logger = logging.getLogger(self.__class__.__name__)
                self.logger.info("initiating intents")
                intents = discord.Intents.default()

                intents.guild_messages = True
                intents.members = True
                intents.guilds = True
                intents.auto_moderation_execution = True
                intents.guild_polls = True
                intents.guild_reactions = True
                intents.guild_typing
                intents.message_content = True
                intents.voice_states = True
                intents.moderation = True
                intents.dm_typing = True
                intents.dm_messages = True
                intents.emojis_and_stickers = True
                intents.dm_reactions = True
                intents.guild_scheduled_events = True
                intents.integrations = True
                intents.presences = True
                
                self.logger.info("making bot")
                
                if prefix is not None:
                        super(command_prefix=commands.when_mentioned_or(prefix), intents= intents)
                else:
                        print('(no prefix)')
                        super(command_prefix=commands.when_mentioned, intents= intents)
                
                
                self.synced = False
                self.logger.info("bot complete")
                
        async def _load_extensions(self, delay: float = 0) -> None:
                await asyncio.sleep(delay)
                self.logger.info("Loading Extensions from " + cogsFolder_name)
                print(get_cogsfolder())
                if not os.path.isdir(get_cogsfolder()):
                        self.logger.error(f'Extension directory "{cogsFolder_name}" does not exist.')
                        return
                for filename in os.listdir(cogsFolder_name):
                        if filename.endswith(".py") and not filename.startswith("_"):
                                try:
                                        print(f"{cogsFolder_name}.{filename[:-3]}")
                                        await self.load_extension(f'{cogsFolder_name}.{filename[:-3]}')
                                        self.logger.info(f"Loaded extension {filename[:-3]}")
                                except commands.ExtensionError:
                                        self.logger.error(f"Failed to load extension {filename[:-3]}\n{traceback.format_exc()}")
                print(self.cogs)

        async def on_error(self, event_method: str, *args: typing.Any, **kwargs: typing.Any) -> None:
                self.logger.error(f"An error occurred in {event_method}.\n{traceback.format_exc()}")
        
        async def on_ready(self):
                print(f"logged in as {self.user}")
                await self.set_presence()
                
        async def setup_hook(self) -> None:
                await self.add_cog(SettingsCMD(self))
                self.client = aiohttp.ClientSession()
                #asyncio.create_task(self._load_extensions(1))
                await self._load_extensions(1)
                if not self.synced:
                        await self.tree.sync()
                        self.synced = not self.synced
                        self.logger.info("Synced command tree")
                
        async def close(self) -> None:
                await super().close()
                await self.client.close()
#commands: -------------------
        
#properties: ----------------------
        @property
        def user(self) -> discord.ClientUser:
                assert super().user, "Bot is not ready yet"
                return typing.cast(discord.ClientUser, super().user)
        
        @property
        def uptime(self) -> datetime.timedelta:
                return datetime.datetime.now(datetime.UTC) - self.uptime
        
#methods: -------------------------------
        async def set_presence(self, status: discord.Status = None, presence: discord.Game | discord.Streaming | discord.Activity = None):
                """
                set the presence (status and/or activity)
                """
                if presence == None: presence = discord.CustomActivity(name='Testing', emoji=':computer:')
                status = discord.Status.dnd
                await self.change_presence(status= status, activity=presence)
                pass
        
#bot = CustomBot(customPrefix)
bot = CustomBot()

print("made Bot")

@bot.hybrid_command(description="test")
async def test(ctx):
        '''test command'''
        print("[test command]")
        await ctx.send("Test")
print("initiated test command")


class SettingsCMD(commands.GroupCog, group_name='settings'):
        def __init__(self, bot):
                bot.logger.info("initiating main settings commands")
                self.bot = bot
                

        @commands.hybrid_group(name='settings')
        async def settings(self, ctx):
                await ctx.send("settings not implemented")
        
        @settings.command()
        async def general(self, ctx):
                await ctx.send("general not implemented")
                