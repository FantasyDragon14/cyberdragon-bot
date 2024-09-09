import re
import random
from discord.ext import commands

greetings = ["Hello!", "Hi!", "Hi ^^", "UwU", "Hello", "hello", "Hii~", "who *are* you?", "Hola!", "Greetings!", "o7", "hi...", "Hello!", "Hello :D", "nya~", "nice to see you :D", "hi (:"]

class Auto_Respond(commands.Cog):
        def __init__(self, bot) -> None:
                self.bot = bot
                self.bot.logger.info("[AutoResponder] starting Auto Respond")

        @commands.Cog.listener()
        async def on_message(self, message):
                if message.author.id == self.bot.user.id:
                        return
                if re.match('(hello)|(hi)|(hallo)', message.content, re.I):
                        await message.reply(random.choice(greetings), mention_author=True)

async def setup(bot):
        bot.logger.info("[AutoResponder] loading Auto Respond")
        await bot.add_cog(Auto_Respond(bot))