'''
provides methods for saving and loading bot settings (in a json file)
'''
import os
from pathlib import Path
import json

#os.chdir(Path(os.path.dirname(__file__)).parent.absolute())
#os.chdir(Path(__file__).parent.absolute())

savingsfolder_name = 'Saving'
cogsFolder_name = 'Cogs'

def folders_ready():
        """checks if the reqired folders exist, creates them if needed
        """
        print("[SaveHandler] " + os.path.abspath(__file__))
        print("[SaveHandler] " + os.path.abspath(os.getcwd()))
        os.makedirs(savingsfolder_name, exist_ok=True)
        os.makedirs(cogsFolder_name, exist_ok=True)
                

        
#TODO: check if this actually works
def get_savefolder():
        return os.path.abspath(savingsfolder_name)

def get_cogsfolder():
        return Path(cogsFolder_name).absolute()
        
class Settings:
        
        settingsFile = 'settings.json'
        
        @staticmethod
        async def loadSettingsFile():
                raise NotImplementedError
        
        @staticmethod
        def createSettingsFile():
                raise NotImplementedError
        
        @staticmethod
        async def getSetting(guild, settingsExtension: str, settingname:str, defaultvalue = None):
                """provides the value of the setting with the given name.
                if the setting does not exist, it is created with the given defaultvalue

                Args:
                    settingsExtension (str): the name of the extension (each extension can define its own name)
                    settingname (str): the name of the setting
                    defaultvalue (_type_, optional):the default entry to the setting if it doesn't exist. Defaults to None.

                Returns:
                    _type_: the value of the setting-entry
                """
                #TODO
                settingvalue = True
                return settingvalue
        
        @staticmethod
        async def setSetting(guild, settingsExtension, settingname:str, newValue):
                """sets the value of the setting with the given name.
                if the setting does not exist, it is created with the given value

                Args:
                    settingsExtension (str): the name of the extension (each extension can define its own name)
                    settingname (str): the name of the setting
                    newValue (_type_): the value the setting should be set to

                Returns:
                    _type_: the old value of the setting-entry
                """
                #TODO
                oldvalue = False
                
                return oldvalue

if __name__ == "__main__":
        print("\n" * 3)
        folders_ready()