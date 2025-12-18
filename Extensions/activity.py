"""
assigns roles based on activity in the server

TODO: Split this up into two extensions: one seperate for activity logging (maybe save message and content too? Not sure how we'd use it except for activity roles...) , one for the role and activity score
So other extensions can use activity data aswell?
"""
import attrs
import hikari
import hikari.guilds
import lightbulb as commands
import sqlite3
import Util.data as Data
import Util.utils as Util
from enum import Enum
import datetime, math, re, os, sys
import logging
import tomlkit
import pandas

try: #adding Extension-specific activity/status if status extension exists
    import Extensions.status as Status
    Status.activities.append(hikari.Activity(name="your activity", type= hikari.ActivityType.WATCHING))
except: pass

try: #for updating  if activityroles extension exists
    import Extensions.status as Status
    Status.activities.append(hikari.Activity(name="your activity", type= hikari.ActivityType.WATCHING))
except: pass

mode = "testing"
try:
    mode = sys.argv[1]
except:
    pass

class Loader(commands.Loader):
    async def remove_from_client(self, client: commands.Client) -> None:
        #unload / close db connections here?
        logger.info('Removing activity extension')
        return await super().remove_from_client(client)
    
    async def add_to_client(self, client:commands.Client) -> None:
        logger.info('adding activity extension')
        await register_commands()
        await super().add_to_client(client)
        try:
            guilds_update_activity.start()
        except: logger.debug("didn't start activity updater")
        
loader = Loader()
logger = logging.getLogger("activity")



db_name = "activity"
category = "activity"
update_frequency = pandas.Timedelta(hours=1)
if mode == 'testing':
    update_frequency = pandas.Timedelta(minutes=5)

#general config
gen_conf = {
                'update_freq': pandas.Timedelta(hours=1).isoformat(),
            }
gen_doc = tomlkit.item(gen_conf)
gen_doc['update_freq'].comment('Format: ISO8601 timedelta. How much Time between ')

guild_conf = {
                'enabled': False,
                'updateOnEvent': True,
                'dataretention': {
                        'total': pandas.Timedelta(days=30).isoformat(),
                        'typing': pandas.Timedelta(days=5).isoformat(),
                },
        }
guild_doc = tomlkit.item(guild_conf)
#doc['liveupdate'].comment('whether a members role should be updated as soon as activity is detected')
guild_doc['dataretention'].comment('Format: ISO8601 timedelta')

    
# Data.default_config_general_set(category, gen_doc)
Data.default_config_guild_set(category, guild_doc)


class ActivityType(Enum):
    """The type of activity a user did. for sending a message, that's MESSAGE, etc
    Not to be confused by hikari.ActivityType
    """
    MESSAGE = 'msg'
    VOICE = 'vce'
    REACTION = 'rct'
    TYPING = 'typ'
    POLL = 'pll'
    LURKING = 'lrk'
    
class Operation(Enum):
    SAVE = 1 # save the activity
    MODIFY = 0 # modify existing activity (for completing voice join, for edited messages)
    DELETE = -1 # try to delete the database entry (because the reaction was removed, the message got deleted)

