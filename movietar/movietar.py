import asyncio
from email.mime import image
import functools
from io import BytesIO
from typing import Literal, Optional
import logging
import tempfile
import pathlib

import aiohttp
import discord
from PIL import Image, ImageDraw, ImageFont
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.data_manager import bundled_data_path
from redbot.core.utils.chat_formatting import pagify
from redbot.core.data_manager import cog_data_path

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

from .converters import FuzzyMember

import moviepy
from moviepy.editor import CompositeVideoClip, VideoFileClip
from moviepy.editor import VideoFileClip
from moviepy.editor import *
import numpy as np

logging.captureWarnings(False)
log = logging.getLogger("red.glas-cogs.movietar")


class Movietar(commands.Cog):
    """
    Make trash videos with your avatar
    """

    __version__ = "1.0.0"

    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(
            self,
            identifier=82345678897346,
            force_registration=True,
        )
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        asyncio.create_task(self.session.close())

    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(aliases=["crimee"], cooldown_after_parsing=True)
    async def crimenes(self, ctx, *, member: FuzzyMember = None):
        """Se busca urgentemente.."""
        if not member:
            member = ctx.author
        videotype = "crimes.mp4"
        pos = (0, 147)
        avisize = (300, 300)
        async with ctx.typing():
            avatar = await self.get_avatar(member)
            with tempfile.TemporaryDirectory() as tmpdirname:
                folder = pathlib.Path(
                    tmpdirname
                )  # cant tell if it returns a string or a path object
                file = folder / f"{ctx.message.id}final.mp4"
                image = self.gen_vid(
                    ctx, avatar, file, folder, videotype, pos, avisize
                )  # just generates the video
                file = discord.File(file, filename="crimenes.mp4")
                await ctx.send(file=file)

    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(aliases=["cuatrok"], cooldown_after_parsing=True)
    async def fourk(self, ctx, *, member: FuzzyMember = None):
        """Caught in 4k.."""
        if not member:
            member = ctx.author
        videotype = "4k.mp4"
        pos = (30, 20)
        avisize = (150, 150)
        async with ctx.typing():
            avatar = await self.get_avatar(member)
            with tempfile.TemporaryDirectory() as tmpdirname:
                folder = pathlib.Path(
                    tmpdirname
                )  # cant tell if it returns a string or a path object
                file = folder / f"{ctx.message.id}final.mp4"
                image = self.gen_vid(
                    ctx, avatar, file, folder, videotype, pos, avisize
                )  # just generates the video
                file = discord.File(file, filename="4k.mp4")
                await ctx.send(file=file)

    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(aliases=["powa"], cooldown_after_parsing=True)
    async def heman(self, ctx, *, member: FuzzyMember = None):
        """I've got the power.."""
        if not member:
            member = ctx.author
        videotype = "heman.mp4"
        pos = (200, 20)
        avisize = (150, 150)
        async with ctx.typing():
            avatar = await self.get_avatar(member)
            with tempfile.TemporaryDirectory() as tmpdirname:
                folder = pathlib.Path(
                    tmpdirname
                )  # cant tell if it returns a string or a path object
                file = folder / f"{ctx.message.id}final.mp4"
                image = self.gen_vid(
                    ctx, avatar, file, folder, videotype, pos, avisize
                )  # just generates the video
                file = discord.File(file, filename="4k.mp4")
                await ctx.send(file=file)

    @commands.bot_has_permissions(attach_files=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(aliases=["lis"], cooldown_after_parsing=True)
    async def blame(self, ctx, *, member: FuzzyMember = None):
        """I've gotta blame somebody.."""
        if not member:
            member = ctx.author
        videotype = "heman.mp4"
        pos = (210, 20)
        avisize = (150, 150)
        async with ctx.typing():
            avatar = await self.get_avatar(member)
            with tempfile.TemporaryDirectory() as tmpdirname:
                folder = pathlib.Path(
                    tmpdirname
                )  # cant tell if it returns a string or a path object
                file = folder / f"{ctx.message.id}final.mp4"
                image = self.gen_vid(
                    ctx, avatar, file, folder, videotype, pos, avisize
                )  # just generates the video
                file = discord.File(file, filename="4k.mp4")
                await ctx.send(file=file)

    async def generate_image(self, ctx: commands.Context, task: functools.partial):
        task = self.bot.loop.run_in_executor(None, task)
        try:
            image = await asyncio.wait_for(task, timeout=60)
        except asyncio.TimeoutError:
            return "An error occurred while generating this image. Try again later."
        else:
            return image

    async def get_avatar(self, member: discord.User):
        avatar = BytesIO()
        await member.avatar_url_as(static_format="png").save(avatar, seek_begin=True)
        return avatar

    @staticmethod
    def bytes_to_image(image: BytesIO, size: int):
        image = Image.open(image).convert("RGBA")
        image = image.resize((size, size), Image.ANTIALIAS)
        return image

    def gen_vid(self, ctx, member_avatar, fp, folder, videotype, pos, avisize):
        member_avatar = self.bytes_to_image(member_avatar, 300)
        clip = VideoFileClip(f"{bundled_data_path(self) / videotype}")
        duration = clip.duration

        clip = clip.volumex(1.0)
        numpydata = np.asarray(member_avatar)
        cat = ImageClip(numpydata).set_duration(duration).resize((avisize)).set_position((pos))
        clip = CompositeVideoClip([clip, cat])
        data = clip.write_videofile(
            str(fp),
            threads=1,
            preset="superfast",
            verbose=False,
            logger=None,
            temp_audiofile=str(folder / f"{ctx.message.id}final.mp3")
            # ffmpeg_params=["-filter:a", "volume=0.5"]
        )
        path = fp
        return data
