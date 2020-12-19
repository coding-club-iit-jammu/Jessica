import os
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv
from pymongo import MongoClient
from logs import log_emit

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
AUTHOR = int(os.getenv('AUTHOR'))
DEBUG = (os.getenv("DEBUG","") != "False" )

uri = os.getenv('MONGODB')
mongodb = MongoClient(uri)
db = mongodb['CodingClub']

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
        command_prefix='.',
        description='Jessica Ava`s Sister',
        case_insensitive=True,
        intents=intents
    )

async def give_role(member):
    roles = "Verified"
    try:
        verf_role = discord.utils.get(member.guild.roles, name=roles)
        await member.add_roles(verf_role)
    except:
        perms = discord.Permissions(send_messages=True, read_messages=True)
        await member.guild.create_role(name=roles, permissions=perms, mentionable = True)
        verf_role = discord.utils.get(member.guild.roles, name=roles)
        await member.add_roles(verf_role)

@bot.event
async def on_ready():
    global logs
    logs = log_emit(bot, DEBUG)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='Ava`s DB 💗'))
    print(f'{bot.user.mention} has connected to Discord!')

@bot.command()
async def hi(ctx):
    await ctx.send(f'{ctx.author.mention} Hi I Jessica Ava`s Sister')

@bot.command()
@commands.has_role('Mods')
async def leave(ctx):
    if(ctx.message.author.id != AUTHOR):
        return
    await bot.close()

@bot.event
async def on_member_join(member):
    log_channel = discord.utils.get(member.guild.channels, name = "logs")
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, Welcome to Coding Club IIT Jammu`s Competitive Coding Discord server.'
    )
    await logs.print(f'{member.mention} joined Server!', log_channel)
    user = db.member.find_one({'discordid' : f'{member.id}'},{'name':1, 'entry':1})
    if(user != None):
        await logs.print(f"```username: {member.mention} \nName: {user['name']} \nEntry No: {user['entry']}```", log_channel)
        await give_role(member)
        await logs.print(f'Roles given to {member.mention}', log_channel)
    else:
        await member.dm_channel.send(
            f'Please join Coding Club Main server and then rejoin this server'
        )
        await logs.print(f'Unable to verify {member.mention}', log_channel)

@bot.command()
@commands.has_role('Mods')
async def update(ctx):
    users = db.member.find({},{'_id':0,'name':1, 'entry':1, 'discordid' : 1})
    user_map = {}
    for i in users:
        user_map[i['discordid']] = i
    for member in ctx.guild.members:
        if(str(member.id) in user_map):
            await give_role(member)
    return await ctx.send("All member`s roles are updated")


@bot.command()
async def id(ctx):
    await ctx.send(f"{ctx.author.id}")

@bot.command()
@commands.has_role('Verified')
async def avatar(ctx, avamember : discord.Member=None):
    userAvatarUrl = avamember.avatar_url
    print(userAvatarUrl)
    await ctx.send(userAvatarUrl)    

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        msg_s = f"{ctx.author.mention} Invalid Command"
        await ctx.send(msg_s)
    else:
        raise error
bot.run(TOKEN)