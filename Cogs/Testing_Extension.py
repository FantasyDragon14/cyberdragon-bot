from discord.ext import commands
import discord

class Test(commands.Cog):
        def __init__(self, bot) -> None:
                print("starting Testing Extension")
                self.bot = bot
        
        @bot.tree.command(name="test1", type=app_commands.contextType.message)
        async def test1(self, interaction: discord.Interaction):
                if interaction.channel == None: return
                await interaction.channel.send(f"copied message:\n" + interaction.message)

        
                
async def setup(bot):
        print("loading Testing Extension")
        await bot.add_cog(Test(bot))