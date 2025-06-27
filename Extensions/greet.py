"""
reacts to member joins with a welcome message
if setting is true, also sends a custom message on member leaving
"""
import hikari
import lightbulb as commands
import logging

class Loader(commands.Loader):
    async def remove_from_client(self, client: commands.Client) -> None:
        #unload / close db connections here?
        logger.info('Removing greet Extension')
        return await super().remove_from_client(client)
    
    async def add_to_client(self, client:commands.Client) -> None:
        logger.info('adding greet extension')
        # await register_commands()
        await super().add_to_client(client)
        
loader = Loader()
logger = logging.getLogger("greet")

try: #adding Extensin-specific activity/status if status extension exists
    import Extensions.status as Status
    Status.activities.append(hikari.Activity(name="for new members", type=hikari.ActivityType.WATCHING),)
except: pass

@loader.listener(hikari.MemberCreateEvent)
async def member_joined(event: hikari.MemberCreateEvent) -> None:
    guild:hikari.GatewayGuild = event.get_guild()
    guild_name = guild.name
    
    logger.info(f"{event.member.mention} joined {guild_name}, sending message.")
    logger.debug(f'guild_flags: {event.member.guild_flags}')
    logger.debug(f'user flags: {event.member.flags}')

    #TODO make this message customizable in settings, maybe even per server
    msg = f"{event.member.mention} welcome to {guild_name} ^w^"
    if hikari.GuildMemberFlags.DID_REJOIN in event.member.guild_flags:
        msg = f"Welcome back {event.member.mention}!"
    logger.debug("sending " + msg)
    await event.app.rest.create_message(guild.system_channel_id, msg, user_mentions=True)
    pass

@loader.listener(hikari.MemberDeleteEvent)
async def member_left(event: hikari.MemberDeleteEvent)  -> None:
    guild:hikari.GatewayGuild = event.get_guild()
    logger.info(f"{event.user.display_name} left {guild.name}")
    logger.debug(f'user flags: {event.user.flags}')
    
    #TODO make this message customizable in settings, maybe even per server
    msg = f"{event.user.mention} left"
    await event.app.rest.create_message(guild.system_channel_id, msg)
    pass