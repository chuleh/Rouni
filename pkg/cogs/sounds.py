import asyncio
import os
import random
import re
import shutil

import discord
from discord.ext import commands

from pkg.utils.discord_utils import is_admin_request
import pkg.utils.aws_utils as aws
from pkg.utils.clip_utils import create_clip, mix_clips, clip_length
from pkg.utils.config import cfg

RESOURCE_PATH = 'resources/sounds/'


class Sounds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if cfg['use_aws_resources']:
            aws.sync_resources(cfg['bucket_name'], cfg['sounds_prefix'], RESOURCE_PATH)

    @commands.command()
    async def play(self, ctx, *, sound='random'):
        user = ctx.message.author
        # only play sound if user is in a voice channel
        if user.voice is not None:
            all_sounds = get_clips()
            channel = user.voice.channel
            if sound == 'random':
                random_sound = random.choice(all_sounds)
                await play_clip(channel, get_clip_file(random_sound))
            elif sound == 'test':
                await play_clip(channel, 'resources/tmp.mp3')
            elif sound in all_sounds:
                await play_clip(channel, get_clip_file(sound))
            else:
                await ctx.send('Not a valid clip.')

    @commands.command()
    async def playlist(self, ctx, *, arg):
        user = ctx.message.author
        # only play sound if user is in a voice channel
        if user.voice is not None:
            all_sounds = get_clips()
            channel = user.voice.channel

            args = arg.split(',')
            # last arg needs to be a number
            delay = to_int(args[-1])
            if delay < 0 or delay > 10:
                await ctx.send('Last parameter needs to be a number in seconds, less than 10')
            # if delay is the only parameter, play 3 random sounds
            elif len(args) == 1:
                sounds = [random.choice(all_sounds) for i in range(3)]
                await play_clips_delay(channel, sounds, delay)
            else:
                sounds = args[0:-1]
                await play_clips_delay(channel, sounds, delay)

    @commands.command()
    async def delay(self, ctx, *, arg):
        await delay(ctx, arg.split(','))

    @commands.command()
    async def clips(self, ctx, search_term=None):
        clip_list_msg = ''
        clips = get_clips()
        if search_term is not None:
            clips = filter(lambda clip: search_term.lower() in clip.lower(), clips)
        for clip_name in sorted(clips):
            clip_list_msg += clip_name
            # Break up message every 1500 chars (Discord limit is 2000 per message)
            if len(clip_list_msg) > 1500:
                await ctx.send(clip_list_msg)
                # Start building a new message
                clip_list_msg = ''
            else:
                clip_list_msg += ', '
        await ctx.send(clip_list_msg[:-2])

    @commands.command()
    async def newclip(self, ctx, yt_link, start, duration_str):
        duration = to_float(duration_str)
        if not is_admin_request(ctx):
            await ctx.send('Clip creation only available to admins.')
        elif 'youtube.com' not in yt_link:
            await ctx.send('Clip must be a link to youtube.com.')
        elif not is_timestamp(start):
            await ctx.send('Start time must be in format HH:MM:SS.MM.')
        elif not 0 < duration <= 30:
            await ctx.send('Duration must be a number of seconds between 0 and 30.')
        else:
            await ctx.send('Creating clip...')
            create_clip(yt_link, start, duration_str, 'resources/tmp.mp3')
            await ctx.send('New clip created. `!play test` to hear it again, `!saveclip clip_name` to save it.')

            # Could be refactored
            voice = ctx.message.author.voice
            if voice is not None:
                await play_clip(voice.channel, 'resources/tmp.mp3')

    @commands.command()
    async def saveclip(self, ctx, clip_name, force=None):
        if is_admin_request(ctx):
            if clip_name not in get_clips() or force == "force":
                local_file = f'resources/sounds/{clip_name}.mp3'
                os.rename('resources/tmp.mp3', local_file)
                aws.save_resource(cfg['bucket_name'], local_file)
                await ctx.send("Clip created successfully!")
            else:
                await ctx.send("Clip with that name already exists. You can overwrite with `!savelip clip_name force`")

    @commands.command()
    async def savefile(self, ctx):
        if not cfg['allow_savefile']:
            await ctx.send('Save file command is disabled.')
        if is_admin_request(ctx) and len(ctx.message.attachments) > 0:
            attachment = ctx.message.attachments[0]
            file_name = attachment.filename
            file_extension = file_name[file_name.index("."):]

            if file_name[:file_name.index(".")] in get_clips():
                await ctx.send('Clip with that name already exists.')
            elif (file_extension != '.wav') and (file_extension != '.mp3'):
                await ctx.send('Invalid file, must be .wav or .mp3.')
            else:
                print(f"Saving attachment...{file_name}")
                await attachment.save(RESOURCE_PATH + file_name)
                aws.save_resource(cfg['bucket_name'], RESOURCE_PATH + file_name)
                await ctx.send('File saved!')

    @commands.command()
    async def resync(self, ctx):
        if cfg['use_aws_resources']:
            await ctx.send("Resyncing all clip files...")
            if os.path.exists(RESOURCE_PATH):
                shutil.rmtree(RESOURCE_PATH)
            aws.sync_resources(cfg['bucket_name'], cfg['sounds_prefix'], RESOURCE_PATH)
            await ctx.send("Clips resycned!")

    @commands.command()
    async def length(self, ctx, clip):
        cliplen = clip_length(get_clip_file(clip))
        await ctx.send(f"{cliplen}ms")







