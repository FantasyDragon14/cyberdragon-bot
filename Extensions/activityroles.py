import hikari
import lightbulb as commands
import asyncio

loader = commands.Loader()

@loader.command
class test(
    commands.SlashCommand,
    name="test",
    description="a test command",
    
    #hooks=[dev]
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context) -> None:
        ctx.respond("test running...")
        await asyncio.sleep(5)
        ctx.edit_response("test complete")