@attrs.define()
class Activity():
    activity_type:ActivityType = attrs.field()
    '''the type of activity'''
    date: datetime.datetime = attrs.field()
    '''when the activity got logged'''
    author: hikari.Member| None = attrs.field()
    '''the member who caused the activity. None on a delete Event'''
    author_id: hikari.Snowflake | None = attrs.field()
    '''the id of the member who triggered the activity. None on Delete'''
    is_bot: bool = attrs.field()
    '''if the activity is from a bot'''
    guild_id: hikari.Snowflake = attrs.field()
    '''the id of the guild the activity happened in'''
    message_id: hikari.Snowflake | None = attrs.field()
    '''the message id if applicable'''
    channel_id: hikari.Snowflake = attrs.field()
    '''the channel id the activity took place in'''
    additional_data: str = attrs.field()
    '''additional data, varies between activity types'''
    score: int = attrs.field()
    '''the score of the activity. number of words, seconds of vc'''
    operation: Operation = attrs.field()
    '''the action taken when log() is called'''
    logged: bool = attrs.field()
    '''whether the activity got logged into the db already'''
    def __init__(self, guild_id: hikari.Snowflake, activity_type:ActivityType, channel_id: hikari.Snowflake, message_id: hikari.Snowflake|None = None, author:hikari.guilds.Member = None, additional_info: str = '', date: datetime.datetime = datetime.datetime.now(datetime.UTC), operation:Operation = Operation.ADD, score:int = 0):
        """
        Args:
            guild_id (hikari.Snowflake): the id of the guild this happened in
            activity_type (ActivityType): Type of activity
            channel_id (hikari.Snowflake): the channel id where the activity took place in
            message_id (hikari.Snowflake, optional): the id of the message if Activity is message or reaction, else None
            
            author (hikari.guilds.Member, optional): member who did it
            additional_info (str, optional): additional Type specific info
            date (datetime.datetime): the date and time the activity happened
            words (int, optional): Number of words if the ActivityType is MESSAGE. Defaults to 0.
            guild (hikari.GatewayGuild|hikari.RESTGuild, optional): we can get the guild from the member object, so idk why i even put this here. Defaults to None.
        """
        self.guild_id = guild_id
        self.author = author
        if author != None: self.is_bot = author.is_bot()
        else: self.is_bot = False
        self.activity_type = activity_type
        self.channel_id = channel_id
        self.message_id = message_id
        self.date = date
        self.additional_data = additional_info
        self.score = score
        self.operation = operation
        self.logged = False

    def from_event(self, event:hikari.GuildMessageCreateEvent|hikari.GuildMessageDeleteEvent|hikari.GuildMessageUpdateEvent|hikari.GuildReactionAddEvent|hikari.GuildReactionDeleteEvent|hikari.GuildReactionDeleteAllEvent|hikari.GuildReactionDeleteEmojiEvent|hikari.GuildTypingEvent|hikari.VoiceStateUpdateEvent):
        self.date = datetime.datetime.now(datetime.UTC) #setting date
        self.activity_type = ActivityType.MESSAGE # default setting ig
        self.guild_id = event.guild_id # all events supply guild_id
        
        if isinstance(event, hikari.GuildTypingEvent): #set typing
            self.activity_type = ActivityType.TYPING
        if not isinstance(event, (type(hikari.GuildTypingEvent), type(hikar.VoiceStateUpdateEvent), type(hikari.GuildBulkMessageDeleteEvent))):
            self.message_id = event.message_id
            
        if isinstance(event, (type(hikari.GuildMessageCreateEvent), # if event supplies member
                            type(hikari.GuildReactionAddEvent),
                            type(hikari.GuildMessageUpdateEvent),
                            type(hikari.VoiceServerUpdateEvent),
        )):
            self.author = event.member
            self.author_id = event.author_id
            
        
        
            
            
        
    async def log(self, cursor:sqlite3.Cursor = None, suppress_event:bool = False):
        """
        Args:
            cursor (sqlite3.Cursor, optional): 
            suppress_event (bool, optional): set this to true if you don't want to fire an ActivityUpdate event after logging"""
        logger.debug(f"Attempting to log a {self.activity_type.name} activity")
        if cursor is None: cur = Data.get_guild_db(self.guild.id, db_name).cursor()
        else: cur = cursor
        await ensure_member_table(cur, str(self.member.id))
        logger.debug('logging activity into table...')
        query = f"""--sql
                INSERT INTO {Data.member_table(str(self.member.id))} (
                    activity,
                    date,
                    channel_id,
                    message_id,
                    info,
                    score,
                    deleted,
                )
                VALUES (
                    ?,
                    unixepoch(?), 
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                )
                """
        cur.execute(query, (
            str(self.activity_type.value),
            self.date,
            int(self.channel_id),
            int(self.message_id),
            str(self.additional_data),
            int(self.score),
            0
            )
        )
        logger.debug('query executed')
        if cursor is None:
            cur.connection.commit()
            cur.connection.close()
        logger.debug("Activity logged")
        self.logged = True


