import discord
from discord.ext import commands
from discord.ui import View, Button
import os
import datetime

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents)

# IDs
TRAINEE_HELPER_ROLE_IDS = [1350919325070004266, 1350919300440915982]
HEAD_STAFF_ROLE_IDS = [1313584543088775218, 1313959293594107965, 1338599484019707975, 1342429953916010526]
WARNING_ROLES = [1346927598164508713, 1346927992940531763, 1346928093377331322, 1346928242514464798]
WARNING_LOG_CHANNEL_ID = 1346248603559006219

@bot.command()
async def warn(ctx, member: discord.Member = None, *, reason: str = None):
    if member is None or reason is None:
        return await ctx.send(embed=discord.Embed(
            description="❗ Please use the format: `.warn @user (reason)`",
            color=discord.Color.orange()
        ))

    trainee_helper = None
    for role in ctx.guild.roles:
        if role.id in TRAINEE_HELPER_ROLE_IDS:
            trainee_helper = role
            break

    if not trainee_helper:
        return await ctx.send("❌ No trainee/helper found.")

    class ConfirmView(View):
        def __init__(self):
            super().__init__(timeout=60)
            self.value = None

        @discord.ui.button(label="Sure", style=discord.ButtonStyle.green)
        async def sure(self, interaction: discord.Interaction, button: Button):
            self.value = True
            self.stop()

        @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
        async def cancel(self, interaction: discord.Interaction, button: Button):
            self.value = False
            self.stop()

    # Step 1: DM Trainee/Helper
    trainee_dm_sent = False
    for member_obj in ctx.guild.members:
        if any(role.id in TRAINEE_HELPER_ROLE_IDS for role in member_obj.roles):
            try:
                view = ConfirmView()
                embed = discord.Embed(
                    title="⚠️ Warning Request",
                    description=f"Do you approve warning {member.mention} for:
`{reason}`
By: {ctx.author.mention}?",
                    color=discord.Color.orange()
                )
                await member_obj.send(embed=embed, view=view)
                trainee_dm_sent = True
                await view.wait()
                if not view.value:
                    return await ctx.send(embed=discord.Embed(description="❌ Warning canceled by trainee/helper.", color=discord.Color.red()))
                break
            except:
                continue

    if not trainee_dm_sent:
        return await ctx.send("⚠️ No trainee/helper available to confirm.")

    # Step 2: DM Head Staff
    head_confirmed = False
    for head in ctx.guild.members:
        if any(role.id in HEAD_STAFF_ROLE_IDS for role in head.roles):
            try:
                view = ConfirmView()
                embed = discord.Embed(
                    title="⚠️ Final Warning Confirmation",
                    description=f"{ctx.author.mention} requested to warn {member.mention} for:
`{reason}`
Confirmed by trainee/helper. Do you confirm?",
                    color=discord.Color.red()
                )
                await head.send(embed=embed, view=view)
                await view.wait()
                if view.value:
                    head_confirmed = head
                    break
            except:
                continue

    if not head_confirmed:
        return await ctx.send("❌ No head staff confirmed the warning.")

    # Step 3: Apply warning role
    role = ctx.guild.get_role(WARNING_ROLES[0])
    await member.add_roles(role)

    now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    warn_embed = discord.Embed(
        title="⚠️ Warning Issued",
        description=(
            f"{member.mention} has been warned by {ctx.author.mention}
"
            f"Confirmed by: {head_confirmed.mention}
"
            f"Reason: {reason}
Time: {now}
"
            f"This will be saved for staff application review."
        ),
        color=discord.Color.orange()
    )

    await ctx.send(embed=warn_embed)
    log_channel = bot.get_channel(WARNING_LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(embed=warn_embed)

bot.run(os.environ["BOT_TOKEN"])
