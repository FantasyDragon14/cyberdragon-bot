const fs = require('node:fs');
const path = require('node:path');

//import { Client } from 'revolt.js'
//const { Client } = import('revolt.js')
const { Revolt_Client } = require('revolt.js');

require('dotenv').config()
//const { token } = require('./token_discord.txt');

const prefix = "!"

const revolt_rlient = new Client();


revolt_rlient.on("ready", async () => {
	console.info('[Revolt] logged in as ' + client.user.username);
        revolt_rlient.api.patch("/users/@me", { status: { text: "Testing...", presence: "Focus" } }); //status, presence can be: "Online" | "Idle" | "Focus" | "Busy" | "Invisible" | null | undefined // null | undefined leave unchanged
});

revolt_rlient.on("message", async (message) => {
        if (message.content === prefix + "ping") {
                message.channel.sendMessage("Pong!");
        }
});

revolt_rlient.loginBot(process.env.REVOLT_TOKEN);

