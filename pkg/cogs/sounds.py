import asyncio
import os
import random
import re
import shutil
import discord

from fileinput import filename 
from discord.ext import commands
from pkg.utils.config import cfg

import pkg.utils.aws_utils as aws

RESOURCE_PATH = 'resources/sounds/'

# rouni plays sounds
class Sounds(commands.Cog):
    def __init__(self, rouni):
        self.rouni = rouni
        if cfg['use_aws_resources']:
            aws.sync_resources(cfg['bucket_name'], cfg['sounds_prefix'], RESOURCE_PATH)


    @commands.command()
    async def play(self, ctx, *, sound='random'):
        user = ctx.message.author
        # user not in voice channel
        if user.voice is None:
            await ctx.send("Ronald does not compute")
        # only play sound if user is in a voice channel
        elif user.voice is not None:
            all_sounds = get_clips()
            channel = user.voice.channel

            if sound == 'random':
                random_sound = random.choice(all_sounds)
                await play_clip(channel, get_clip_file(random_sound))
            elif sound in all_sounds:
                await play_clip(channel, get_clip_file(sound))

    @commands.command()
    async def resync(self,ctx):
        if cfg['use_aws_resources']:
            await ctx.send("Ronald has become self aware: loading the big guns")
            if os.path.exists(RESOURCE_PATH):
                shutil.rmtree(RESOURCE_PATH)
            aws.sync_resources(cfg['bucket_name'], cfg['sounds_prefix'], RESOURCE_PATH)
            await ctx.send("Ronald has become self aware: lock and loaded")

# defs
async def play_clip(channel, sound_file):
    voice_client = await channel.connect()
    source = discord.FFmpegPCMAudio(sound_file)
    voice_client.play(source)
    while voice_client.is_playing:
        await asyncio.sleep(1)
    await voice_client.disconnect()

def get_clips():
    return [filename[:filename.index(".")] for filename in os.listdir(RESOURCE_PATH)]

def get_clip_file(sound):
    for filename in os.listdir(RESOURCE_PATH):
        if sound == filename[0:-4]:
            return RESOURCE_PATH + filename

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