import os
import disnake
from disnake.ext import commands
from random import choice

# environment variables
TOKEN = os.getenv("BOT_TOKEN")
MAGMA_CHAT = int(os.getenv("MAGMA_CHANNEL_ID"))
AQUA_CHAT = int(os.getenv("AQUA_CHANNEL_ID"))
TEAM_MAGMA = int(os.getenv("MAGMA_ROLE_ID"))
TEAM_AQUA = int(os.getenv("AQUA_ROLE_ID"))

# idk something
intents = disnake.Intents.default()
intents.members = True
command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents, command_sync_flags=command_sync_flags)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.slash_command(description="Assign team roles")
async def customs_assign(inter, random_first_pick:bool=False, lobby_id:int = 0 ):

    print("customs_assign used")

    await inter.response.defer()

    # Red: , Blue: roles
    check_red = None
    check_blue = None

    # Magma and Aqua roles
    team_magma = disnake.utils.get(inter.guild.roles, id=TEAM_MAGMA)
    team_aqua = disnake.utils.get(inter.guild.roles, id=TEAM_AQUA)

    # Magma and Aqua channels
    magma_chat = disnake.utils.get(inter.guild.channels, id=MAGMA_CHAT) 
    aqua_chat = disnake.utils.get(inter.guild.channels, id=AQUA_CHAT) 
    
    # Check for Red: , Blue: roles
    for x in inter.guild.roles:
        if "Red: " in x.name:
            check_red = x
        elif "Blue: " in x.name:
            check_blue = x

    # Assign Magma and Aqua
    if check_blue is None and check_red is None:
        return await inter.followup.send("Failed Coudnt find the Role Red: and Blue: , **Lobby isnt created yet.**")

    magma_added = []
    aqua_added = []

    async def assign(team, check, members_added):
        for member in check.members:
            await member.add_roles(team)
            members_added.append(member.nick if member.nick else member.name) 

    if check_red:
        await assign(team_magma, check_red, magma_added)
    if check_blue:
        await assign(team_aqua, check_blue, aqua_added)

    # channel message
    if random_first_pick == True:
        first_pick = choice([team_magma, team_aqua])
    else:
        first_pick = None

    async def channel_message(team, channel, first_pick, lobby_id):
        if first_pick:
            await channel.send(f"{team.mention} Private team chat!\n**First Pick: **{first_pick.mention}")
        else:
            await channel.send(f"{team.mention} Private team chat!")
        if lobby_id != 0:
            await channel.send(f"# Lobby id: {lobby_id}")
            await channel.send(lobby_id)

    if magma_added:
        await channel_message(team_magma, magma_chat, first_pick, lobby_id)
    if aqua_added:
        await channel_message(team_aqua, aqua_chat, first_pick, lobby_id)
    
    # Followup on the command
    return await inter.followup.send(f"**Assigned Magma to:** {", ".join(magma_added)}\n**Assigned Aqua to:** {", ".join(aqua_added)}")

@bot.slash_command(description="Remove team roles")
async def customs_remove(inter):

    print("customs_remove used")

    await inter.response.defer()

    # Magma and Aqua roles
    team_magma = disnake.utils.get(inter.guild.roles, id=1175474205815472209)
    team_aqua = disnake.utils.get(inter.guild.roles, id=1175474391937712139)

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
    return await inter.followup.send(f"**Removed Magma from:** {", ".join(magma_removed)}\n**Removed Aqua from:** {", ".join(aqua_removed)}")

bot.run(TOKEN)
