import revolt
import asyncio

class Bot(revolt.Client):
        async def on_message(self, message: revolt.Message):
                if message.content == "hello":
                        await message.channel.send("World!")

async def startBot(token:str):
        async with revolt.utils.client_session() as session:
                bot = Bot(session, str)
                await bot.start()