async def play_clip(channel, sound_file):
    voice_client = await channel.connect()
    source = discord.FFmpegPCMAudio(sound_file)
    voice_client.play(source)
    while voice_client.is_playing():
        await asyncio.sleep(1)
    await voice_client.disconnect()


async def play_clips_delay(channel, sounds, delay):
    for i in range(len(sounds)):
        sound = sounds[i].strip()
        await play_clip(channel, get_clip_file(sound))
        if not i == len(sounds) - 1:
            await asyncio.sleep(delay)


async def delay(ctx, args):
    user = ctx.message.author
    # only play sound if user is in a voice channel
    if user.voice is not None:
        # if last arg is a number, and the rest are sounds, do simple delay
        if to_int(args[-1]) > -1 and all(to_int(arg) == -1 for arg in args[:-1]):
            await simple_delay(ctx, args)
        # if args are pairs of sound and delays, do advanced delay
        elif all(to_int(args[n]) == -1 or args[-1].strip() in get_clips() and to_int(args[n + 1]) > -1 for n in
                 range(len(args) - 1, 2)) \
                and to_int(args[-1]) == -1 or args[-1].strip() in get_clips():
            await advanced_delay(ctx, args)
        else:
            await ctx.send("Bad inputs.")


async def simple_delay(ctx, args):
    # Parse delay
    delay = to_int(args[-1])

    # Parse randoms
    randomized_sounds = []
    for i in range(0, len(args)):
        if args[i].strip() == 'random':
            random_sound = random.choice(get_clips())
            randomized_sounds.append(random_sound)
            args[i] = random_sound
    # Construct list of tuples (sound, delay)
    # if delay is the only parameter, mix 5 random sounds
    if len(args) == 1:
        clip_metadata = [(random.choice(get_clips()), delay if i > 0 else 0) for i in range(5)]
    else:
        clip_metadata = [(args[i].strip(), delay if i > 0 else 0) for i in range(len(args) - 1)]
    valid, clip_metadata = validate_clip_metadata(clip_metadata)
    if valid:
        await mix_and_play(ctx, clip_metadata)
    else:
        await ctx.send("Either clips are invalid or delay is greater than 30000.")


async def advanced_delay(ctx, args):
    # Parse randoms
    randomized_sounds = []
    for i in range(0, len(args)):
        if args[i].strip() == 'random':
            random_sound = random.choice(get_clips())
            randomized_sounds.append(random_sound)
            args[i] = random_sound

    # Construct list of tuples (sound, delay)
    # First is always 0 delay
    clip_metadata = [(args[0].strip(), 0)]
    clip_metadata.extend([(args[n+1].strip(), to_int(args[n])) for n in range(1, len(args), 2)])
    valid, clip_metadata = validate_clip_metadata(clip_metadata)
    if valid:
        await mix_and_play(ctx, clip_metadata)
    else:
        await ctx.send("Either clips are invalid or delay is greater than 30000.")


def get_clips():
    return [filename[:filename.index(".")] for filename in os.listdir(RESOURCE_PATH)]


def get_clip_file(sound):
    for filename in os.listdir(RESOURCE_PATH):
        if sound == filename[0:-4]:
            return RESOURCE_PATH + filename


def validate_clip_metadata(clip_metadata):
    valid = all(clip in get_clips() and delay <= 30000 for clip, delay in clip_metadata)
    if not valid:
        return False, None
    else:
        clip_metadata = [(get_clip_file(clip), delay) for clip, delay in clip_metadata]
        clip_metadata = [(path, sum([delay for _, delay in clip_metadata[:i + 1]]))
                         for i, (path, delay) in enumerate(clip_metadata)]
        return True, clip_metadata


async def mix_and_play(ctx, clip_metadata):
    mix_clips(clip_metadata)
    await ctx.send('New clip created. `!play test` to hear it again, `!saveclip clip_name` to save it.')
    await play_clip(ctx.message.author.voice.channel, 'resources/tmp.mp3')


def randomize_if_random(sound):
    return random.choice(get_clips()) if sound.strip() == 'random' else sound.strip()


def is_timestamp(timestamp):
    if re.match(r'\d{2}:\d{2}:\d{2}\.\d{2}', timestamp) is None:
        return False
    else:
        return True


def to_float(s):
    try:
        return float(s)
    except ValueError:
        return -1


def to_int(s):
    try:
        return int(s)
    except ValueError:
        return -1
