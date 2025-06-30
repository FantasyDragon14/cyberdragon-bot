"""
assigns roles based on activity in the server

TODO: Split this up into two extensions: one seperate for activity logging (maybe save message and content too? Not sure how we'd use it except for activity roles...) , one for the role and activity score
So other extensions can use activity data aswell?
"""
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

try: #adding Extensin-specific activity/status if status extension exists
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
        logger.info('Removing ActivityRoles Extension')
        return await super().remove_from_client(client)
    
    async def add_to_client(self, client:commands.Client) -> None:
        logger.info('adding activityroles extension')
        await register_commands()
        await super().add_to_client(client)
        try:
            guilds_update_activity.start()
        except: logger.debug("didn't start activity updater")

loader = Loader()
logger = logging.getLogger("activityroles")

db_name = "activity_old"
category = "activityroles"
update_frequency = pandas.Timedelta(hours=1)
if mode == 'testing':
    update_frequency = pandas.Timedelta(minutes=5)

gen_conf = {
                'update_freq': pandas.Timedelta(hours=1).isoformat(),
            }
gen_doc = tomlkit.item(gen_conf)
gen_doc['update_freq'].comment('Format: ISO8601 timedelta. How much Time between general updates (db pruning, updates to inactive members without events)')

guild_conf = {
                'enabled': False,
                'updateOnEvent': True,
                'dataretention': {
                        'total': pandas.Timedelta(days=30).isoformat(),
                        'typing': pandas.Timedelta(days=5).isoformat(),
                },
                'score': {
                        'typing': 0,
                        'react': 1,
                        'voice': 10,
                        'message': 1,
                },
                'time_weight': {
                        pandas.Timedelta(days=2).isoformat(): 1.0, # younger than 2 days gets full weight
                        pandas.Timedelta(days=5).isoformat(): 0.9,
                        pandas.Timedelta(weeks=1).isoformat(): 0.75,
                        pandas.Timedelta(weeks=2).isoformat(): 0.5,
                        pandas.Timedelta(weeks=4).isoformat(): 0.25,
                        pandas.Timedelta(weeks=8).isoformat(): 0.0,
                        
                },
                'level_score': {
                        str(0): 0,
                        str(1): 1,
                        str(2): 100,
                        str(3): 200,
                        str(4): 1000,
                },
                'level_role': {
                    },
        }
guild_doc = tomlkit.item(guild_conf)
#doc['liveupdate'].comment('whether a members role should be updated as soon as activity is detected')
guild_doc['dataretention'].comment('Format: ISO8601 timedelta')
guild_doc['score'].comment('the scorepoints per logged activity of type. Score per message calculation ignores the value however (plan on changing that)')
guild_doc['time_weight'].comment('Format: ISO8601 timedelta - float pairs. weight of messages younger than timedelta. needs to be odered correctly')
guild_doc['level_score'].comment('minimum score required to reach a level (excluding lurking level). ignored by lurking (level -1)')
guild_doc['level_role'].comment('the discord role id for a certain level. will populate with default roles when left blank')
    
# Data.default_config_general_set(category, gen_doc)
Data.default_config_guild_set(category, guild_doc)

def calculate_weight(words):
    #TODO i may need to revise this formula some time
    return round(math.log10(0.5*words + 1) * 10)

class ActivityType(Enum):
    """The type of activity a user did. for sending a message, that's MESSAGE, etc
    Not to be confused by hikari.ActivityType
    """
    MESSAGE = 'msg'
    VOICE = 'vce'
    REACTION = 'rct'
    TYPING = 'typ'
    LURKING = 'lrk'
