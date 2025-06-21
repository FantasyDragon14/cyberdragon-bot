"""
automatically responds to messages and interactions in chat. Does not use commands for this behaviour
"""
import hikari
import lightbulb as commands
import re
import random
import logging

class Loader(commands.Loader):
    async def remove_from_client(self, client: commands.Client) -> None:
        #unload / close db connections here?
        logger.info('Removing autorespond Extension')
        return await super().remove_from_client(client)
    
    async def add_to_client(self, client:commands.Client) -> None:
        logger.info('adding autorespond extension')
        # await register_commands()
        await super().add_to_client(client)
        
loader = Loader()
logger = logging.getLogger("autorespond")

try: #adding Extensin-specific activity/status if status extension exists
    import Extensions.status as Status
    Status.activities.append(hikari.Activity(name="Hi everyone ^w^", type=hikari.ActivityType.CUSTOM),)
    Status.activities.append(hikari.Activity(name="Hello everynyan :3", type=hikari.ActivityType.CUSTOM),)
    Status.activities.append(hikari.Activity(name="say Hi :D", type=hikari.ActivityType.CUSTOM),)
except: pass

@loader.listener(hikari.MessageCreateEvent)
async def on_message(event: hikari.MessageCreateEvent, bot: hikari.GatewayBot):
	if not event.is_human: return
	
	action = await parse_content(event.message.content)
	me = bot.get_me()

	if me.id in event.message.user_mentions_ids:
		await event.message.add_reaction('👀')
	if action != None:
		await action(event)

hello_response = [
	"Hello!",
	"Hi!",
	"Hi ^^",
	"UwU",
	"Hello",
	"hello",
	"Hii~",
	"who *are* you?",
	"Hola!",
	"Greetings!",
	"o7",
	"hi...",
	"Hello!",
	"Hello :D",
	"nya~",
	"nice to see you :D",
	"hi (:",
	]
	

async def hello(event: hikari.MessageCreateEvent):
	"""called when the bot detects a message only saying a greeting

	Args:
		channel_id: the channel id to send the message to
	"""
	msg = random.choice(hello_response)
	await event.message.respond(msg, reply=event.message)
	pass


async def parse_content(message):
	"""decides based on message content which function to execute

	#TODO does not distinguish reply, interaction, normal message so far

	Args:
		message (str): the content of the message

	Returns:
		function: the function to handle this message
	"""
	logger.info("Parsing message:")
	logger.info(str(message))
	if message is None: return
	#TODO do this properly with the right regex and shit
	if re.search(r"(^|\s+)h(i+|(a|e)llo)\W*([\s]|$)", message, re.I):
		return hello
	#TODO implement other reactions
	return None

#I'm probably gonna rewrite the whole thing for better paring and to detect and parse replies, mentions etc better

#TODO: Rewrite this whole fucing module sometime to actually be usable instead of a gimmick