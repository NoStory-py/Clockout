import os
import sys
import disnake
from disnake.ext import commands
from random import choice
from asyncio import sleep
from pymongo import MongoClient

# environment variables
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

try:
    client = MongoClient(MONGO_URI)
    db = client["Guild"]
    collection = db["data"]
except ConnectionError as e:
    sys.exit("Database connection error")

# idk something
intents = disnake.Intents.default()
intents.members = True
command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents, command_sync_flags=command_sync_flags)

def load_config(guild_id):
    try:
        config = collection.find_one({"guild_id": str(guild_id)})
        return config if config else {}
    except Exception as e:
        return {}

def save_config(guild_id, new_config):
    try:
        collection.update_one({"guild_id": str(guild_id)}, {"$set": new_config}, upsert=True)
    except Exception as e:
        print("Update failed")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.slash_command(description="Set channel and roles", default_member_permissions=disnake.Permissions(administrator=True), guild_only=True)
async def setup(inter, announcement_channel: disnake.TextChannel, team_channel1: disnake.TextChannel, team_channel2: disnake.TextChannel, team_role1: disnake.Role, team_role2: disnake.Role):
    print("Setup used")

    await inter.response.defer()

    guild = inter.guild

    config = load_config(guild.id)

    config["guild_id"] = str(guild.id)
    config["announcement_channel"] = str(announcement_channel.id)
    config["team_channel1"] = str(team_channel1.id)
    config["team_channel2"] = str(team_channel2.id)
    config["team_role1"] = str(team_role1.id)
    config["team_role2"] = str(team_role2.id)

    save_config(guild.id, config)

    display_data = load_config(guild.id)

    for x in display_data:
        if "channel" in x:
            display_data[x] = disnake.utils.get(inter.guild.channels, id=int(display_data[x])).mention
        elif "role" in x:
            display_data[x] = disnake.utils.get(inter.guild.roles, id=int(display_data[x])).mention

    await inter.followup.send(f"Setup was completed: \n\n{"\n".join(f"**{key}**: {value}" for key, value in display_data.items() if key not in ["guild_id", "_id"])} \n\n- Make sure to give **send message permission** to the bot for **mentioned channels**.\n- Make sure that the bot role heirarchy is higher than the mentioned role (the role that its going to assign).\n- You can manage who can use the slash commands from integration settings (By default only admins can).")

@bot.slash_command(description="Assign team roles", default_member_permissions=disnake.Permissions(administrator=True), guild_only=True)
async def customs_assign(inter, random_first_pick:bool=False, lobby_id:int = 0 ):

    config = load_config(inter.guild.id)
    # Check if setup is done
    if not config:
        return await inter.response.send_message("Setup has not been completed yet. Please run the /setup command first.")

    print("customs_assign used")

    await inter.response.defer()

    # Red: , Blue: roles
    check_red = None
    check_blue = None

    # Magma and Aqua roles
    
    team_magma = disnake.utils.get(inter.guild.roles, id=int(config["team_role1"]))
    team_aqua = disnake.utils.get(inter.guild.roles, id=int(config["team_role2"]))

    # Magma and Aqua channels
    customs_chat = disnake.utils.get(inter.guild.channels, id=int(config["announcement_channel"]))
    magma_chat = disnake.utils.get(inter.guild.channels, id=int(config["team_channel1"]))
    aqua_chat = disnake.utils.get(inter.guild.channels, id=int(config["team_channel2"]))

    if not team_magma:
        return await inter.followup.send("Could not find the role1. Please update the config using /setup.")
    if not team_aqua:
        return await inter.followup.send("Could not find the role2. Please update the config using /setup.")
    if not customs_chat:
        return await inter.followup.send("Could not find the announcement channel. Please update the config using /setup.")
    if not magma_chat:
        return await inter.followup.send("Could not find channel1. Please update the config using /setup.")
    if not aqua_chat:
        return await inter.followup.send("Could not find channel2. Please update the config using /setup.")

    # Check for Red: , Blue: roles
    check_red = disnake.utils.find(lambda role: role.name.startswith('Red: '), inter.guild.roles)
    check_blue = disnake.utils.find(lambda role: role.name.startswith('Blue: '), inter.guild.roles)

    if check_blue is None and check_red is None:
        return await inter.followup.send("Failed Coudnt find the Role Red: and Blue: , **Lobby isnt created yet.**")

    # Assign Magma and Aqua
    magma_added = []
    aqua_added = []

    async def assign(team, check, members_added):
        for member in check.members:
            try:
                await member.add_roles(team)
                members_added.append(member.nick if member.nick else member.name) 
            except Exception as e:
                await inter.followup.send(
                    f"An unexpected error occurred while assigning roles: `{str(e)}`",
                    ephemeral=True
                )
    if check_red:
        await assign(team_magma, check_red, magma_added)
    if check_blue:
        await assign(team_aqua, check_blue, aqua_added)

    # Followup on the command
    await inter.followup.send(f"**Assigned Magma to:** {"**,** ".join(magma_added)}\n**Assigned Aqua to:** {"**,** ".join(aqua_added)}")

    # channel message
    async def channel_message(team, channel, lobby_id):
        if channel.guild != inter.guild:
            return await inter.followup.send(f"Not configured properly, use /setup again")
        if lobby_id != 0:
            await channel.send(f"{team.mention} Private team chat!\n# Lobby id: {lobby_id}")
            await channel.send(lobby_id)
        else:
            await channel.send(f"{team.mention} Private team chat!")  

    if magma_added:
        await channel_message(team_magma, magma_chat, lobby_id)
    if aqua_added:
        await channel_message(team_aqua, aqua_chat, lobby_id)
    
    # first pick:
    if random_first_pick == True:
        teams = [team_magma, team_aqua]
        first_pick = choice(teams)
        await sleep(25)
        await customs_chat.send(f"# Selecting a random first pick...")
        await sleep(5)
        await customs_chat.send(f"{first_pick.mention} is the first pick!\n||{teams[1].mention if first_pick == teams[0] else teams[0].mention} ^||")
        
@bot.slash_command(description="Remove team roles", default_member_permissions=disnake.Permissions(administrator=True), guild_only=True)
async def customs_remove(inter):

    config = load_config(inter.guild.id)
    # Check if setup is done
    if not config:
        return await inter.response.send_message("Setup has not been completed yet. Please run the /setup command first.")

    print("customs_remove used")

    await inter.response.defer()


    # Magma and Aqua roles
    team_magma = disnake.utils.get(inter.guild.roles, id=int(config["team_role1"]))
    team_aqua = disnake.utils.get(inter.guild.roles, id=int(config["team_role2"]))

    if not team_magma:
        return await inter.followup.send("Could not find the Magma role. Change the config using /setup.")
    if not team_aqua:
        return await inter.followup.send("Could not find the Aqua role. Change the config using /setup.")
        

    # Remove Magma and Aqua
    magma_removed = []
    aqua_removed = []

    async def remove(team, members_removed):
        for member in team.members:
            await member.remove_roles(team)
            members_removed.append(member.nick if member.nick else member.name)

    if team_magma.members:
        await remove(team_magma, magma_removed) 
    if team_aqua.members:
        await remove(team_aqua, aqua_removed)

    # Followup on the command
    return await inter.followup.send(f"**Removed Magma from:** {"**,** ".join(magma_removed)}\n**Removed Aqua from:** {"**,** ".join(aqua_removed)}")

if __name__ == "__main__":
    bot.run(TOKEN)
