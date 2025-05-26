"""
reacts to member joins with a welcome message
if setting is true, also sends a custom message on member leaving
"""
import hikari
import lightbulb as commands


loader = commands.Loader()

try: #adding Extensin-specific activity/status if status extension exists
    import Extensions.status as Status
    Status.activities.append(hikari.Activity(name="Hi everyone ^w^", type=hikari.ActivityType.CUSTOM),)
except: pass

@loader.listener(hikari.MemberCreateEvent)
async def member_joined(event: hikari.MemberCreateEvent) -> None:
    guild:hikari.GatewayGuild = event.get_guild()
    guild_name = guild.name
    
    print(f"{event.member.mention} joined {guild_name}, sending message...")

    #TODO make this message customizable in settings, maybe even per server
    msg = f"{event.member.mention} welcome to {guild_name} ^w^"
    if hikari.GuildMemberFlags.DID_REJOIN in event.member.flags:
        msg = f"Welcome back {event.member.mention}!"
    print("sending " + msg)
    await event.app.rest.create_message(guild.system_channel_id, msg, user_mentions=True)
    pass

@loader.listener(hikari.MemberDeleteEvent)
async def member_left(event: hikari.MemberDeleteEvent)  -> None:
    guild:hikari.GatewayGuild = event.get_guild()
    #TODO implement check if setting is enabled
    #if (settings.setting_enabled(guild, "message_on_member_leave")):
    
    #TODO make this message customizable in settings, maybe even per server
    msg = f"{event.member_old.mention} just left the Server..."
    print(msg)
    await event.app.rest.create_message(guild.system_channel_id, msg)
    pass