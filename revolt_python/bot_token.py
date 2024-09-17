import os

try:
        from dotenv import load_dotenv
        load_dotenv()
finally:
        pass


def get_token():
        token = os.getenv("REVOLT_TOKEN")
        if token == None:
                print("Environment-Variable 'REVOLT_TOKEN' not found. Trying to find a token in token_revolt.txt:")
                try:
                        with open("token_revolt.txt", 'r') as t:
                                token = t.read()
                except FileNotFoundError:
                        raise EnvironmentError("no token_revolt.txt found")
        print("found token")
        return token

if __name__ == "__main__":
        print("you're not supposed to execute this...")