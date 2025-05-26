"""
provides utilities for default data. extensions may add to 
checks/creates Data structure on execution/import
"""
if __name__ == "__main__":
        print("running standalone, checking data integrity...")

import os, sys
import tomlkit
from pathlib import Path
import sqlite3
import requests
import shutil
import hikari
import lightbulb as commands

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
        
        print(f"downloading file to {filepath}...")
        with open(filepath, "xb") as f:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                for block in response.iter_content(4096):
                        f.write(block)

async def check_guild_data(guild_ids:iter):
        """CHecks if the directories for the given guilds exist
        if given strings, just checks folder. If given other object, also tries to note down name

        Args:
            guild_ids (iter): iterable of variable types: guild_id strings or Guild objects
        """        
        async for id in guild_ids:
                name = ""
                if type(id) != str:
                        try:
                                name = id.name
                                id = id.id
                        except:
                                id = str(id)
                guild_folder_path = os.path.join(".", folder_data, folder_guilds, str(id))
                Path(guild_folder_path).mkdir(parents=True, exist_ok=True)
                if not os.path.exists(os.path.join(guild_folder_path, config)):
                        print(f"config of guild {id} missing, restoring with default")
                        with open(os.path.join(guild_folder_path, config), 'a'):
                                pass
                else: print(f"{id} config exists")
                
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

def build_guild_config():
        pass

def check_data_tree() -> None:
        
        Path(f"./{folder_data}/{folder_guilds}").mkdir(parents=True, exist_ok=True)
        Path(f"./{folder_data}/{folder_misc}").mkdir(parents=True, exist_ok=True)

        # if not os.path.exists(os.path.join(".", folder_data, "default_config_guild.toml")):
        #         print("Default guild config missing, downloading...")
        #         download_file(os.path.join(".", folder_data, "default_config_guild.toml"), "https://raw.githubusercontent.com/FantasyDragon14/cyberdragon-bot/refs/heads/discord-python-hikari/Data/default_config_guild.toml")
        # else: print("default_config_guild exists")

        # if not os.path.exists(os.path.join(".", folder_data, config_global)):
        #         print("Global config missing, downloading...")
        #         download_file(os.path.join(".", folder_data, config_global), "https://raw.githubusercontent.com/FantasyDragon14/cyberdragon-bot/refs/heads/discord-python-hikari/Data/default_config_global.toml")
        # else: print("config_global exists")
        
def member_table(member_id:str) -> str:
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
        if mode == "testing": print(f"checking if table {table_name} exists: ", result[0] == (1,))
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
        return None

#check data tree once at startup
if __name__ == "__main__":
        print("not supposed to be run directly, just for some tests\n")
else: check_data_tree()