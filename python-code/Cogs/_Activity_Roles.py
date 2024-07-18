from discord.ext import tasks, commands
class Activity_Roles(commands.Cog):
        def __init__(self, bot):
                self.bot = bot
                
        @commands.command()
        async def start(self, ctx):
                channel = ctx.channel
                
                self.repeat_refresh.start()
                
        @commands.command()
        async def stop(self, ctx):
                self.repeat_refresh.cancel()
                
        @tasks.loop(minutes=1)
        async def repeat_refresh(self):
                pass
        
async def setup(bot):
        await bot.add_cog(Activity_Roles(bot))
