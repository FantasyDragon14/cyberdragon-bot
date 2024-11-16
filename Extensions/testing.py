import hikari
import lightbulb as commands
import asyncio

loader = commands.Loader()

print("-----------------------\n\tTesting...\n-----------------------")

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
        response = await ctx.respond("test running...")
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