#discord.py
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import enum

#nsfw modules
import PIL.Image as Image
from nsfw_detector.model import Model

#other
from requests import get
import os
import traceback

# Load Blacklisted IDs
def blacklistedids(file="./blacklist.csv"):
    try:
        with open(file, 'rt') as f:
            return [int(i.strip()) for i in f.read().split(",") if i.strip()]
    except FileNotFoundError:
        return []

async def system(cmd):
    await asyncio.create_subprocess_shell(
    cmd,
    stdout=asyncio.subprocess.DEVNULL,
    stderr=asyncio.subprocess.DEVNULL
    )

nsfwcount = 0
blackfile = "./blacklist.csv"
blocked = blacklistedids(blackfile)
bot_owner = None
last_interaction_user = None
nsfwthreshold = 0.2
# Bot Setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user == bot_owner

# Slash Commands
@bot.tree.command(
    name="suggest",
    description="Suggest a bot to be added to blacklist"
    )
async def suggest(interaction: discord.Interaction, bot_id: str):
    botid = int(bot_id)
    if botid < 500000 or botid == bot_owner.id:
        await interaction.response.send_message("Not funny lil bro",
                                                ephemeral=True
                                                )
    if botid in blocked:
        await interaction.response.send_message("bot is already in the blacklist",
                                                ephemeral=True
                                                )
    else:
        with open("./suggestions.txt", "at") as f:
            f.write(str(bot_id) + "\n")
            await bot_owner.send(bot_id)
            await interaction.response.send_message(
                f"Added bot id: {bot_id} to suggestions.txt", ephemeral=True
            )

class managementcomm(enum.Enum):
    add = 1

@bot.tree.command(
    name="bm",
    description="owner only"
    )

@app_commands.check(is_owner)
async def add(interaction: discord.Interaction, sel: managementcomm,  snow: str):
    if interaction.user != bot_owner:
        await interaction.response.send_message(
            f"this is for owner only and your not them",
            ephemeral=True
        )
    else:
        match sel.value:
            case 1:
                botid = int(snow)
                if botid < 500000:
                    await interaction.response.send_message("Not funny lil bro",
                                                        ephemeral=True
                                                        )
                if botid in blocked:
                    await interaction.response.send_message("bot is already in the blacklist",
                                                            ephemeral=True
                                                            )

                    with open(blackfile, "at") as f:
                        f.write("," + str(snow))

                await interaction.response.send_message(
                    f"Added bot id: {snow} to blacklist.csv"
                )

@bot.tree.command(
    name="status",
    description="Check bot status"
    )
async def status(interaction: discord.Interaction):
    await interaction.response.send_message("Online ✅",
                                            ephemeral=True
                                            )

@bot.tree.command(
    name="remall",
    description="deletes all messages")
