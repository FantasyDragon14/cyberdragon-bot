from discord import app_commands
from discord.app_commands import tree
from discord.ext import commands
import discord

class Test(commands.Cog):
        def __init__(self, bot: commands.Bot) -> None:
                self.bot = bot
                self.ctx_menu = app_commands.ContextMenu(
                                name='Cool Command Name',
                                callback=self.my_cool_context_menu, # set the callback of the context menu to "my_cool_context_menu"
                        )
                self.bot.tree.add_command(self.ctx_menu) # add the context menu to the tree

        async def my_cool_context_menu(self, interaction: discord.Interaction, message: discord.Message) -> None:
                await interaction.response.send_message(message.content)
                
async def setup(bot):
        bot.logger.info("[TestExtension] loading Test Extension")
        await bot.add_cog(Test(bot))