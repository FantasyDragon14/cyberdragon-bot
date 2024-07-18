import os


#from dotenv import load_dotenv
#load_dotenv()

def get_token():
        token = os.getenv("TOKEN")
        if token == None:
                print("Environment-Variable 'TOKEN' not found. Trying to find a token in token.txt:")
                try:
                        with open("token.txt", 'r') as t:
                                token = t.read()
                except FileNotFoundError:
                        raise EnvironmentError("no token.txt found")
        print("found token")
        return token

if __name__ == "__main__":
        print("you're not supposed to execute this...")