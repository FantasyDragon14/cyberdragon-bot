from discord import app_commands
from discord.app_commands import tree
from discord.ext import commands
import discord

class Test(commands.Cog):
        def __init__(self, bot: commands.Bot) -> None:
                self.bot = bot
                
                guilds = ""
                for i, guild in enumerate(self.bot.guilds):
                        guilds += f"| {i}: {guild.name}|"
                        
                self.bot.logger.info("[Debug] guild list: " + str(guilds)) #list all guilds the bot is currently in
                
                self.ctx_menu = app_commands.ContextMenu(
                                name='Cool Command Name',
                                callback=self.my_cool_context_menu, # set the callback of the context menu to "my_cool_context_menu"
                        )
                self.bot.tree.add_command(self.ctx_menu) # add the context menu to the tree



        @commands.hybrid_command(name="test2", description="test2")
        async def test(self, ctx):
                '''test command'''
                print("[test command in test cog]")
                await ctx.send("Test 2")

        async def my_cool_context_menu(self, interaction: discord.Interaction, message: discord.Message) -> None:
                await interaction.response.send_message(message.content)
                
                
        @commands.hybrid_command(name="list_members")
        async def members(self, ctx):
                """lists members for the server in terminal (and in chat)"""
                await ctx.defer()
                msg = f"Members of {ctx.guild.name}: \n"
                for i, member in enumerate(ctx.guild.members):
                        msg += f"{i}.\t{member.nick or member.name}\n"
                print(msg)
                await ctx.send(msg)
                print("done")
        
        
                
async def setup(bot):
        bot.logger.info("[TestExtension] loading Debug Extension")
        await bot.add_cog(Test(bot))