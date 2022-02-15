import os, asyncio, random
from discord.ext import commands
from pkg.cogs.sounds import Sounds
from dotenv import load_dotenv

# access discord token
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# create bot
ronald = commands.Bot(command_prefix='!')

# attach cogs
ronald.add_cog(Sounds(ronald))

def get_clips():
    return [filename[:filename.index(".")] for filename in os.listdir(RESOURCE_PATH)]

@ronald.event
async def on_ready():
    minTime = 1
    maxTime = 300
    print('Rouni has landed')
    await asyncio.sleep(random.randint(minTime, maxTime))
    if user.voice is not None:
        all_sounds = get_clips()
        channel = user.voice.channel
        random_sound = random.choice(all_sounds)
        await play_clip(channel, get_clip_file(random_sound))

@ronald.command()
async def unstuck(ctx):
    for client in ronald.voice_clients:
        await client.disconnect(force=True)

# start bot
ronald.run(DISCORD_BOT_TOKEN)