class Activity():
    type:ActivityType
    description:str
    guild:hikari.GatewayGuild|hikari.RESTGuild
    member:hikari.Member
    date:datetime.datetime
    words:int
    logged:bool

    def __init__(self, member:hikari.guilds.Member, type:ActivityType, date:datetime.datetime, description:str= "", words:int=0, guild:hikari.GatewayGuild |hikari.RESTGuild | None=None):
        """uh

        Args:
            member (hikari.guilds.Member): member who did it
            type (ActivityType): Type of activity
            date (datetime.datetime): the date and time the activity happened
            words (int, optional): Number of words if the ActivityType is MESSAGE. Defaults to 0.
            guild (hikari.GatewayGuild|hikari.RESTGuild, optional): we can get the guild from the member object, so idk why i even put this here. Defaults to None.
        """        
        if not guild: guild = member.get_guild()
        self.guild = guild
        self.member = member
        self.type = type
        self.description = description
        self.date = date
        
        self.words = words
        self.logged = False

    async def log(self, cursor:sqlite3.Cursor = None, member_update:bool = False):
        logger.debug(f"Attempting to log a {self.type.name} activity")
        if cursor is None: cur = Data.get_guild_db(self.guild.id, db_name).cursor()
        else: cur = cursor
        await ensure_member_table(cur, str(self.member.id))
        logger.debug('logging activity into table...')
        query = f"""--sql
                INSERT INTO {Data.member_table(str(self.member.id))} VALUES (
                    ?,
                    ?,
                    unixepoch(?),
                    ?
                )
                """
        cur.execute(query, (
            str(self.type.value),
            str(self.description),
            str(self.date),
            int(self.words),)
        )
        logger.debug('query executed, update role: ' + str(member_update))
        if member_update:
            await activity_member_update(cur, guild=self.guild, member=self.member)
        if cursor is None:
            cur.connection.commit()
            cur.connection.close()
        logger.debug("Activity logged")
        
async def assert_activty_roles(guild:hikari.GatewayGuild|hikari.RESTGuild, cur:sqlite3.Cursor):
    """makes sure one activityrole per level in the config exists:
    - does the saved role id exist in the guild? if not make new role and save it
    - does an activity level not have a role entry? create a new role and entry
    """
    level_score = Data.config_guild_get(str(guild.id), (category, 'level_score',))
    level_score = {int(key):level_score[key] for key in level_score.keys()}
    level_role = Data.config_guild_get(str(guild.id), (category, 'level_role',))
    level_role = {int(key):level_role[key] for key in level_role.keys()}
    level_score[-1] = None
    
    all_levels = list(level_score.keys())
    all_levels.sort()
    for level in all_levels:
        role_id = level_role.get(level)
        if role_id and guild.get_role(role_id):
            logger.debug(f'role for activitylevel {level} exists')
        else:
            logger.debug(f"activitylevel {level} role is not saved correctly, creating new")
            name = 'activitylevel ' + str(level)
            if level < 0: name = 'lurking'
            role = await Data.bot.rest.create_role(guild=guild, name=name, reason='new activityrole')
            Data.config_guild_set(str(guild.id), (category, 'level_role', str(level)), str(role.id))
            logger.debug(f'created role {str(role)}')
        
    #was that everything?
    

async def activity_member_update(cur: sqlite3.Cursor, guild: hikari.GatewayGuild|hikari.RESTGuild, member:hikari.Member, level_role:dict=None):
    """updates a members activity. this includes pruning the db, recalculating the activity level and score and reassigning the activity role if necessary
    """
    logger.debug(f"updating activity of {member.display_name}({member.id}) in guild {str(guild)}({guild.id})")
    max_time = pandas.to_timedelta(Data.config_guild_get(str(guild.id), (category, 'dataretention', 'total'))).to_pytimedelta()
    max_typing = pandas.to_timedelta(Data.config_guild_get(str(guild.id), (category, 'dataretention', 'typing'))).to_pytimedelta()
    prune_member_table(cur, Data.member_table(str(member.id)), max_time, max_typing)
    level, score, info = activity_calculation(cur, Data.member_table(str(member.id)), str(guild.id))
    if not level_role:
        level_role = Data.config_guild_get(str(guild.id), (category, 'level_role',))
    level_role = {int(level): level_role[level] for level in level_role.keys()} #Don't forget: the keys are initially strings
    members_roles = [str(role_id) for role_id in member.role_ids]
    
    logger.debug(f'wanted role: {level_role[level]}')
    for role in level_role.values():
        logger.debug(f'has role {role}? {role in members_roles}. Is role wanted? {role == level_role[level]}')
        if role != level_role[level]:
            
            if role in members_roles:
                await member.remove_role(role, reason='wrong activity role')
    
    if level_role[level] in members_roles:
        logger.debug('member already has correct role')
        return
    logger.debug("member doesn't have correct activityrole, clearing others")
    
    
    await member.add_role(level_role[level], reason='activity level changed')

