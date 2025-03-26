import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix=".", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.command()
async def p(ctx):
    await ctx.send(file=discord.File("your-image.png"))  # Replace with your actual file name

bot.run(os.environ["BOT_TOKEN"])
