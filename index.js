//import { Client } from "revolt.js";
import { Client } from "revolt.js";

import dotenv from 'dotenv';
dotenv.config();

let prefix = "!";

// Create a new client instance
let revolt_client = new Client();

// Once your client is ready, this code will be executed (only once)
revolt_client.on("ready", async () => {
    console.info(`Logged in as ${revolt_client.user.username}!`); // This returns "Logged in as *Your bot's name*!" in the console
    revolt_client.api.patch("/users/@me", { status: { text: "Testing...", presence: "Online" } }); //status, presence can be: "Online" | "Idle" | "Focus" | "Busy" | "Invisible" | null | undefined // null | undefined leave unchanged
});

revolt_client.on("messageCreate", async (message) => {
    if (message.content === "hello") {
      message.channel.sendMessage("world");
    }
  });

// Log in to Revolt with your client's token
revolt_client.loginBot(process.env.REVOLT_TOKEN);