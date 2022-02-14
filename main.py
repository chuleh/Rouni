import os

from decouple import config
from discord.ext import commands
from pkg.cogs.sounds import Sounds

# access discord token
DISCORD_BOT_TOKEN = config('DISCORD_BOT_TOKEN')

# create bot
bot = commands.Bot(command_prefix='!', help_command=None)

# attach cogs
bot.add_cog(Sounds(bot))


@bot.command()
async def help(ctx, subhelp=None):
    if subhelp == 'newclip':
        await ctx.send('```!newclip youtube.com/abc 00:05:30.00 10\n'
                       '    Creates a new clip that begins at the 5 min 30 sec mark in the video, and runs for 10 seconds\n'
                       '!play test\n'
                       '    Listen to the created clip.\n'
                       '!saveclip testclip\n'
                       '    Save it as a new clip called testclip.```')
    elif subhelp == 'playlist':
        await ctx.send('```!playlist clip 1, clip 2, clip 3, 5\n'
                       '    Play the listed clips in sequence, with a delay of 5 seconds between each.\n'
                       '!playlist 5\n'
                       '    Plays 3 random clips with a 5 second delay between each.```')
    elif subhelp == 'delay':
        await ctx.send('```!delay clip 1, clip 2, clip 3, 500\n'
                       '    Creates a new clip from overlaying each clip every 500ms.\n'
                       '!delay 500\n'
                       '    Creates a new clip from overlaying 5 random clips every 500ms.```')
    else:
        await ctx.send('```Available Commands: \n'
                       '   !clips               List all clips\n'
                       '   !play <clip name>    Play a specific sound clip\n'
                       '   !newclip             Create a new clip. "!help newclip" for more\n'
                       '   !playlist            Play a lit of clips. "!help playlist" for more\n'
                       '   !delay               Overlay clips after a delay. "!help delay" for more\n')


@bot.command()
async def build(ctx):
    if 'BUILD_ID' in os.environ:
        build_id = os.environ['BUILD_ID']
        build_str = f'{build_id}'
    else:
        build_str = "undefined"
    await ctx.send(build_str)


@bot.command()
async def unstuck(ctx):
    for client in bot.voice_clients:
        await client.disconnect(force=True)

# start bot
print("Rouni on the river!")