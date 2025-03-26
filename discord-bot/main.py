import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

WELCOME_CHANNEL_ID = 1346886957707427912  # Set to your provided channel ID

@bot.event
async def on_ready():
    print(f"👋 WelcomeBot is online as {bot.user}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(embed=discord.Embed(
            description=f"👋 Welcome {member.mention} to the server! 🎉",
            color=discord.Color.green()
        ))

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(embed=discord.Embed(
            description=f"💨 {member.name} just left the server. Goodbye!",
            color=discord.Color.red()
        ))

bot.run(os.environ["BOT_TOKEN"])
