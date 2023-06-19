import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("MHBOT_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(intents=intents, command_prefix='!', case_insensitive=True)


class MyNewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page, title='HELP')
            await destination.send(embed=emby)


bot.help_command = MyNewHelp()


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('with the Minehut API'), status=discord.Status.online)
    print(f'Logged in/Rejoined as {bot.user} (ID: {bot.user.id})')
    print(
        f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=applications.commands%20bot")
    print('------ Error Log ------')


@bot.event
async def setup_hook():
    print('loading slash commands...')
    try:
        await bot.tree.sync(guild=None)
    except Exception as e:
        print(e)
    print("If you are seeing this then unseeyou's epic bot is working!")


@bot.hybrid_command(help='probably my ping')
async def ping(ctx: commands.Context):
    latency = round(bot.latency*1000, 2)
    message = await ctx.send("Pong!")
    await message.edit(content=f"Pong! My ping is `{latency} ms`")
    print(f'Ping: `{latency} ms`')


async def main():
    async with bot:
        await bot.load_extension("cogs.MHBOTCMDS")
        await bot.start(TOKEN)


asyncio.run(main())
