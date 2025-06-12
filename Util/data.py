"""
provides utilities for default data. extensions may add to 
checks/creates Data structure on execution/import
"""

import os, sys
import tomlkit, tomllib
from pathlib import Path
import sqlite3
import requests
import shutil
import hikari
import lightbulb as commands
import logging

logger = logging.getLogger("data")
folder_data = "Data"
folder_guilds = "Guilds"
folder_misc = "Misc"
config_global = "config_global.toml"
config = "config.toml"

mode = "testing"
try:
    mode = sys.argv[1]
except:
    pass
# db structure:

"""
TODO:
    - methods to check for certain files/ initialize if missing
        - Data Directory
        - global config
        - Guilds directory
        - directory for each guild
        - guild config
    
        - guild db file?
        - better: DB directory -> one db per extension/purpose, table per guild
            not manually file-deleteable per guild though
                -> provide command and check to delete a guilds data in all db-s
            - extensions have to call ensure_db(name) themselves? no, connect() creates database if not exists
            
    - method for deleting all tables with name guild_id in all existing db files (no matter if extension loaded or not)
    
    - method to access db? -> goes in respective extension, not here
    
    - methods to access global settings
    
    - methods to access guild settings
"""
def download_file(filepath:str, url: str):
        """downloads a file to the given path

        Args:
            filepath (StrPath): the filepath including filename, in string form
            url (str): the url to the file that should be downloaded
        """
        logger.info(f"downloading file to {filepath}...")
        with open(filepath, "xb") as f:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                for block in response.iter_content(4096):
                        f.write(block)

async def check_guild_data(guilds:iter):
        """CHecks if the directories for the given guilds exist
        if given strings, just checks folder. If given other object, also tries to note down name

        Args:
            guilds (iter): iterable of variable types: guild_id strings or Guild objects
        """        
        async for id in guilds:
                name = "..."
                if type(id) != str:
                        try:
                                name = id.name
                                id = id.id
                        except:
                                id = str(id)
                guild_folder_path = os.path.join(".", folder_data, folder_guilds, str(id))
                Path(guild_folder_path).mkdir(parents=True, exist_ok=True)
                if not os.path.exists(os.path.join(guild_folder_path, config)):
                        logger.warn(f"config of guild {id} missing, restoring with default")
                        with open(os.path.join(guild_folder_path, config), 'a'):
                                pass
                else: logger.info(f"{id} config exists")
                
                with open(os.path.join(guild_folder_path, name), 'w') as f:
                        f.write("name: " + name)
                        f.write("\n")
                        f.write("id: " + str(id))

def get_guild_db(guild_id:str, db_name:str) -> (sqlite3.Connection):
        """returns the connection to the databank with db_name from the guild folder of the corresponding guild id

        Args:
            guild_id (*Snowflake): the id of the guild
            db_name (str): the db name without file extension
        """
        if type(guild_id) != str:
                try: guild_id = guild_id.id
                except: guild_id = str(guild_id)
        return sqlite3.connect(os.path.join(".", folder_data, folder_guilds, str(guild_id), db_name + ".db"))


def check_data_tree() -> None:
        
        Path(f"./{folder_data}/{folder_guilds}").mkdir(parents=True, exist_ok=True)
        Path(f"./{folder_data}/{folder_misc}").mkdir(parents=True, exist_ok=True)

        # if not os.path.exists(os.path.join(".", folder_data, "default_config_guild.toml")):
        #         logger.info("Default guild config missing, downloading...")
        #         download_file(os.path.join(".", folder_data, "default_config_guild.toml"), "https://raw.githubusercontent.com/FantasyDragon14/cyberdragon-bot/refs/heads/discord-python-hikari/Data/default_config_guild.toml")
        # else: logger.info("default_config_guild exists")

        # if not os.path.exists(os.path.join(".", folder_data, config_global)):
        #         logger.info("Global config missing, downloading...")
        #         download_file(os.path.join(".", folder_data, config_global), "https://raw.githubusercontent.com/FantasyDragon14/cyberdragon-bot/refs/heads/discord-python-hikari/Data/default_config_global.toml")
        # else: logger.info("config_global exists")
        
def member_table(member_id:str) -> str:
        """essentially just tacks 'id' in front of the given string, because table names have to begin with a letter

        Args:
            member_id (str): the members id

        Returns:
            str: the name of the table
        """
        return "id" + str(member_id)

