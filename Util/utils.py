import random
import lightbulb
import re
import logging

logger = logging.getLogger('util')

dev_ids = [
    432248872845180932, #FantasyDragon14
    #944287847630921768, #eternalfloof
]
# @lightbulb.Check
# def check_dev(ctx: lightbulb.Context) -> bool:
#     return ctx.author.id in dev_ids
        
def split_message(s:str, maxchars:int=2000, separator="\n") -> list:
    maxchars = maxchars - int(maxchars*0.05)
    logger.debug("[MAXCHARS]: " + str(maxchars))
    messages = []
    msg = ""
    l = s.rsplit('\n')
    for p in l: #check for maxchars first? which is better? ...
        if len(p) > maxchars:
            raise Exception()
    for i, p in enumerate(l):
        if len(msg) + len(p) < maxchars:
            msg += p + "\n"
        else:
            messages.append(msg + "")
            msg = p + "\n"
    if len(msg) > 0: messages.append(msg)
    return messages
    
def count_words(s:str) -> int:
    """attempts to count how many words are in a string,
    by splitting on whitespace and excluding numbers

    Args:
        s (str): the input string

    Returns:
        int: how many words are in the string
    """
    i = 0
    words = s.split()
    for word in words:
        if not word.isnumeric():
            i += 1
    return i

def test():
    msg1 = "this is a very long paragraph, definitely.\nI'll have to set the maxchars very low for this to work\nbut maybe...\nidk what I'm gonna do\n"
    msg = "hu\nyeah"
    print("testing word counting:")
    msg = "one two three. I put 8 words in here\nsecond sentence has 4 words"
    result = count_words(msg)
    print("{", msg, "} has ", result, "words")
    
    
if __name__ == "__main__":
        print("not supposed to be run directly, just for some tests\n")
        test()
        pass
    