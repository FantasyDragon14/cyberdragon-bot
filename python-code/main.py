
from Bot import bot
import os
import bot_token

os.chdir(os.path.abspath(os.path.dirname(__file__)))

print ("bot starting...")


if __name__ == "__main__":
    print ("Hello ^^")

    print("(idk what I'm doing)")
    
    bot.run(bot_token.get_token())
    