def table_exists(cur:sqlite3.Cursor, table_name:str) -> bool:
        """Returns True if a table with the name table_name exists in the databank the given cursor is executing in
        False otherwise

        Args:
            cur (sqlite3.Cursor): cursor to the databank that should be checked
            table_name (str): name of the table

        Returns:
            bool: wether the table exists
        """        
        cur.execute("""--sql
                        SELECT EXISTS (
                                SELECT 
                                        name
                                FROM 
                                        sqlite_schema 
                                WHERE 
                                        type='table' AND name= ?
                        )
                    """, (table_name, ))
        result = cur.fetchall()
        logger.debug(f"checking if table {table_name} exists: {result[0] == (1,)}")
        return  result[0] == (1,)

async def get_guilds(bot: hikari.GatewayBot) -> hikari.LazyIterator:
        results = await bot.rest.fetch_my_guilds()
        return results

def settings_get(setting:str):
        #TODO set this up properly so it reads the settings file
        pass

def guildsettings_get(guild_id:str, setting:str):
        #TODO set this up properly so it reads the guilds settings file
        if 'activity' in setting:
                if "weight" in setting:
                        if "typing" in setting: return 0
                        if "reaction" in setting: return 1
                        if "lurking" in setting: return 1
                        if "voice" in setting: return 10
                        if "message" in setting: return 5
                if 'data_retention' in setting:
                        if 'total' in setting: return 30
                        if 'typing' in setting: return 5
                if 'live_update' in setting:
                        return True
        return None

def config_global_get(settingtree:tuple[str]):
        setting = None
        try:
                with open(os.path.join(folder_data, folder_misc, config_global), 'rb') as f:
                        toml = tomllib.load(f)
        except (FileNotFoundError):
                logger.warn(f'global config: file missing! Rebuild the config to avoid errors')
                return None
        subsetting = None
        try:
                for branch in settingtree:
                        subsetting = branch
                        setting = setting[branch]
        except (KeyError):
                logger.warn(f"global config: failed to find subsetting [{subsetting}] in setting [{setting}]")
                return None
        return setting
        
def config_guild_get(guild_id:str, category:str, settingtree:tuple[str]) -> str|None:
        """reads a guilds settings file and returns the value at [category][treesetting1][setting2]...
        """
        setting = None
        try:
                with open(os.path.join(folder_data, folder_guilds, str(guild_id), config), 'rb') as f:
                        toml = tomllib.load(f)
        except (FileNotFoundError):
                logger.warn(f'config [{guild_id}]: config file missing! Rebuild the config to avoid errors')
                return None
        try:
                setting = toml[category]
        except (KeyError):
                logger.warn(f"config [{guild_id}]: failed to find category [{category}]")
                return None
        subsetting_name = None
        setting_name = None
        try:
                for branch in settingtree:
                        subsetting_name = branch
                        setting = setting[branch]
                        setting_name = branch
        except (KeyError):
                logger.warn(f"config [{guild_id}]: failed to find subsetting [{subsetting_name}] in setting [{setting_name}]")
                return None
        return setting

def config_guild_set(guild_id:str, category:str, settingtree:tuple[str], value:str) -> str|None:
        """sets a value (string), returns old value.
        Creates a setting (with settingtree if it doesn't exist yet)
        
        Use for changing one string, not adding sections to the config
        """
        logger.debug('\n----- setting setting ------------')
        toml = tomlkit.document()
        try:
                with open(file, 'rb') as f:
                        toml = tomlkit.load(f)
        except (FileNotFoundError):
                logger.warn(f'config [{guild_id}]: config file missing! Rebuild the config to avoid errors')
                return None
        #Do stuff
        try:
                setting = toml[category]
        except (tomlKit.KeyError):
                logger.warn(f"config [{guild_id}]: failed to find category [{category}]")
                return None
        b = None
        for branch in settingtree[:-1]:
                try:
                        setting = setting[branch]
                except:
                        setting.add(branch, tomlkit.table())
                        setting = setting[branch]
        try:
                setting.add(settingtree[-1], value)
                old = None
        except:
                old = setting[settingtree[-1]]
                setting[settingtree[-1]] = value
        
        with open(file, 'w') as f:
                tomlkit.dump(toml, f)
        logger.debug('------ setting set ----------------')
        return old

"""
Plan: 
have a default config built by the extensions, then separate method to check/build config for every guild
-> compare with default config
config_default:tomlkit.Document()
"""

#check data tree once at startup
if __name__ == "__main__":
        print("not supposed to be run directly\n")
else:
        check_data_tree()