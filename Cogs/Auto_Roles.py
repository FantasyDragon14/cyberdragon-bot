import discord
from discord.ext import tasks, commands

class Auto_Roles(commands.Cog):
        def __init__(self, bot):
                self.bot = bot
                self._last_member = None
                self.bot.logger.info("[Auto_Roles] starting Auto_Roles")

                        
        @commands.hybrid_command(name="verify_member")
        async def verify(self, ctx, *, member: discord.Member = None):
                """run verify for all members or for given member"""
                msg = ""
                if not member:
                        for member in ctx.guild.members:

                                member.joined_at

        async def verify_member(self, ctx):
                pass
                
                
async def setup(bot):
        bot.logger.info("[Auto_Roles] adding AutoRoles")
        await bot.add_cog(Auto_Roles(bot))