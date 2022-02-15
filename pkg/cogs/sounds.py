import asyncio
import os
import random
import re
import shutil

import discord
from discord.ext import commands

import pkg.utils.aws_utils as aws
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

def get_clip_file(sound):
    for filename in os.listdir(RESOURCE_PATH):
        if sound == filename[0:-4]:
            return RESOURCE_PATH + filename

