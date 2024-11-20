"""
reacts to member joins with a welcome message
if setting is true, also sends a custom message on member leaving
"""
import hikari
import lightbulb as commands

class customLoader(commands.Loader):
    pass

loader = commands.Loader()


@loader.listener(hikari.MemberCreateEvent)
async def member_joined(event: hikari.MemberCreateEvent) -> None:
    guild:hikari.GatewayGuild = event.get_guild()
    guild_name = guild.name

    #TODO make this message customizable in settings, maybe even per server
    msg = f"{event.member.mention} welcome to {guild_name} ^w^"
    if hikari.Guilds.GuildMemberFlags.DID_REJOIN in event.member.flags:
        msg = f"Welcome back {event.member.mention}!"
    print("sending " + msg)
    await event.app.rest.create_message(guild.system_channel_id, msg)
    pass

@loader.listener(hikari.MemberDeleteEvent)
async def member_left(event: hikari.MemberDeleteEvent)  -> None:
    guild:hikari.GatewayGuild = event.get_guild()
    #TODO implement check if setting is enabled
    #if (settings.setting_enabled(guild, "message_on_member_leave")):
    
    #TODO make this message customizable in settings, maybe even per server
    msg = f"{event.old_member.mention} just left the Server..."
    pass