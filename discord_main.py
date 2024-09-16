"""
Run this file to use the bot
"""
from pathlib import Path
from discord_code import SaveHandler

from discord_code.Bot import bot
import os
from discord_code import bot_token

os.chdir(Path(__file__).parent.absolute())

print ("bot starting...")

async def wait():
    await bot.is_ready()

if __name__ == "__main__":
    print ("Hello ^^")

    print("(idk what I'm doing)")
    
    SaveHandler.folders_ready()
    
    bot.run(bot_token.get_token())
    
    print("stopped")