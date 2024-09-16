const fs = require('node:fs');
const path = require('node:path');

import { Revolt_Client } from 'revolt.js';
//const { Revolt_Client } = import('revolt.js');
//const { Revolt_Client } = require('revolt.js');

require('dotenv').config()
//const { token } = require('./token_discord.txt');

const prefix = "!"

let revolt_client = new Revolt_Client();


revolt_client.on("ready", async () => {
	console.info('[Revolt] logged in as ' + revolt_client.user.username);
        revolt_client.api.patch("/users/@me", { status: { text: "Testing...", presence: "Focus" } }); //status, presence can be: "Online" | "Idle" | "Focus" | "Busy" | "Invisible" | null | undefined // null | undefined leave unchanged
});

revolt_client.on("message", async (message) => {
        if (message.content === prefix + "ping") {
                message.channel.sendMessage("Pong!");
        }
});

revolt_client.loginBot(process.env.REVOLT_TOKEN);

