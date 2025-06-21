"""
classic starboard functionality. takes messages with star reactions and puts them in a special channel
"""
#make separate emoji for piping #shitposting to #memes 🏅
#   -> better if i just make another specific extension? memes.py
#-> ignore certain channels ()

import hikari
import lightbulb as commands
import logging
import tomlkit
from Util import data as Data

class Loader(commands.Loader):
    async def remove_from_client(self, client: commands.Client) -> None:
        #unload / close db connections here?
        logger.info('Removing starboard Extension')
        return await super().remove_from_client(client)
    async def add_to_client(self, client:commands.Client) -> None:
        logger.info('adding starboard extension')
        # await register_commands()
        await super().add_to_client(client)
        
loader = Loader()
logger = logging.getLogger("starboard")

category = 'starboard'
db_name = 'starboard'

guild_conf = {
    'enabled': False,
    'starboard_channel_id': '',
    'channel_blacklist': [],
    'reaction_emoji': '⭐'
}
guild_doc = tomlkit.item(guild_conf)
guild_doc['channel_blacklist'].comment("a list of id's.")
guild_doc['reaction_emoji'].comment("(custom) emoji id or the unicode emoji itself")

Data.default_config_guild_set(category, guild_doc)



"""Planning:

Save all starred messages id's in a db

save as:
starboardchannel message id (key): the id of the message the bot sent in the starboard channel
message_id: the id of the member message that was starred initially
points: the number of star reacts. Don't really need this if we're gonna read the reacts every time? what about messages that are not cached anymore? Gotta look it up

listen to reactionevents, filter for a specific emoji (could be set in guildsettings?)
read total number of star reacts every time, to update for removing reactions

listen to messagedelete events to remove an entry if one of the messages (starboard or source) is deleted
- automatically remove star reacts from source if starboard is deleted?
"""