async def activity_guild_update(guild:hikari.GatewayGuild|hikari.RESTGuild):
    cur = Data.get_guild_db(str(guild.id), db_name).cursor()
    
    await assert_activty_roles(guild, cur)
    level_role = Data.config_guild_get(str(guild.id), (category, 'level_role',))
    members = guild.get_members()
    for member_id in members:
        if members[member_id].is_bot: continue
        await activity_member_update(cur, guild, members[member_id], level_role)
    cur.connection.close()
    
    
    

def activity_calculation(cur:sqlite3.Cursor, member_table:str, guild_id:str, detail:bool=False) -> tuple:
    """calculates the activity level, score of a given members table

    Args:
        cur (sqlite:Cursor): cursor to a guilds databank
        member_table (str): name of the table to be interacted with
        guild_id (str): guild id for settings lookups

    Returns:
        level (int): activity level computed from activity score
        score (float): total computed activity score
        info (dict): a list of additional infos
    """
    #define default values:
    level = 0
    score = 0
    info = {
        'reactions': 0,
        'messages': 0,
        'voice joins/leaves': 0,
        'force lurk': False,
    }

    time_weight = Data.config_guild_get(guild_id, (category, 'time_weight',))
    if not time_weight: time_weight = guild_conf['time_weight']
    keys = [pandas.to_timedelta(k) for k in time_weight.keys()]
    keys.sort()
    timedelta_for_weights = {k: time_weight[k.isoformat()] for k in keys}
    
    level_score = Data.config_guild_get(guild_id, (category, 'level_score',))
    if not level_score: level_score = guild_conf['level_score']
    level_score = {int(level): level_score[level] for level in level_score.keys()}
    
    
    
    weight_typing = 0 # this will later also be settable by 
    weight_react = 1
    weight_voice = 10
    weight_message = calculate_weight
    
    query = """--sql
            SELECT EXISTS (
                SELECT name FROM sqlite_schema WHERE type='table' AND name=?
            )
            """
    cur.execute(query, (member_table,))
    result = cur.fetchall()
    if result[0] == (0,): return level, score, info #"dead by no table"
    else:
        query = f"""--sql
                SELECT EXISTS (
                    SELECT 1 FROM {member_table}
                )
                """
        cur.execute(query)
        result = cur.fetchall()
        logger.debug(result)
        if result[0] == (0,): return level, score, info #"dead by no activity in table"
    #test for lurking second
    
    #force lurk:
    query = f"""--sql
            SELECT EXISTS (
                SELECT 1 FROM {member_table} WHERE (
                    activity = ?
                )
            )
            """
    cur.execute(query, (ActivityType.LURKING.value,))
    result = cur.fetchall()
    logger.debug(result)
    if result[0] == (1,):
        level = -1 #"lurking by force"
        info['force lurk'] = True
    
    # non-force lurk (no msg/vce)
    query = f"""--sql
            SELECT EXISTS (
                SELECT 1 FROM {member_table} WHERE (
                    activity = ? OR activity = ?
                )
            )
            """
    cur.execute(query, (ActivityType.MESSAGE.value, ActivityType.VOICE.value))
    result = cur.fetchall()
    if result[0] == (0,): level = -1
    
    #now's the part we actually calculate a score
    query = f"""--sql
            SELECT activity, words, unixepoch(?) - unix_date FROM {member_table}
            """
    cur.execute(query, ('now',))
    result = cur.fetchall()
    timedelta_weight = []
    for r in result:
        if r[0] == ActivityType.TYPING.value:
            timedelta_weight.append((datetime.timedelta(seconds=r[2]), weight_typing))
            
        elif r[0] == ActivityType.REACTION.value:
            timedelta_weight.append((datetime.timedelta(seconds=r[2]), weight_react))
            info['reactions'] += 1
        elif r[0] == ActivityType.VOICE.value:
            timedelta_weight.append((datetime.timedelta(seconds=r[2]), weight_voice))
            info['voice joins/leaves'] += 1
            
        elif r[0] == ActivityType.MESSAGE.value:
            timedelta_weight.append((datetime.timedelta(seconds=r[2]), weight_message(r[1])))
            info['messages'] += 1
    
    # ---------- calculating final sum -------
    
    for delta, weight in timedelta_weight:
        for key in timedelta_for_weights.keys():
            if delta <= key:
                score += weight * timedelta_for_weights[key]
                break

    if level != -1: # set level for non-lurking
        for key in level_score.keys():
            if score <= level_score[key]:
                return level, score, info
            level = key
            
    
    return level, score, info

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
    #for pruning the dbs without updating any roles
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
                    desc text,
                    unix_date int,
                    words int
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

