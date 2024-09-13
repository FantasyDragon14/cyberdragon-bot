const fs = require('node:fs');
const path = require('node:path');

const { Client} = require('revolt.js');
require('dotenv').config()
//const { token } = require('./token_discord.txt');

const prefix = "!"

const client = new Client({ intents: [GatewayIntentBits.Guilds] });



client.on("ready", async () => {
	console.info('logged in as ' + client.user.username);
        client.api.patch("/users/@me", { status: { text: "Testing...", presence: "Focus" } }); //status, presence can be: "Online" | "Idle" | "Focus" | "Busy" | "Invisible" | null | undefined // null | undefined leave unchanged
});

client.on("message", async (message) => {
        if (message.content === prefix + "ping") {
                message.channel.sendMessage("Pong!");
        }
});

client.loginBot(process.env.REVOLT_TOKEN);

