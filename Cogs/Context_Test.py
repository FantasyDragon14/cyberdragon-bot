from discord.ext import commands

class Context_Test(commands.Cog):
        def __init__(self, bot) -> None:
                print("starting contextTest")
                self.bot = bot
                
        
        
                
async def setup(bot):
        print("loading contextTest")
        await bot.add_cog(Context_Test(bot))