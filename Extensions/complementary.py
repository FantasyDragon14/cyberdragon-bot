"""
commands to complement people via the bot (or shame...?)
"""

import random
import hikari
import lightbulb as commands
import logging
import tomlkit
from Util import data as Data

try: #adding Extensin-specific activity/status if status extension exists
    import Extensions.status as Status
    Status.activities.append(hikari.Activity(name="ready to relay compliments ;3", type=hikari.ActivityType.CUSTOM),)
except: pass

        
class Loader(commands.Loader):
    async def remove_from_client(self, client: commands.Client) -> None:
        #unload / close db connections here?
        logger.info('Removing complementary Extension')
        return await super().remove_from_client(client)
    
    async def add_to_client(self, client:commands.Client) -> None:
        logger.info('adding complementary extension')
        # await register_commands()
        await super().add_to_client(client)
        
loader = Loader()
logger = logging.getLogger("complementary")

category = 'complementary'
db_name = 'complements'

guild_conf = {
    'enabled': False,
    'channel_blacklist': [],
    'is_whitelist': False,
}
guild_doc = tomlkit.item(guild_conf)
guild_doc['channel_blacklist'].comment("a list of channel ids. can be converted to a whitelist if is_whitelist is true")

Data.default_config_guild_set(category, guild_doc)

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
        is_whitelist = Data.config_guild_get(str(ctx.guild_id), (category, 'is_whitelist'))
        
        if ctx.channel_id in Data.config_guild_get(str(ctx.guild_id), (category, 'channel_blacklist')):
            if not is_whitelist:
                await ctx.respond("sending complements isn't allowed in this channel ;w;", ephemeral=True)
                return
        elif is_whitelist:
                await ctx.respond("sending complements isn't allowed in this channel ;w;", ephemeral=True)
                return
        
        if self.msg == "":
            self.msg = random.choice(compliments)
        logger.debug(f"msg is: '{self.msg}'")
        self.msg = f"{self.target.mention} {self.msg}"
        await ctx.client.app.rest.create_message(ctx.channel_id, self.msg, user_mentions=True)
        await ctx.respond("complement sent <3", ephemeral=True)
        
        pass

# i = 0
# while i < 50:
#     print(random.choice(compliments))
#     i += 1