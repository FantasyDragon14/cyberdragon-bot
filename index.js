/*
//import { Revolt_Client } from 'revolt.js';
//const { Revolt_Client } = import('revolt.js');
const { Revolt_Client } = require('revolt.js');

require('dotenv').config()
//const { token } = require('./token_discord.txt');

let prefix = "!"

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
*/




// Import the "Client" class from the revolt.js package

//import { Client } from "revolt.js";
import { Client } from "revolt.js";

//import 'dotenv'.config()

import dotenv from 'dotenv';
dotenv.config();

let prefix = "!"

// Create a new client instance
let client = new Client();

// Once your client is ready, this code will be executed (only once)
client.on("ready", async () => {
    console.info(`Logged in as ${client.user.username}!`); // This returns "Logged in as *Your bot's name*!" in the console
});

// Make the client (bot) send the "Pong!" message after you send a message with the content "!ping" into chat.
client.on("message", async (message) => {
    if (message.content === prefix + "ping") {
        message.channel.sendMessage("Pong!");
    }
});

// Log in to Revolt with your client's token
client.loginBot(process.env.REVOLT_TOKEN);