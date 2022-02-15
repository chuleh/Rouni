import os, asyncio, random, youtube_dl, discord
from discord.ext import commands, tasks
from pkg.cogs.sounds import Sounds
from dotenv import load_dotenv

# access discord token
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# create bot
subcommands = discord.Intents().all()
client = discord.Client(subcommands=subcommands)
ronald = commands.Bot(command_prefix='!r',subcommands=subcommands)

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

@ronald.command()
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} goes full ronald").format(ctx.message.author.name)
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@ronald.command(name='casquet')
async def casquet(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_clients.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("Ronald does not compute")


# start bot
ronald.run(DISCORD_BOT_TOKEN)