async def remall(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.guild_permissions.manage_messages:
        def isbyuser(m):
            return m.author == user
        
        deleted = await interaction.channel.purge(limit=200, check=isbyuser)
        await interaction.response.send_message(
            f'Deleted {len(deleted)} message(s)',
            ephemeral=True)
    else:
        await interaction.response.send_message(
            "You dont have permission to use this command",
            ephemeral=True)

@bot.tree.command(
    name="purge",
    description="Purges all messages")
async def purge(interaction: discord.Interaction):
    if interaction.user.guild_permissions.manage_messages:
        deleted = await interaction.channel.purge(limit=200)
        await interaction.response.send_message(
            f'Purged {len(deleted)} message(s)',
            ephemeral=True)
    else:
        await interaction.response.send_message(
            "You dont have permission to use this command",
            ephemeral=True
            )


@bot.tree.command(
    name="sourcecode",
    description="returns the bots source code"
    )
async def sc(interaction: discord.Interaction):
    await interaction.response.send_message(
        "https://github.com/oghatmake1/oghm-bot", 
        ephemeral=True)

# Events
@bot.event
async def on_ready():
    global bot_owner
    await bot.tree.sync()
    app_info = await bot.application_info()
    bot_owner = app_info.owner
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')

@bot.event
async def on_member_join(member):
    if member.id in blocked and member.bot and member.id != ctx.guild.owner_id:
        await member.guild.owner.send(
            f"Kicked a possible raid bot ({member}) — check audit logs"
        )
        await member.kick(reason="Possible Raid Bot")

@bot.event
async def on_message(message):
    # Ignore messages from self
    if message.author != bot.user:
        user = message.author

        # Delete blocked bot messages
        if user.id in blocked and user.bot and user.id != message.guild.owner_id:
            await message.delete()

        # Audit chain of replies
            suspects = [user]
            temp = message.reference
            while temp and temp.resolved:
                original = temp.resolved
                if original.author not in suspects and original.id != message.guild.owner_id:
                    suspects.append(original.author)
                temp = original.reference
                suspects.append(last_interaction_user)
            if suspects:
                owner = message.guild.owner
                await owner.send(
                    "Possible raid bot detected. suspect(s): " +
                    ", ".join(f"{u.name} ({u.id})" for u in suspects) +
                    f" prime suspect: " + str(last_interaction_user.id)
                )
                await bot_owner.send(
                    "Possible raid bot detected. suspect(s): " +
                    ", ".join(f"{u.name} ({u.id})" for u in suspects) +
                    f" prime suspect: " + str(last_interaction_user.id)
                 )

    if message.attachments and not message.channel.nsfw:
        net = Model()
        for i in message.attachments:
            ext = i.url.split(".")[-1].split("?")[0].lower()
            filename = "temp"+"."+ext
            prename = "sdlkajhch.dfsaojlnjkcxzzxclzxjknn"
            newext = ".jpg"
            match ext:
                case ("gif" | "apng" | "webp" | "avif" | "heif" | "heic" | "mng" | "jxl" | "tiff"):
                    await system(f'ffmpeg -i {filename} -vf "scale=128:128,tile=8x8" -frames:v 1 {filename}{newext}')
                    prename = filename
                    filename += newext
                case ("mp4" | "mkv" | "avi" | "mov" | "webm" | "flv" | "mpeg" | "mpg" | "3gp" | "ogv" | "ts" | "m2ts"):
                    await system(f'ffmpeg -i {filename} -vf "scale=128:128,tile=99x99" -frames:v 1 {filename}{newext}')
                    prename = filename
                    filename += newext
                case _:
                    prename = filename
                    
            with open(filename, "w+b") as f:
                f.write(get(i.url).content)
                try:
                    if f.read() == open("pp.png", "rb").read():
                        await message.delete()
                    elif f.read() == open("ppsamp.png", "rb").read():
                        await message.delete()
                except FileNotFoundError:
                    pass
            results = net.predict(filename)
            try:
                if results[filename]['Score'] >= nsfwthreshold:
                    await message.delete()
                    if message.guild.id != 1483236925509865552: # this is the test server
                        nsfwcount += 1
                        with open("stats", "w+b"):
                            f.write(str(nsfwcount))
            except KeyError:
                pass
            print(results)
            os.remove(filename)
            try:
                os.remove(prename)
            except FileNotFoundError:
                pass
    #match message.content:
    await bot.process_commands(message)



@bot.event
async def on_error(event_method, *args, **kwargs):

    # Get bot owner
    app_info = await bot.application_info()

    # Format the traceback
    tb = traceback.format_exc()

    # Send a DM to the bot owner
    try:
        await bot_owner.send(
            f"Error in event `{event_method}`:\n```\n{tb}\n```"
            )
    except Exception as e:
        print(f"Failed to DM bot owner: {e}")

    # Optional: print locally too
    print(f"Error in event {event_method}:\n{tb}")

async def on_interaction(interaction: discord.Interaction):
    global last_interaction_user
    last_interaction_user = interaction.user


bot.run(open("./token", "rt").read())
