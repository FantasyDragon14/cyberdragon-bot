"""reacts to member joins with a welcome message
    if setting is true, also sends a custom message on member leaving
"""
import hikari
import lightbulb as commands

class customLoader(commands.Loader):
    pass

loader = commands.Loader()

# @loader.listener(hikari.MessageCreateEvent)
# async def on_message(ctx: commands.Context):
#     pass #TODO greet

@loader.listener(hikari.MemberCreateEvent)
async def member_joined(event: hikari.MemberCreateEvent) -> None:
    #TODO send Welcome Message
    guild:hikari.GatewayGuild = event.get_guild()
    if guild: guild_name = guild.name
    else: guild_name = "unknown"
    msg = f"Welcome to {guild_name} {event.member.mention} ^w^"
    print("sending " + msg)
    await event.app.rest.create_message(guild.system_channel_id, msg)
    pass

