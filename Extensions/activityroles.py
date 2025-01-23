"""
assigns roles based on activity in the server
"""
import hikari
import lightbulb as commands
import sqlite3

loader = commands.Loader()

async def index_guild(guild:hikari.GatewayGuild, max_time, ):
    
    pass




"""
TODO: implement this list:
    - database / file per guild to save activity of each user (in the respective guild)
    - activity includes:
        - last x messages (in text channel, threads, voice channels)
        - last seen typing in channel
        - reactions? can we even do that? maybe
        - joined voice channel
        - /lurking [member] [duration] command (for moderator) to set 
    - settings:
        - how long do records go back?
        - activity per role
        - roles n stuff maybe later customizable, at first hardcoded
    - command for full server indexing
        - last [input days]
        - overwrite / add to db
        - can only update messages (maybe reaction based on message date?)
    - roles:
        - dead:     no activity on record / in last [Setting] days
        - lurking:  no messages / voice activity since [Setting] days, but reactions and/or typing
        - participating: small activity, quantify?
        - active: 
        - talkative: medium activity, quantify
        - 
"""