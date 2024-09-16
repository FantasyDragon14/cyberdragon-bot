if __name__ == '__main__':
        print("You're not supposed to run this directly...")
        pass


import asyncio
import datetime
import logging
import os
import enum
import traceback
import typing
import aiohttp
import discord
import re
from discord.ext import commands
from discord import app_commands
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
                        super().__init__(command_prefix=commands.when_mentioned_or(prefix), intents= intents)
                else:
                        print('(no prefix)')
                        super().__init__(command_prefix=commands.when_mentioned, intents= intents)
                
                
                self.synced = False
                self.logger.info("bot complete")
                
        
        


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
        async def _load_extensions(self, delay: float = 0) -> None:
                await asyncio.sleep(delay)
                self.logger.info("Loading Extensions from " + cogsFolder_name)
                if not os.path.isdir(get_cogsfolder()):
                        self.logger.error(f'Extension directory "{cogsFolder_name}" does not exist.')
                        return
                for filename in os.listdir(cogsFolder_name):
                        if filename.endswith(".py") and not filename.startswith("_"):
                                try:
                                        await self.load_extension(f'{cogsFolder_name}.{filename[:-3]}')
                                        self.logger.info(f"Loaded extension {filename[:-3]}")
                                except commands.ExtensionError:
                                        self.logger.error(f"Failed to load extension {filename[:-3]}\n{traceback.format_exc()}")

        async def reload_extensions(self, reload_extension_list=None, load_new:bool=False, unload_extension_list=[]):
                """
                reloads all extensions in the folder, or only the extensions with the names in the list. skips not previously loaded extensions, except if load_new is True
                does not unload removed extensions (yet)
                """
                if not os.path.isdir(get_cogsfolder()):
                        self.logger.error(f'Extension directory "{cogsFolder_name}" does not exist.')
                        return
                
                if len(unload_extension_list) > 0:
                        self.logger.info("removing extensions")
                        for e in unload_extension_list:
                                try :self.unload_extension(e)
                                except commands.ExtensionNotLoaded:
                                        self.logger.error(f'extension {filename[:-3]} was not loaded')
                                except commands.ExtensionNotFound:
                                        self.logger.error(f"extension {filename[:-3]} could not be removed because it couldn't be found")
                                else: self.logger.info(f'extension {filename[:-3]} successfully unloaded')

                if reload_extension_list == None: reload_extension_list = list(self.extensions.keys())
                else:
                        reload_extension_list = [f"{cogsFolder_name}.{extension_name}" for extension_name in reload_extension_list]
                self.logger.info(f"Reloading these Extensions: {reload_extension_list}")
                extension_files = os.listdir(cogsFolder_name)

                extension_files = [f"{cogsFolder_name}.{extension_name[:-3]}" for extension_name in extension_files if extension_name.endswith(".py") and not extension_name.startswith("_") ]
                self.logger.info(f"Extensions in Directory:    {extension_files}")
                
                #reloading extensions
                for e in reload_extension_list:
                        try:
                                extension_files.remove(e)
                                print(f"removed {e} from list")
                        finally:
                                try:
                                        await self.reload_extension(e)
                                        self.logger.info(f"Loaded extension {e}")
                                except commands.ExtensionNotFound:
                                        self.logger.error(f'extension {e} not Found')
                                except commands.ExtensionNotLoaded:
                                        self.logger.error(f'extension {e} was not loaded')
                                        if load_new:
                                                try:
                                                        await self.load_extension(e)
                                                        self.logger.info(f"Loaded extension {e}")
                                                except commands.ExtensionError:
                                                        self.logger.error(f"Failed to load extension {e}\n{traceback.format_exc()}")
                
                                except commands.ExtensionError:
                                        self.logger.error(f"Failed to reload extension {e}\n{traceback.format_exc()}")

                #loading new extensions
                if load_new:
                        self.logger.info(f"Loading new extensions: {extension_files}")
                        for filename in extension_files:
                                try:
                                        await self.load_extension(filename)
                                        self.logger.info(f"Loaded extension {filename}")
                                except commands.ExtensionError:
                                        self.logger.error(f"Failed to load extension {filename}\n{traceback.format_exc()}")
                        
                self.logger.info("Finished reloading extensions, syncing Commands...")
                await self.tree.sync()
                self.synced = True
                self.logger.info("done")


                

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

def check_for_dev_privilege(ctx):
        dev_list = [
                432248872845180932, #FantasyDragon14
        ]
        print("checking dev")
        print(f"{ctx.message.author.id} in {dev_list} : {ctx.message.author.id in dev_list}")
        return ctx.message.author.id in dev_list

class MyBoolEn(str, enum.Enum):
        Yes = "yes"
        No = "no"

class SettingsCMD(commands.GroupCog, group_name='settings'):
        def __init__(self, bot):
                bot.logger.info("initiating main settings commands")
                self.bot = bot

        @app_commands.command(name="reload_extensions" )
        @commands.check(check_for_dev_privilege)
        async def reload_extensions(self, ctx, load_new: MyBoolEn):
                await ctx.response.send_message("reloading...")
                try:
                        await bot.reload_extensions(load_new=(load_new == "yes"))
                except:
                        await ctx.followup.send(f"something went wrong")
                else:
                        await ctx.followup.send("Reloaded Extensions")

        @commands.hybrid_command(name= 'dev')
        @commands.check(check_for_dev_privilege)
        async def some_command(seld, ctx):
                await ctx.defer()
                await asyncio.sleep(10)
                await ctx.send("you have dev privileges with this bot :3")

        @commands.hybrid_group(name='subsettings', fallback='test')
        async def settings(self, ctx):
                await ctx.send("subsettings not implemented")
        
        @settings.command()
        async def general(self, ctx):
                await ctx.send("general not implemented")

        @settings.command()
        async def specific(self, ctx):
                await ctx.send("specific not implemented")
                