@attrs.define()
class ActivityUpdate(hikari.Event):
    """called when the data in the activity db has changed"""
    #TODO: figure out if i should pass more info than just that
    app: hikari.traits.RESTAware = attrs.field()
    activity: list[Activity] = attrs.field()
    '''list of added activities. empty if only removed'''
    guild_id: hikari.Snowflake | int = attrs.field()
    '''the id of the guild whose activity got updated'''


async def activity_member_update(cur: sqlite3.Cursor, guild: hikari.GatewayGuild|hikari.RESTGuild, member:hikari.Member, level_role:dict=None):
    """updates a members activity. this includes pruning the db, recalculating the activity level and score and reassigning the activity role if necessary
    """
    #TODO
    pass
    

async def activity_guild_update(guild:hikari.GatewayGuild|hikari.RESTGuild):
    #TODO
    pass
    
    
def user_getlastloggeddate(cur:sqlite3.Cursor, user_table:str):
    """return the date of the last logged activity of a given user"""
    query = f"""--sql
            SELECT MAX(unix_date)
            FROM {user_table}; 
            """
    cur.execute(query)
    result = cur.fetchall()
    return datetime.datetime.fromtimestamp(result[0])
    #TODO Test this

def guild_getlastloggeddate(cur:sqlite3.Cursor) -> datetime.datetime:
    """return the date of the last logged date in a given db"""

    cur.execute("""--sql
        SELECT name FROM sqlite_schema WHERE type='table';
        """)
    result = cur.fetchall()
    last_date = datetime.datetime.min
    for table in result:
        i = user_getlastloggeddate(cur=cur, user_table=table[0])
        if i > last_date: last_date = i
    return last_date
    #TODO Test this
 
def prune_member_table(cur:sqlite3.Cursor, member_table:str, max_time: datetime.timedelta, typing_time:datetime.timedelta):
    """deletes all rows from the members table where the timedelta between now and log-date is bigger than max_time
    Commits when done

        Args:
            cur (sqlite.Cursor): the cursor to the db where the member table should be pruned
            member_id (str): the id of the member whose table should be pruned
            max_time (datetime.timedelta): the maximum timedelta a row is kept in the db
            max_typing (datetime.timedelta): the maximum timedelta a typing activity is saved
        """
    if not Data.table_exists(cur, member_table): return
    now = datetime.datetime.now(datetime.UTC)
    query = f"""--sql
            DELETE FROM {member_table} WHERE (
                unixepoch(?) - unix_date > ?
            )
            """
    cur.execute(query, ("now", max_time.total_seconds()))
    
    query = f"""--sql
            DELETE FROM {member_table} WHERE (
                unixepoch(?) - unix_date > ? AND
                activity = ?
            )
            """
    cur.execute(query, ('now', typing_time.total_seconds(), str(ActivityType.TYPING.value)))
    
    query = """--sql
            
            """
    
    cur.connection.commit()
    logger.debug(f'pruned table {member_table}')
       
def prune_guild_db(guild_id:str, cursor:sqlite3.Cursor=None):
    """prunes the whole db of a guild"""
    if cursor is None:
        cur = Data.get_guild_db(guild_id, db_name).cursor()
    else: cur = cursor
    max_time = pandas.to_timedelta(Data.config_guild_get(str(guild_id), (category, "dataretention", "total"))).to_pytimedelta()
    max_typing = pandas.to_timedelta(Data.config_guild_get(str(guild_id), (category, "dataretention", "typing"))).to_pytimedelta()
    cur.execute("""--sql
               SELECT name FROM sqlite_schema WHERE type='table';
               """) #get all tables
    for result in cur.fetchall():
        prune_member_table(cur, result[0], max_time, max_typing)
    if cursor is None:
        cur.connection.close()
    
