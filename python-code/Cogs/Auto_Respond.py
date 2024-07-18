import re
import random
from discord.ext import commands

greetings = ["Hello!", "Hi", "Hi ^^", "UwU", "Hello", "hello", "Hii~", "who *are* you?", "Hola!", "Greetings!", "o7", "hi", "Hello!", "Hello :D", "nya~", "nice to see you :D", "hi (:"]

class Auto_Respond(commands.Cog):
        def __init__(self, bot) -> None:
                print("starting autoRespond")
                self.bot = bot
                
        @commands.Cog.listener()
        async def on_message(self, message):
                if message.author.id == self.bot.user.id:
                        return
                print(message.content)
                if re.match('(hello)|(hi)', message.content, re.I):
                        await message.reply(random.choice(greetings), mention_author=True)
                
async def setup(bot):
        print("loading autoRespond")
        await bot.add_cog(Auto_Respond(bot))