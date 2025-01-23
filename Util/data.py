"""
provides utilities for data.
checks/creates Data structure on execution/import
"""
if __name__ == "__main__":
        print("running standalone, checking data integrity...")

import os
import tomlkit
from pathlib import Path
import sqlite3
import requests

data_folder = "Data"
guilds_folder = "Guilds"
db_folder = "DB"
global_config = "config_global.json"
config = "config.json"

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
def download_file(filename, url):
        print(f"downloading file to {filename}...")
        with open(filename, "xb") as f:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                for block in response.iter_content(4096):
                        f.write(block)

def check_data_tree() -> None:
        
        Path(f"./{data_folder}/{guilds_folder}").mkdir(parents=True, exist_ok=True)
        Path(f"./{data_folder}/{db_folder}").mkdir(parents=True, exist_ok=True)

        if not os.path.exists(f"./{data_folder}/default_config_guild.toml"):
                print("Default guild config missing, downloading...")
                download_file(f"./{data_folder}/default_config_guild.toml", "https://raw.githubusercontent.com/FantasyDragon14/cyberdragon-bot/refs/heads/discord-python-hikari/Data/default_config_guild.toml")
        else: print("default_config_guild exists")

        if not os.path.exists(f"./{data_folder}/default_config_global.toml"):
                print("Default global config missing, downloading...")
                download_file(f"./{data_folder}/default_config_global.toml", "https://raw.githubusercontent.com/FantasyDragon14/cyberdragon-bot/refs/heads/discord-python-hikari/Data/default_config_global.toml")
        else: print("default_config_global exists")

#check data tree once at startup
check_data_tree()