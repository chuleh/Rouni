'''
Rouni: el bot más cajetilla de todo Discord
'''

import os 
import asyncio
import random
import youtube_dl 
import discord
from discord.ext import commands, tasks
from pkg.cogs.sounds import Sounds
from dotenv import load_dotenv

# access discord token
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# create bot
ronald = commands.Bot(command_prefix='!r ', help_comm=None)

# sound cog
ronald.add_cog(Sounds(ronald))

# main
@ronald.event
async def on_ready():
    print("ready")

@ronald.command()
async def casquet(ctx):
    for client in ronald.voice_clients:
        await client.disconnect(force=True)

@ronald.command()
async def status(ctx):
    channel = ronald.get_channel(285648579605954560)
    await channel.send('Ronald is self aware')

@ronald.command()
async def stop (ctx):
    channel = ronald.get_channel(285648579605954560)
    await channel.send('Ronald does not compute')
    

@ronald.command()
async def ayuda(ctx, subhelp=None):
    if subhelp == 'newclip':
        await ctx.send('```!r newclip => crea un nuevo clip basado en youtube.\n'
                        '   ej: !r newclip youtube.com/xyz 00:01:20 05\n'
                        '       crea un clip de 1 min 20 segundos que dura 5 segundos de largo.\n'
                        '  !r saveclip <nombre>\n'
                        '       guarda el clip recién creado con <nombre>.```')
    else:
        await ctx.send('```Comandos: \n'
                       '!r play => rouni goes full ronald y tira sonidos random en tiempo random.\n'
                       '!r newclip => crea un nuevo clip "!r ayuda newclip" para más info.\n'
                       '!r saveclip <nombre> => guarda el clip recién creado con su <nombre>```')


ronald.run(os.environ['DISCORD_BOT_TOKEN'])