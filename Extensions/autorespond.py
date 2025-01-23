"""
automatically responds to messages and interactions in chat. Does not use commands for this behaviour
"""
import hikari
import lightbulb as commands
import re
import random

loader = commands.Loader()

@loader.listener(hikari.MessageCreateEvent)
async def on_message(event: hikari.MessageCreateEvent):
	if not event.is_human: return
	
	action = await parse_content(event.message.content)

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
	await event.app.rest.create_message(event.channel_id, msg)
	#TODO
	pass


async def parse_content(message):
	"""decides based on message content which function to execute

	#TODO does not distinguish reply, interaction, normal message so far

	Args:
		message (str): the content of the message

	Returns:
		function: the function to handle this message
	"""
	print("Parsing message:")
	print(message)
	if message is None: return
	#TODO do this properly with the right regex and shit
	if re.search(r"(^|\s+)h(i+|(a|e)llo)\W*([\s]|$)", message, re.I):
		return hello
	#TODO implement other reactions
	return None

#I'm probably gonna rewrite the whole thing for better paring and to detect and parse replies, mentions etc better