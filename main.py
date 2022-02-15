'''
Rouni: el bot más cajetilla de todo Discord
'''

import os, asyncio, random, youtube_dl, discord
from discord.ext import commands, tasks
from pkg.cogs.sounds import Sounds
from dotenv import load_dotenv

# access discord token
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# client
client = discord.Client()

# create bot
ronald = commands.Bot(command_prefix='!r', subcommand=None)

# sound cog
ronald.add_cog(Sounds(ronald))

# main
@ronald.event
async def on_ready():
    print('Ronald has become self-aware')

@ronald.command()
async def casquet(ctx):
    for client in ronald.voice_clients:
        await client.disconnect(force=True)

ronald.run(os.environ['DISCORD_BOT_TOKEN'])