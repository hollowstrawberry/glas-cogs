"""
MIT License

Copyright (c) 2020-present phenom4n4n

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import discord
from rapidfuzz import process
from redbot.core import commands
from redbot.core.commands import BadArgument, MemberConverter
from unidecode import unidecode

import re

from discord.ext.commands.converter import Converter
from discord.ext.commands.errors import BadArgument

# original converter from https://github.com/TrustyJAID/Trusty-cogs/blob/master/serverstats/converters.py#L19
class FuzzyMember(MemberConverter):
    def __init__(self, response: bool = True):
        self.response = response
        super().__init__()

    async def convert(self, ctx: commands.Context, argument: str) -> discord.Role:
        try:
            member = await super().convert(ctx, argument)
        except BadArgument:
            guild = ctx.guild
            result = [
                (m[2], m[1])
                for m in process.extract(
                    argument,
                    {m: unidecode(m.display_name) for m in guild.members},
                    limit=None,
                    score_cutoff=75,
                )
            ]
            if not result:
                raise BadArgument(f'Member "{argument}" not found.' if self.response else None)

            sorted_result = sorted(result, key=lambda r: r[1], reverse=True)
            member = sorted_result[0][0]
        return member


IMAGE_LINKS = re.compile(r"(https?:\/\/[^\"\'\s]*\.(?:png|jpg|jpeg|gif|png|svg)(\?size=[0-9]*)?)")
EMOJI_REGEX = re.compile(r"(<(a)?:[a-zA-Z0-9\_]+:([0-9]+)>)")
MENTION_REGEX = re.compile(r"<@!?([0-9]+)>")
ID_REGEX = re.compile(r"[0-9]{17,}")


class ImageFinder(Converter):
    """This is a class to convert notsobots image searching capabilities into a more general
    converter class."""

    async def convert(self, ctx, argument):
        attachments = ctx.message.attachments
        mentions = MENTION_REGEX.finditer(argument)
        matches = IMAGE_LINKS.finditer(argument)
        emojis = EMOJI_REGEX.finditer(argument)
        ids = ID_REGEX.finditer(argument)
        urls = []
        if matches:
            for match in matches:
                urls.append(match.group(1))
        if emojis:
            for emoji in emojis:
                ext = "gif" if emoji.group(2) else "png"
                url = "https://cdn.discordapp.com/emojis/{id}.{ext}?v=1".format(
                    id=emoji.group(3), ext=ext
                )
                urls.append(url)
        if mentions:
            for mention in mentions:
                user = ctx.guild.get_member(int(mention.group(1)))
                if user is not None:
                    url = IMAGE_LINKS.search(str(user.avatar_url_as(format="png")))
                    urls.append(url.group(1))
        if not urls and ids:
            for possible_id in ids:
                user = ctx.guild.get_member(int(possible_id.group(0)))
                if user:
                    url = IMAGE_LINKS.search(str(user.avatar_url_as(format="png")))
                    urls.append(url.group(1))
        if attachments:
            for attachment in attachments:
                urls.append(attachment.url)

        if not urls and ctx.guild:
            user = ctx.guild.get_member_named(argument)
            if user:
                url = user.avatar_url_as(format="png")
                urls.append(url)
        if not urls:
            raise BadArgument("No images found.")
        return urls[0]

    async def search_for_images(self, ctx):
        urls = []
        async for message in ctx.channel.history(limit=10):
            if message.attachments:
                for attachment in message.attachments:
                    urls.append(attachment.url)
            match = IMAGE_LINKS.match(message.content)
            if match:
                urls.append(match.group(1))
        if not urls:
            raise BadArgument("No Images found in recent history.")
        return urls[0]
