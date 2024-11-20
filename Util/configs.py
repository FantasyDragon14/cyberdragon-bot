import os
import tomlkit
from pathlib import Path

data_folder = "Data"
guilds_folder = "Guilds"
global_config = "config_global.json"
config = "config.json"

def ensure_config(guilds):
        """ensure the config files exist, create them if not
        """
        print(f"current directory: {os.path.abspath.__file__}")
        Path(f"./{data_folder}/{guilds_folder}").mkdir(parents=True, exist_ok=True)

def create_config_global():
        """create the global config file"""
        pass #TODO

def create_config_guild(guild_id):
        """create the config for a given guild

        Args:
            guild_id (string): the guild_id of the guild
        """
        Path(f"./{data_folder}/{guilds_folder}/{guild_id}").mkdir(parents=True, exist_ok=True)
        pass #TODO