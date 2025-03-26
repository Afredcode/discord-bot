import discord
from discord.ext import commands
from discord.utils import get
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

# Settings
WELCOME_CHANNEL_ID = 1346886957707427912
ALLOWED_ROLE_IDS = [1342429953916010526, 1338175441336533044]
TICKET_CATEGORIES = [1350919325070004266, 1350919300440915982]

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(embed=discord.Embed(
            description=f"👋 Welcome {member.mention} to **LeoneMC Chill Community**! Have a great time 🎉",
            color=discord.Color.green()
        ))

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(embed=discord.Embed(
            description=f"👋 **{member.name}** has left the server 💔",
            color=discord.Color.red()
        ))

@bot.command()
async def givewarning(ctx, member: discord.Member):
    author = ctx.author
    guild = ctx.guild

    if not any(role.id in ALLOWED_ROLE_IDS for role in author.roles):
        return await ctx.send(embed=discord.Embed(
            description="❌ You don't have permission to use this command.",
            color=discord.Color.red()
        ))

    await ctx.send(embed=discord.Embed(
        description="📩 Hello mod, we have sent you a DM.",
        color=discord.Color.blurple()
    ))

    try:
        await author.send(embed=discord.Embed(
            title="⚠️ Warning Confirmation",
            description=f"Are you sure you want to report **{member}**?
Type `yes` or `no`.",
            color=discord.Color.orange()
        ))
    except:
        return await ctx.send(embed=discord.Embed(
            description="❌ Could not DM you. Please enable DMs.",
            color=discord.Color.red()
        ))

    def check(m):
        return m.author == author and isinstance(m.channel, discord.DMChannel)

    try:
        reply = await bot.wait_for("message", check=check, timeout=60)
    except:
        return await author.send(embed=discord.Embed(
            description="⏰ Timed out. Please run the command again.",
            color=discord.Color.red()
        ))

    if reply.content.lower() != "yes":
        return await author.send(embed=discord.Embed(
            description="❌ Report canceled.",
            color=discord.Color.red()
        ))

    await author.send(embed=discord.Embed(
        title="📝 Offense Description",
        description="Please type the offense (you can write a full sentence).",
        color=discord.Color.gold()
    ))

    try:
        offense_msg = await bot.wait_for("message", check=check, timeout=180)
    except:
        return await author.send(embed=discord.Embed(
            description="⏰ Timed out. Please run the command again.",
            color=discord.Color.red()
        ))

    await author.send(embed=discord.Embed(
        title="🔒 Final Confirmation",
        description="Are you sure you want to send this to a ticket?
This can’t be undone.
Type `sure` or `cancel`.",
        color=discord.Color.red()
    ))

    try:
        confirm = await bot.wait_for("message", check=check, timeout=60)
    except:
        return await author.send(embed=discord.Embed(
            description="⏰ Timed out. Please run the command again.",
            color=discord.Color.red()
        ))

    if confirm.content.lower() != "sure":
        return await author.send(embed=discord.Embed(
            description="❌ Report canceled.",
            color=discord.Color.red()
        ))

    # Create ticket
    category = get(guild.categories, id=TICKET_CATEGORIES[0]) or get(guild.categories, id=TICKET_CATEGORIES[1])
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    ticket_channel = await guild.create_text_channel(
        name=f"court-{member.name}",
        overwrites=overwrites,
        category=category,
        topic=f"Warning issued by {author.name} against {member.name}"
    )

    embed = discord.Embed(
        title="⚖️ Court Case Started",
        description=(
            f"**Moderator:** {author.mention}
"
            f"**Accused:** {member.mention}
"
            f"**Offense:**
{offense_msg.content}"
        ),
        color=discord.Color.purple()
    )
    embed.set_footer(text="🧾 Please type your story in 1 sentence. If not, this will be closed and both get a warning.")

    await ticket_channel.send(content=f"{author.mention} {member.mention}", embed=embed)

@bot.command()
async def closecase(ctx):
    if ctx.channel.name.startswith("court-"):
        await ctx.send(embed=discord.Embed(
            description="🔒 Case closed. Thank you for attending court.",
            color=discord.Color.dark_gray()
        ))
        await ctx.channel.delete()
    else:
        await ctx.send(embed=discord.Embed(
            description="❌ This command can only be used inside a court ticket.",
            color=discord.Color.red()
        ))

bot.run(os.environ["BOT_TOKEN"])
