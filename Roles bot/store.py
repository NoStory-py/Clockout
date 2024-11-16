"""
# Get id Bot command
@tree.command(name="get_id", description="Get Player Id's")
async def get_id(interaction: discord.Interaction):
    print("Get id used")

    await interaction.response.defer()

    df = pd.read_csv("entries.csv")

    df['id'] = df['id'].astype(str)

    found = []

    for i, row in df.iterrows():
        for member in interaction.guild.members:
            
            if row['name'] == member.name or row['name'] == member.global_name or row['name'] == member.nick:
                print(row['name'], member.name, member.global_name, member.nick)
                if row['id'] == 'nan':
                    df.at[i, 'id'] = str(member.id)
                    found.append(row["name"])
                break

  
    df.to_csv("entries.csv", index=False)
    return await interaction.followup.send(f"Retrieved for: {", ".join(found)}")
"""
"""
import discord
from discord import app_commands
import os
import pandas as pd

TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {bot.user}')


@tree.command(name="customs_assign", description="Assign team roles")
async def customs_assign(interaction: discord.Interaction):

    print("customs_assign used")

    await interaction.response.defer()

    check_red = None
    team_magma = discord.utils.get(interaction.guild.roles, name='Team Magma')
    check_blue = None
    team_aqua = discord.utils.get(interaction.guild.roles, name='Team Aqua')
    magma_added = []
    aqua_added = []

    for x in interaction.guild.roles:
        if "Red: " in x.name:
            check_red = x
        elif "Blue: " in x.name:
            check_blue = x

    if check_blue is None and check_red is None:
        return await interaction.followup.send("Failed Coudnt find the Role Red: and Blue: , **Lobby isnt created yet.**")

    if check_red is not None:
        for member in check_red.members:
            await member.add_roles(team_magma)
            magma_added.append(member.nick if member.nick else member.name)

    if check_blue is not None:
        for member in check_blue.members:
            await member.add_roles(team_aqua)
            aqua_added.append(member.nick if member.nick else member.name)

    magma_chat = bot.get_channel(1175476709999526048)
    aqua_chat = bot.get_channel(1175476817440804974)
    # test magma_chat = bot.get_channel(1273275120391164007)
    # test aqua_chat = bot.get_channel(1273275140620156950)
   
    if magma_chat is not None:
        await magma_chat.send(f"{team_magma.mention} Private team chat!")
    if aqua_chat is not None:
        await aqua_chat.send(f"{team_aqua.mention} Private team chat!")
    
    return await interaction.followup.send(f"**Assigned Magma to:** {"**,** ".join(magma_added)}\n**Assigned Aqua to:** {"**,** ".join(aqua_added)}")


@tree.command(name="customs_remove", description="Remove team roles")
async def customs_remove(interaction: discord.Interaction):

    print("customs_remove used")

    await interaction.response.defer()
    team_magma = discord.utils.get(interaction.guild.roles, name='Team Magma')
    team_aqua = discord.utils.get(interaction.guild.roles, name='Team Aqua')
    magma_removed = []
    aqua_removed = []

    if team_magma.members is not None:
        for member in team_magma.members:
            await member.remove_roles(team_magma)
            magma_removed.append(member.nick if member.nick else member.name)
    if team_aqua.members is not None:
        for member in team_aqua.members:
            await member.remove_roles(team_aqua)
            aqua_removed.append(member.nick if member.nick else member.name)

    return await interaction.followup.send(f"**Removed Magma from:** {"**,** ".join(magma_removed)}\n**Removed Aqua from:** {"**,** ".join(aqua_removed)}")

bot.run(TOKEN)
"""
"""
import os
import disnake
from disnake.ext import commands

TOKEN = os.getenv("BOT_TOKEN")

intents = disnake.Intents.default()
intents.members = True
command_sync_flags = commands.CommandSyncFlags.default()
command_sync_flags.sync_commands_debug = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents, command_sync_flags=command_sync_flags)

queue = []

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

class QueueView(disnake.ui.View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label="Join Queue", style=disnake.ButtonStyle.green)
    async def join_queue(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        user_id = interaction.user.id
        if user_id in queue:
            await interaction.response.send_message("You're already in the queue!", ephemeral=True)
        else:
            queue.append(user_id)
            await interaction.response.send_message("You've joined the queue!", ephemeral=True)
            await self.update_queue_message(interaction)

    @disnake.ui.button(label="Leave Queue", style=disnake.ButtonStyle.red)
    async def leave_queue(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        user_id = interaction.user.id
        if user_id in queue:
            queue.remove(user_id)
            await interaction.response.send_message("You've left the queue.", ephemeral=True)
            await self.update_queue_message(interaction)
        else:
            await interaction.response.send_message("You're not in the queue.", ephemeral=True)

    async def update_queue_message(self, interaction: disnake.MessageInteraction):
       
        current_queue_members = self.get_queue_members()
        await interaction.channel.send(f"Click the buttons to join or leave the queue. Current queue: {current_queue_members}")

    def get_queue_members(self):
       
        if not queue:
            return "No one is in the queue."
        # Get usernames for the members in the queue
        members = [f"<@{user_id}>" for user_id in queue]
        return ", ".join(members)

@bot.slash_command(description="Start Customs Queue", dm_permission=False)
async def start(inter: disnake.ApplicationCommandInteraction):
    view = QueueView()  # Initialize the view
    initial_message = await inter.response.send_message(
        f"Click the buttons to join or leave the queue. {view.get_queue_members()}", view=view
    )

@bot.slash_command(description="Assign team roles", dm_permission=False)
async def customs_assign(inter):

    print("customs_assign used")

    await inter.response.defer()

    check_red = None
    team_magma = disnake.utils.get(inter.guild.roles, name='Team Magma')
    check_blue = None
    team_aqua = disnake.utils.get(inter.guild.roles, name='Team Aqua')
    magma_added = []
    aqua_added = []

    for x in inter.guild.roles:
        if "Red: " in x.name:
            check_red = x
        elif "Blue: " in x.name:
            check_blue = x

    if check_blue is None and check_red is None:
        return await inter.followup.send("Failed Coudnt find the Role Red: and Blue: , **Lobby isnt created yet.**")

    if check_red is not None:
        for member in check_red.members:
            await member.add_roles(team_magma)
            magma_added.append(member.nick if member.nick else member.name)

    if check_blue is not None:
        for member in check_blue.members:
            await member.add_roles(team_aqua)
            aqua_added.append(member.nick if member.nick else member.name)

    # og magma_chat = bot.get_channel(1175476709999526048)
    # og aqua_chat = bot.get_channel(1175476817440804974)
    magma_chat = bot.get_channel(1273275120391164007)
    aqua_chat = bot.get_channel(1273275140620156950)
   
    if magma_chat is not None:
        await magma_chat.send(f"{team_magma.mention} Private team chat!")
    if aqua_chat is not None:
        await aqua_chat.send(f"{team_aqua.mention} Private team chat!")
    
    await inter.followup.send(f"**Assigned Magma to:** {"**,** ".join(magma_added)}\n**Assigned Aqua to:** {"**,** ".join(aqua_added)}")

@bot.slash_command(description="Remove team roles", dm_permission=False)
async def customs_remove(inter):

    print("customs_remove used")

    await inter.response.defer()
    team_magma = disnake.utils.get(inter.guild.roles, name='Team Magma')
    team_aqua = disnake.utils.get(inter.guild.roles, name='Team Aqua')
    magma_removed = []
    aqua_removed = []

    if team_magma.members is not None:
        for member in team_magma.members:
            await member.remove_roles(team_magma)
            magma_removed.append(member.nick if member.nick else member.name)
    if team_aqua.members is not None:
        for member in team_aqua.members:
            await member.remove_roles(team_aqua)
            aqua_removed.append(member.nick if member.nick else member.name)

    await inter.followup.send(f"**Removed Magma from:** {"**,** ".join(magma_removed)}\n**Removed Aqua from:** {"**,** ".join(aqua_removed)}")

bot.run(TOKEN)

"""
"""
@bot.slash_command(description="Get non_members", dm_permission=False)
async def get_non_members(inter: disnake.ApplicationCommandInteraction):
    
    print("non-members used")
    
    await inter.response.defer()

    non_members = []
    
    for member in inter.guild.members:
        if not any(role.name == "Members" for role in member.roles):
            non_members.append(member.name)

    await inter.followup.send("**,** ".join(non_members))
"""