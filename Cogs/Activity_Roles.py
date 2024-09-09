import asyncio
import datetime
from main_code.SaveHandler import Settings
import discord
from discord.ext import tasks, commands

class Activity_Roles(commands.Cog):
        def __init__(self, bot: commands.Bot):
                self.bot = bot
                self.lock = asyncio.Lock()
                self.bot.logger.info("[ActivityRoles] Initiating ActivityRoles")
                
                self.add_settings(self.ActivityRoles)
                
                try:
                        for guild in self.bot.guilds:
                                result = asyncio.run(self.ActivityRolesEnabled(guild))
                                if result:
                                        self.repeat_activity.start(guild)
                finally:
                        pass


        def cog_unload(self) -> tasks.Coroutine[tasks.Any, tasks.Any, None]:
                self.bot.logger.info("[ActivityRoles] unloading ActivityRoles")
                self.repeat_activity.stop()
                
                
        def add_settings(self, group_to_add):
                #self.bot.get_cog("SettingsCMD").app_command.add_command(self.ActivityRoles)
                #print(self.bot.commands)
                ls = list(self.bot.commands)
                #for c in ls:
                #        print(c.name)
                cmd = [c for c in ls if c.name == 'settings']
                #print(cmd)
                
        async def refresh_activity_roles(self, guild:discord.Guild):
                """Refreshes all activity roles for a given guild

                Args:
                    guild (_type_): the guild to perform the operation in
                """
                user_message_dict = {}
                for member in guild.members:
                        user_message_dict[member] = 0
                
                self.bot.logger.error("Not Implemented yet, WIP")
        
        @commands.hybrid_group(name='activityroles')
        async def ActivityRoles(self, ctx):
                """The addition to the core settings command that allows for the configuration of this extendion here
                """
                raise NotImplementedError
        
        @ActivityRoles.command(name='toggle_auto_refresh')
        async def toggleAutoRefresh(self, ctx):
                Settings.setSetting(ctx.guild, self.__class__.__name__, 'toggleAutoRefresh', True)
        
                
        @commands.hybrid_command(name='refresh_activity_roles_now')
        async def refreshActivityRoles(self, ctx):
                """the discord-command to manually execute refresh_activity_roles in a guild
                """
                time = datetime.datetime.now(datetime.UTC)
                await self.refresh_activity_roles(ctx.guild)
                ctx.send(datetime.datetime.now(datetime.UTC) - time)
                
        @tasks.loop(hours=24)
        async def repeat_activity(self, guild):
                self.bot.logger.info("[ActivityRoles] refreshing for " + guild.name)
                await self.refresh_activity_roles(guild)
        
        @classmethod
        def ActivityRolesEnabled(cls, guild) -> bool:
                return Settings.getSetting(guild, cls.__name__, "ActivityRoles", True)
        
async def setup(bot):
        await bot.add_cog(Activity_Roles(bot))
        

