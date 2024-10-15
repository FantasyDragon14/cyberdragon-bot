import random
        
def split_message(s:str, maxchars:int=2000, separator="\n") -> list:
    maxchars = maxchars - int(maxchars*0.05)
    print("[MAXCHARS]: " + str(maxchars))
    messages = []
    msg = ""
    l = s.rsplit('\n')
    #print("[printing l]")
    #print(l)
    for p in l: #check for maxchars first? which is better? ...
        if len(p) > maxchars:
            raise Exception()
    for i, p in enumerate(l):
    #    print(f"[DEBUG] checking msglen: {len(msg)} plen: {len(p)} (sum: {len(msg) + len(p)}|: {p}")
        if len(msg) + len(p) < maxchars:
            msg += p + "\n"
        else:
            messages.append(msg + "")
            msg = p + "\n"
    if len(msg) > 0: messages.append(msg)
    return messages
    
def test():
    msg = "this is a very long paragraph, definitely.\nI'll have to set the maxchars very low for this to work\nbut maybe...\nidk what I'm gonna do\n"
    msg = "hu\nyeah"
    for i in range(1):
        msg += f"{i}. \tusername |" + "Stuff"* random.randrange(2, 10) + "\n"
    print("testing split_message()")
    print(msg)
    newmsgs = split_message(msg, 200)
    print(newmsgs)
    print("\n\n\n")
    for m in newmsgs:
        print("_____[NEW_MESSAGE]________________")
        print(m)
        print("[END]")
    
    
if __name__ == "__main__":
        print("not supposed to be run directly, just for some tests\n")
        test()
        pass
    