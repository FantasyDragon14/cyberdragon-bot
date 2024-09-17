"""
Run this file to use the bot
"""
"""
import asyncio
from pathlib import Path

import os
from revolt_python import bot_token
from revolt_python import Bot

os.chdir(Path(__file__).parent.absolute())

print ("bot starting...")


#async def wait():
#    await bot.is_ready()

if __name__ == "__main__":
    asyncio.run(Bot.startBot(bot_token.get_token()))
"""
import revolt
import asyncio

from revolt_python import bot_token

class Client(revolt.Client):
    async def on_message(self, message: revolt.Message):
        if message.content == "hello":
            await message.channel.send("hi how are you")

async def main():
    async with revolt.utils.client_session() as session:
        client = Client(session, bot_token.get_token())
        await client.start()

asyncio.run(main())