def unlurk(cur:sqlite3.Cursor, table_name:str):
    """Removes all lurk entries from a given databases table

    Args:
        cur (sqlite3.Cursor): cursor to the db
        table_name (str): the name of the table to unlurk
    """
        
    if mode == 'testing':
        query = f"""--sql
                SELECT * FROM {table_name} WHERE (
                    activity = ?
                )
                """
        cur.execute(query, (ActivityType.LURKING.value,))
        result = cur.fetchall()
        for r in result:
            logger.debug(str(r))

    query = f"""--sql
                DELETE FROM {table_name} WHERE (
                    activity = ?
                )
                """
    cur.execute(query, (ActivityType.LURKING.value,))
    cur.connection.commit()

group = commands.Group('activityroles', 'the commands for the ActivityRoles extensions')
            
@group.register
class Activity_update_CMD(
    commands.SlashCommand,
    name="update-activity",
    description="updates the activityroles",
    hooks=[commands.prefab.has_permissions(hikari.Permissions.ADMINISTRATOR)],
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context, bot:hikari.GatewayBot) -> None:
        await ctx.defer(ephemeral=True)
        if not Data.config_guild_get(str(ctx.guild_id), (category, 'enabled',)):
            ctx.respond('activity roles are disabled for this guild')
            return
        await activity_guild_update(ctx.member.get_guild())
        await ctx.respond('updated roles, purged databases')

class Lurk_CMD(
    commands.SlashCommand,
    name="lurk",
    description="sets your activity role to *lurking* for the given time",
):
    lurk_time = commands.number("days", "how many days you'll lurk")

    @commands.invoke
    async def invoke(self, ctx: commands.Context, bot:hikari.GatewayBot) -> None:
        await ctx.defer()
        logger.info(f"activating lurk mode for {ctx.member.display_name}")
        # try:
        interval = datetime.timedelta(days=self.lurk_time) #timedelta
        logger.debug(f"lurking for {interval}")
        lurk_end_date = datetime.datetime.now(datetime.UTC) + interval #datetime
        time_until_lurk_purged = pandas.to_timedelta(Data.config_guild_get(str(ctx.guild_id), (category, 'dataretention', 'total'))).to_pytimedelta() #timedelta
        correct_lurk_date = lurk_end_date - time_until_lurk_purged #datetime
        
        logger.debug(f"now: {datetime.datetime.now(datetime.UTC)}, lurk ends at {lurk_end_date}\
            \nlurk will purge in {time_until_lurk_purged}, that means date is {correct_lurk_date}")
        
        member = await ctx.member.fetch_self()
        lurk = Activity(member=member, type=ActivityType.LURKING, date=correct_lurk_date, description="force")
        await lurk.log(member_update=True)
        await ctx.respond(f"{ctx.member.mention} is just lurking", )
        # except:
        #     await ctx.respond("something went wrong. contact my dev")
        