async def ensure_member_table(db_cursor:sqlite3.Cursor, member_id:str):
    """ensures the table for a given member_id exists in the provided cursors databank
        will donothing if it already exists, will create a new table if it doesn't exist
    Args:
        db_cursor (sqlite3.Cursor): a cursor to a activity-databank
        member_id (str): the member_id to be checked
    """
    if not Data.table_exists(db_cursor, Data.member_table(member_id)):
        # remember: How many columns do we really need?
        query = f"""--sql
                CREATE TABLE {Data.member_table(member_id)} (
                    activity text,
                    date int,
                    channel_id int,
                    message_id int,
                    info text,
                    score int,
                    deleted int,
                )
                """
        db_cursor.execute(query)
        
async def index_guild(guild:hikari.GatewayGuild|hikari.RESTGuild, max_time:datetime.timedelta=None, replace:bool = False):
    cur = Data.get_guild_db(guild.id, db_name).cursor()
    logger.info(f'indexing Guild {guild.name} (id {guild.id}):')
    if replace:
        
        logger.info('replacing all data, deleting old...')
        cur.execute("""--sql
               SELECT name FROM sqlite_schema WHERE type='table';
               """)

        result = cur.fetchall()
        query = """--sql
                DROP TABLE IF EXISTS ?
                """
        for r in result:
            cur.execute(query, (r[0],))
            logger.debug(str(r[0]))
    if max_time is None:
        max_time = pandas.to_timedelta(Data.config_guild_get(str(ctx.guild_id), (category, 'dataretention', 'total'))).to_pytimedelta()
    #TODO get index_guild working
    
    channels = await guild.get_channels()
    for channel_id in channels:
        messageIterator = Data.bot.rest.fetch_messages(channels[channel_id])
        
    
    members = set()
    
    cur.connection.close()

async def index_channel(channel:hikari.TextableGuildChannel, users:set, max_time:datetime.timedelta, replace:bool=False):
    channel


group = commands.Group('activity', 'the commands for the Activity extensions')

@group.register
class Index_CMD(
    commands.SlashCommand,
    name="index-activity",
    description="registers all new activity in the guild",
    hooks=[commands.prefab.has_permissions(hikari.Permissions.ADMINISTRATOR)],
):
    max_time = commands.integer("days", "how many days back the bot will index", default=-1)
    replace = commands.boolean("replace", 'whether to replace the old data', default=False)

    @commands.invoke
    async def invoke(self, ctx: commands.Context, bot:hikari.GatewayBot) -> None:
        await ctx.respond('not implemented yet')
        return
        
        response = await ctx.respond("indexing your server. this may take a bit...")
        try:
            await index_guild(ctx.member.get_guild(), self.max_time, self.replace)
            await ctx.edit_response(response, "Server indexed successfully")
        except:
            await ctx.edit_response(response, "Something went wrong")

@group.register
class index_all_CMD(
    commands.SlashCommand,
    name="index-all",
    description="goes through the entire guild and saves the activity",
    hooks=[commands.prefab.owner_only],
):
    @commands.invoke
    async def execute_for_all_guilds(self, ctx:commands.Context, bot: hikari.GatewayBot, client: commands.Client) -> None:
        await ctx.respond('not implemented yet')
        return
    
    
        for guild in Data.get_guilds(bot):
            logger.info(f"Indexing '{guild.name}' now")
            await index_guild(guild)

@loader.listener(hikari.StartedEvent)
async def onStarted(event:hikari.StartedEvent):
    logger.debug('starting activity updater')
    guilds_update_activity.start()

@loader.task(commands.uniformtrigger(seconds=update_frequency.seconds, wait_first=False), auto_start=False, max_failures=-1, max_invocations=-1)
async def guilds_update_activity(bot: hikari.GatewayBot, client: commands.Client) -> None:
    # call update_activity for all guilds
    logger.info('updating activities')
    
    async for guild in bot.rest.fetch_my_guilds():
        if not Data.config_guild_get(str(guild.id), (category, 'enabled',)):
            logger.debug(f"roles not enabled for {guild.name}, just pruning the db")
            prune_guild_db(str(guild.id))
            continue
        logger.debug(f"updating '{guild.name}' now")
        guild = await guild.fetch_self()
        await activity_guild_update(guild)
        
        


