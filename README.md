# Clockout

This repository contains internal tools for **ClockOut**, a Pokémon Unite squad. The main utility is a Discord bot used to manage custom game lobbies by assigning team roles and creating private team chats for organized play.

## About ClockOut

ClockOut is a squad focused on custom match experience. This repository supports those goals by providing discord bot commands that streamline the process of:
- Moving players into teams based on existing lobby roles.
- Creating temporary team roles ('Magma', 'Aqua').
- Notifying players and setting up team chats automatically.
- Choosing a first pick team (team that will pick first in draft)

## Key Features

- Discord bot built with Disnake.
- Custom slash commands for assigning and removing team roles.
- MongoDB-backed config storage (per guild).
- Support for randomized first-pick announcement.
- Team-based chat channels and pings.

## Important Disclaimer

This bot **requires another system-generated setup**. Specifically:
- It expects players to already be grouped using roles named 'Red: something' and 'Blue: something'.
- These roles are **not created by this bot**. They must be set up by another bot or a manual process beforehand.
- The 'customs_assign' command **reads** from these roles and assigns players into predefined teams.

This means the bot **won't work** without a compatible setup in your Discord server.


## Setup

You are free to clone and run the project for learning or development purposes.
- git clone https://github.com/NoStory-py/clockout.git
- setup .env file containing TOKEN, MONGO_URI
- pip install -r requirements.txt
- python app.py
