import discord
from discord.ext import commands
import random

class Greetings(commands.Cog):
        def __init__(self, bot):
                self.bot = bot
                self._last_member = None

        @commands.Cog.listener()
        async def on_member_join(self, member):
                channel = member.guild.system_channel
                if channel is not None:
                        await channel.send(f'Welcome on J4F, {member.mention} ^w^')
                        
        @commands.hybrid_command(name="greet")
        async def hello(self, ctx, *, member: discord.Member = None):
                """Says hello to a user"""
                member = member or ctx.author
                msg = f"Hello ^^"
                greetings = [
                        f"{ctx.author.display_name} says hello to {member.mention}!",
                        f"Hello {member.mention}! (from {ctx.author.display_name})",
                        f"{ctx.author.display_name} is greeting you, {member.mention}!"
                        ]
                greetings2 = [
                        f"Again is a *Hello* sent to {member.mention}!",
                ]
                if self._last_member is None or self._last_member.id != member.id:
                        if member == ctx.author: msg = f"Hello {member.mention}!"
                        else: msg = random.choice(greetings)
                else:
                        if member == ctx.author: msg = f'Hello again {member.mention} ^.·.^'
                        else: msg = random.choice(greetings2)
                await ctx.send(msg)
                self._last_member = member
                
async def setup(bot):
        await bot.add_cog(Greetings(bot))