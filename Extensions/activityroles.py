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
import Extensions.activity as Activity

try: #adding Extensin-specific activity/status if status extension exists
    import Extensions.status as Status
    Status.activities.append(hikari.Activity(name="i can see you lurking ;3", type= hikari.ActivityType.CUSTOM))
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

db_name = "activity"
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

guild_doc['score'].comment('the scorepoints per logged activity of type. Score per message calculation ignores the value however (plan on changing that)')
guild_doc['time_weight'].comment('Format: ISO8601 timedelta - float pairs. weight of messages younger than timedelta. needs to be odered correctly')
guild_doc['level_score'].comment('minimum score required to reach a level (excluding lurking level). ignored by lurking (level -1)')
guild_doc['level_role'].comment('the discord role id for a certain level. will populate with default roles when left blank')
    
# Data.default_config_general_set(category, gen_doc)
Data.default_config_guild_set(category, guild_doc)



def calculate_weight(words):
    #TODO i may need to revise this formula some time
    return round(math.log10(0.5*words + 1) * 10)

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

group = commands.Group('activityroles', 'the commands for the ActivityRoles extensions')
@group.register
class Activity_update_CMD(
    commands.SlashCommand,
    name="update",
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

@loader.listener(Activity.ActivityUpdate)
async def update_roles(event: Activity.ActivityUpdate) -> None:
    #TODO
    pass      


async def register_commands(guild_ids:list = []):
    if len(guild_ids) < 1:
        guilds_it = Data.bot.rest.fetch_my_guilds()
        async for guild in guilds_it:
            guild_ids.append(guild.id)
    loader.command(command=group, guilds=guild_ids)
    loader.command(command=Unlurk_CMD, guilds=guild_ids)
    loader.command(command=Lurk_CMD, guilds=guild_ids)
