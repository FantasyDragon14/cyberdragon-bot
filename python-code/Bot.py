if __name__ == '__main__':
        print("You're not supposed to run this directly...")
        pass

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


cogs_directory= "Cogs"
customPrefix = "}"

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

class CustomBot (commands.Bot):
        client: aiohttp.ClientSession
        _uptime: datetime.datetime = datetime.datetime.now(datetime.UTC)
        
        def __init__(self, prefix: str, cogs_dir: str):
                
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
                super().__init__(command_prefix=commands.when_mentioned_or(prefix), intents= intents)
                
                self.cogs_dir = cogs_dir
                self.synced = False
                self.logger.info("bot complete")
                
        async def _load_extensions(self) -> None:
                self.logger.info("Loading Extensions from " + self.cogs_dir)
                if not os.path.isdir(self.cogs_dir):
                        self.logger.error(f"Extension directory {self.cogs_dir} does not exist.")
                        return
                for filename in os.listdir(self.cogs_dir):
                        if filename.endswith(".py") and not filename.startswith("_"):
                                try:
                                        await self.load_extension(f"{self.cogs_dir}.{filename[:-3]}")
                                        self.logger.info(f"Loaded extension {filename[:-3]}")
                                except commands.ExtensionError:
                                        self.logger.error(f"Failed to load extension {filename[:-3]}\n{traceback.format_exc()}")
                print(self.cogs)

        async def on_error(self, event_method: str, *args: typing.Any, **kwargs: typing.Any) -> None:
                self.logger.error(f"An error occurred in {event_method}.\n{traceback.format_exc()}")
        
        async def on_ready(self):
                print(f"logged in as {self.user}")
                
        async def setup_hook(self) -> None:
                self.client = aiohttp.ClientSession()
                await self._load_extensions()
                if not self.synced:
                        await self.tree.sync()
                        self.synced = not self.synced
                        self.logger.info("Synced command tree")
                
        async def close(self) -> None:
                await super().close()
                await self.client.close()
                
        @property
        def user(self) -> discord.ClientUser:
                assert super().user, "Bot is not ready yet"
                return typing.cast(discord.ClientUser, super().user)
        
        @property
        def uptime(self) -> datetime.timedelta:
                return datetime.datetime.now(datetime.UTC) - self.uptime
        
bot = CustomBot(customPrefix, cogs_directory)

print("made Bot")

@bot.command(description="test")
async def test(ctx):
        '''test command'''
        print("[test command]")
        await ctx.send("Test")
print("initiated test command")