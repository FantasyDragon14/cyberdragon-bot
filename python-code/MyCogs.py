import discord
from discord.ext import tasks, commands
import asyncio

class Activity_Roles(commands.Cog):
        def __init__(self, bot):
                self.bot = bot
        
class Greetings(commands.Cog):
        def __init__(self, bot):
                self.bot = bot
                self._last_member = None

        @commands.Cog.listener()
        async def on_member_join(self, member):
                channel = member.guild.system_channel
                if channel is not None:
                        await channel.send(f'Welcome on J4F, {member.mention} ^w^')
                        
        @commands.command()
        async def hello(self, ctx, *, member:discord.member = None):
                """Says hello"""
                member = member or ctx.author
                if self._last_member is None or self._last_member.id != member.id:
                        await ctx.send(f'Hello {member.name}')
                else:
                        await ctx.send(f'Hello again, {member.name}~~\n;3c')
                self._last_member = member
                
if __name__ == '__main__':
        print("You're not supposed to run this directly...")