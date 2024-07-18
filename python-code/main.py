import os
import discord
from Bot import Bot
from discord.ext import commands
import bot_token
from MyCogs import Greetings, Activity_Roles

print ("bot starting...")
intents = discord.Intents.default()
intents.message_content = True
bot = Bot(intents)


if __name__ == "__main__":
    print ("Hello ^^")

    print("(idk what I'm doing)")
    
    bot.run(bot_token.get_token())
    
    