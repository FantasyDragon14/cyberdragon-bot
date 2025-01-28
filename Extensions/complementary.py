"""
commands to complement people via the bot (or shame...?)
"""
#TODO

import random
import hikari
import lightbulb as commands

loader = commands.Loader()

compliments = [
    "you're cool ^^",
    "you're cool btw",
    "you're cool :3",
    "you're great btw :3",
    "you're great btw",
    "you're great :3",
    "somebody just wanted to say you're cool",
    "take this unexpected compliment! You're great :D",
    "someone just called you a nice person ^w^",
    "you're nice btw >w<",
    "you're nice ^w^",
    "<- cool person spotted B3",
    "<- cutie >:3c"
]

@loader.command
class Complement(
    commands.SlashCommand,
    name="complement-user",
    description="complement a given user",
):
    #options
    # target = commands.mentionable("Target", "who will be pinged",) #while it would be very funny, i don't think allowing people to ping any role indirectly without permission check is a good idea >~<
    target = commands.user("user", "the User to be complemented")
    #optional:
    msg = commands.string("text", '''optional text. shows up as "@user 'text'"''', default="")
    @commands.invoke
    async def invoke(self, ctx: commands.Context) -> None:
        if self.msg == "":
            self.msg = random.choice(compliments)
        print(f"[DEBUG] msg is: '{self.msg}'")
        self.msg = f"{self.target.mention} {self.msg}"
        await ctx.client.app.rest.create_message(ctx.channel_id, self.msg, user_mentions=True)
        await ctx.respond("complement sent <3", ephemeral=True)
        
        pass

# i = 0
# while i < 50:
#     print(random.choice(compliments))
#     i += 1