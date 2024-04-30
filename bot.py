import discord
from discord.ext import commands
import asyncio
import json
import os
import sys

# DEFINITIONS FOR MEMBER CHANNELS
async def update_member_channel(guild):
    channel_id = await get_member_channel_id(guild)
    if channel_id and (channel := guild.get_channel(channel_id)):
        await channel.edit(name=f"👤╏{guild.member_count} Members")

async def get_member_channel_id(guild):
    try:
        with open('member_channels.json', 'r') as file:
            return json.load(file).get(str(guild.id))
    except FileNotFoundError:
        return None

async def save_member_channel(guild_id, channel_id):
    try:
        with open('member_channels.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    data[str(guild_id)] = channel_id
    with open('member_channels.json', 'w') as file:
        json.dump(data, file)

async def create_or_update_member_channels():
    for guild in bot.guilds:
        channel_id = await get_member_channel_id(guild)
        if not channel_id or not guild.get_channel(channel_id):
            await create_member_channel(guild)
        else:
            await update_member_channel(guild)

async def create_member_channel(guild):
    channel = await guild.create_voice_channel(f"👤╏{guild.member_count} Members")
    await save_member_channel(guild.id, channel.id)
    print(f"added member counter in {guild.id}")

# DEFINITIONS FOR WELCOME AND RULES CHANNELS
async def setup_welcome_channel(guild):
    channel = await guild.create_text_channel('welcome')
    return channel.id

async def setup_rules_channel(guild):
    channel = await guild.create_text_channel('rules')
    return channel.id

async def send_welcome_message(member):
    with open('welcome_channels.json', 'r') as file:
        welcome_channels = json.load(file)
    if str(member.guild.id) in welcome_channels:
        welcome_channel_id = welcome_channels[str(member.guild.id)]
        welcome_channel = member.guild.get_channel(int(welcome_channel_id))
        if welcome_channel:
            rules_channel_id = await get_rules_channel_id(member.guild)
            if rules_channel_id:
                rules_mention = f"<#{rules_channel_id}>"
            else:
                rules_mention = "the rules channel"
            await welcome_channel.send(f"wsg {member.mention}! read the rules and verify in {rules_mention}!")

async def get_rules_channel_id(guild):
    try:
        with open('rules_channels.json', 'r') as file:
            return json.load(file).get(str(guild.id))
    except FileNotFoundError:
        return None

async def save_rules_channel(guild_id, channel_id):
    try:
        with open('rules_channels.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    data[str(guild_id)] = channel_id
    with open('rules_channels.json', 'w') as file:
        json.dump(data, file)

# CREATE NEEDED FILES
if not os.path.exists('welcome_channels.json'):
    with open('welcome_channels.json', 'w') as file:
        json.dump({}, file)
if not os.path.exists('rules_channels.json'):
    with open('rules_channels.json', 'w') as file:
        json.dump({}, file)
if not os.path.exists('member_channels.json'):
    with open('member_channels.json', 'w') as file:
        json.dump({}, file)
if not os.path.exists('balances.json'):
    with open('balances.json', 'w') as file:
        json.dump({}, file)
if not os.path.exists('config.json'):
    with open('config.json', 'w') as file:
        json.dump({}, file)

# DEFINITIONS FOR OTHER THINGS
def get_config():
    with open('config.json', 'r') as file:
        return json.load(file)

# BOT AND EVENTS
intents = discord.Intents.all()
intents.members = True

config = get_config()

bot = commands.Bot(
    command_prefix=config['prefix'],
    intents=intents,
    activity=discord.Activity(type=discord.ActivityType.listening, name="v1per 🤡"),
    status=discord.Status.idle
)

@bot.event
async def on_ready():
    print("bot is ready!")
    sys.path.append('./cogs')
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
    await create_or_update_member_channels()
    for guild in bot.guilds:
        with open('welcome_channels.json', 'r+') as file:
            welcome_channels = json.load(file)
            if str(guild.id) not in welcome_channels:
                channel_id = await setup_welcome_channel(guild)
                welcome_channels[str(guild.id)] = channel_id
                file.seek(0)
                json.dump(welcome_channels, file, indent=4)
        with open('rules_channels.json', 'r+') as file:
            rules_channels = json.load(file)
            if str(guild.id) not in rules_channels:
                channel_id = await setup_rules_channel(guild)
                rules_channels[str(guild.id)] = channel_id
                file.seek(0)
                json.dump(rules_channels, file, indent=4)

@bot.event
async def on_member_join(member):
    await create_or_update_member_channels()
    await send_welcome_message(member)

@bot.event
async def on_member_remove(member):
    await create_or_update_member_channels()

# START (ENTER TOKEN)
bot.run(config['token'])