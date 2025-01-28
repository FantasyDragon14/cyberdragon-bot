import os
import sys
import hikari
import lightbulb as commands
import asyncio
import sqlite3

#from bot import dev

class CustomLoader(commands.Loader):
    pass
    async def remove_from_client(self, client: commands.Client) -> None:
        #unload / close db connections here?
        return await super().remove_from_client(client)


loader = commands.Loader()

print("-----------------------\n\tTesting...\n-----------------------")

db = sqlite3.connect("./Data/DB/test.db")

@loader.command
class test(
    commands.SlashCommand,
    name="test",
    description="a test command",
    
    #hooks=[dev]
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context) -> None:
        print("test running")
        response = await ctx.respond(f"{ctx.member.mention}test running...", user_mentions=True)
        await asyncio.sleep(10)
        await ctx.edit_response(response, "test complete")
        print("test complete")


@loader.command
class HelloWorld(
    commands.SlashCommand,
    name="hello-world",
    description="Makes the bot say hello world"
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context) -> None:
        await ctx.respond("Hello World!")

@loader.command
class Restart_Bot(
    commands.SlashCommand,
    name="restart_completely",
    description="Restarts the bot completely for testing. needs dev privileges",
    hooks=[commands.prefab.owner_only],
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context) -> None:
        python = sys.executable
        await ctx.respond("restarting, done if I'm online again")
        os.execl(python, python, *sys.argv)