class Unlurk_CMD(
    commands.SlashCommand,
    name="unlurk",
    description="removes the lurk",
):
    @commands.invoke
    async def invoke(self, ctx: commands.Context, bot:hikari.GatewayBot) -> None:
        await ctx.defer(ephemeral=True)
        cur = Data.get_guild_db(str(ctx.guild_id), db_name).cursor()
        
        if not Data.table_exists(cur, Data.member_table(str(ctx.member.id))):
            
            logger.debug("the table doesn't exist yet")
            
            liveupdate = Data.config_guild_get(str(ctx.guild_id), (category, 'updateOnEvent',))
            await Activity(ctx.member, ActivityType.TYPING, datetime.datetime.now(datetime.UTC)).log(member_update=liveupdate)
            await ctx.respond("the dead can't unlurk?? anyways you're now soft-lurking lol\n(to not be lurking you need to speak.)")
            return
        
        
        logger.debug(f"Deleting '{ActivityType.LURKING.value}' activities from table {Data.member_table(str(ctx.member.id))}:")
        
        unlurk(cur, Data.member_table(str(ctx.member.id)))
        
        guild = ctx.member.get_guild()
        
        await activity_member_update(cur, guild, ctx.member) 
        
        cur.connection.close()
        await ctx.respond("you are not force-lurked anymore\n-# you will still be lurking if you haven't talked tho")

@group.register
class get_activity_CMD(
    commands.SlashCommand,
    name="get-activity",
    description="gets the activity level and count of a given member",
):
    user = commands.user("user", "whose activity to return", default=None)
    detailed = commands.boolean("detailed", 'do you want a more detailed answer?', default=False)

    @commands.invoke
    async def invoke(self, ctx: commands.Context, bot:hikari.GatewayBot) -> None:
        await ctx.defer()
        if self.user is None: self.user = ctx.member
        cur = Data.get_guild_db(str(ctx.guild_id), db_name).cursor()
        level, score, info = activity_calculation(cur, Data.member_table(str(self.user.id)), str(ctx.guild_id), detail=self.detailed)
        msg = f"Activity of {self.user.mention}:\n\tlevel:" + ("lurking" if level == -1 else str(level)) + "\n\tscore:" + str(round(score))
        if self.detailed:
            msg += "\n\tInfos: " + str(info)
        
        if mode == 'testing':
            logger.debug('All Activity: --------------------------')
            query = f"""--sql
                    SELECT * FROM {Data.member_table(str(self.user.id))}
                    """
            cur.execute(query)
            
            for r in cur.fetchall():
                logger.debug(f"{r[0]}, {r[1]}, {datetime.datetime.fromtimestamp(r[2])}")
    
        cur.connection.close()
        await ctx.respond(msg, user_mentions=True)

@group.register
class Index_CMD(
    commands.SlashCommand,
    name="index-activity",
    description="goes through the entire guild and saves the activity",
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
    if event.is_bot: return
    guild = event.get_guild()
    words = 1
    if event.content:
        words = Util.count_words(event.content)
    logger.debug(f"message activity: {words} words, content:\n{event.content}")
    liveupdate = Data.config_guild_get(str(event.guild_id), (category, 'updateOnEvent',))
    if not Data.config_guild_get(str(event.guild_id), (category, 'enabled',)): liveupdate = False
    await Activity(member=event.member, type=ActivityType.MESSAGE, date=datetime.datetime.now(datetime.UTC), words=words).log(member_update=liveupdate)

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
    loader.command(command=Unlurk_CMD, guilds=guild_ids)
    loader.command(command=Lurk_CMD, guilds=guild_ids)

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