import enum
from discord import app_commands
from discord.app_commands import tree
from discord.ext import commands
import discord
import discord.ext
from discord_python import utils

class MyAttributeEn(str, enum.Enum):
        No = ""
        DateJoined = "joindate"
        DateCreated = "creationdate"
        TopRole = "top role"

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
        async def members(self, ctx: commands.Context, attribute: MyAttributeEn):
                """lists members for the server in terminal (and in chat). List with an attribute (optional)"""
                await ctx.defer()
                header = f"Members of {ctx.guild.name}"
                if attribute != "":
                        header += "+ " + attribute
                        
                await ctx.send(header + ":")
                
                print("[DEBUG] Members: " + str([g.name for g in ctx.guild.members]))
                
                msg = ""
                for i, member in enumerate(ctx.guild.members):
                        line = f"{i + 1}.\t{member.nick or member.name}"
                
                        match attribute:
                                case "":
                                        line += ""
                                case "joindate":
                                        line += "\t| " + str(member.joined_at)
                                case "creationdate":
                                        line += "\t| " + str(member.created_at)
                                case "top role":
                                        line += "\t| " + str(member.top_role)
                        msg += line + "\n"
                        
                print("[DEBUG] splitting message into:")
                messages = utils.split_message(msg)
                print(messages)
                for s in messages:
                        print("[DEBUG] sending " + s)
                        await ctx.send(s)
                
                print("done")
        
                
async def setup(bot):
        bot.logger.info("[TestExtension] loading Debug Extension")
        await bot.add_cog(Test(bot))
