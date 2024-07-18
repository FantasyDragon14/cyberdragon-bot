import discord
from discord.ext import commands
from discord.ext import tasks
from aiohttp import ClientSession

from MyCogs import *

class Bot (commands.Bot):
        
        def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                
        async def on_ready(self):
                print(f"logged in as {self.user}")
                self.add_cog(Greetings(self))
        
        async def on_message(self, message):
                print("saw a message")
                if message.author == self.user:
                        return
                print("[Message]:" + message.content)
                print(message.content.startswith("$hello"))
                if message.content.startswith('$hello'):
                        await message.channel.send("Hello!")
                        
        @tasks.loop(minutes=1)
        async def refresh(self):
                print("refreshed")
                
if __name__ == '__main__':
        print("You're not supposed to run this directly...")