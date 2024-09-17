from discord.ext import commands

class Context_Test(commands.Cog):
        def __init__(self, bot) -> None:
                self.bot = bot
                self.bot.logger.info("[Context_Test] starting Context Test")
                
        
        
                
async def setup(bot):
        bot.logger.info("[Context_Test] loading Context Test")
        await bot.add_cog(Context_Test(bot))