@loader.listener(hikari.GuildMessageCreateEvent)
async def message_activity(event: hikari.GuildMessageCreateEvent) -> None:
    Activity.from_event()
    
    
    if event.is_bot: return
    guild = event.get_guild()
    words = 1
    if event.content:
        words = Util.count_words(event.content)
    logger.debug(f"message activity: {words} words, content:\n{event.content}")
    liveupdate = Data.config_guild_get(str(event.guild_id), (category, 'updateOnEvent',))
    if not Data.config_guild_get(str(event.guild_id), (category, 'enabled',)): liveupdate = False
    await Activity(member=event.member, activity_type=ActivityType.MESSAGE, date=datetime.datetime.now(datetime.UTC), words=words).log(member_update=liveupdate)

@loader.listener(hikari.VoiceStateUpdateEvent)
async def voice_activity(event: hikari.VoiceStateUpdateEvent) -> None:
    if event.state.member.is_bot: return
    liveupdate = Data.config_guild_get(str(event.guild_id), (category, 'updateOnEvent',))
    if not Data.config_guild_get(str(event.guild_id), (category, 'enabled',)): liveupdate = False
    logger.debug(f"voice activity: {event.state} (old: {event.old_state})")
    if event.state.channel_id != None and event.old_state == None:
        await Activity(event.state.member, ActivityType.VOICE, datetime.datetime.now(datetime.UTC), description="join").log(member_update=liveupdate)
    if event.state.channel_id == None and event.old_state != None:
        await Activity(event.state.member, ActivityType.VOICE, datetime.datetime.now(datetime.UTC), description="leave").log(member_update=liveupdate)
    
@loader.listener(hikari.GuildReactionAddEvent)
async def reaction_activity(event: hikari.GuildReactionAddEvent) -> None:
    if event.member.is_bot: return
    liveupdate = Data.config_guild_get(str(event.guild_id), (category, 'updateOnEvent',))
    if not Data.config_guild_get(str(event.guild_id), (category, 'enabled',)): liveupdate = False
    await Activity(event.member, ActivityType.REACTION, datetime.datetime.now(datetime.UTC)).log(member_update=liveupdate)
    
@loader.listener(hikari.GuildTypingEvent)
async def typing_activity(event:hikari.GuildTypingEvent) -> None:
    if event.member.is_bot: return
    liveupdate = Data.config_guild_get(str(event.guild_id), (category, 'updateOnEvent',))
    if not Data.config_guild_get(str(event.guild_id), (category, 'enabled',)): liveupdate = False
    await Activity(event.member, ActivityType.TYPING, datetime.datetime.now(datetime.UTC)).log(member_update=liveupdate)

async def register_commands(guild_ids:list = []):
    if len(guild_ids) < 1:
        guilds_it = Data.bot.rest.fetch_my_guilds()
        async for guild in guilds_it:
            guild_ids.append(guild.id)
    loader.command(command=group, guilds=guild_ids)

# CHecklist: ----------------------------------

# # listeners: set up and working ( so far havent been able to reproduce database locked error)
# commands: 
#   - Lurk: working
#   - UnLurk: check if working
#
#   - get avtivity: not pretty, but working make output prettier, i guess
#   - Index: needs index_guild(cursor, guild, until_date) function
#   - index all: check if it works after index_guild(cusor, guild, until_date) is complete
#   other commands (maybe?):
#       - update_guild (update every member)
#       - update_user
#       - delete_data

# tasks:
#   - refresh_roles_all -> for every guild go through every member and refresh the activityrole (prune db, new role)
#       needs refresh_roles(guild) method

#   - index_catchup -> task run once after starting to index all guilds until last logged message
#       needs index_guild to work

# functions:

#   - index_all_guilds(bot) -> since i would need to write this twice, just write it once i guess

#   - index_guild() --- this should make its own cursor, not need one

#   - activity_member_update