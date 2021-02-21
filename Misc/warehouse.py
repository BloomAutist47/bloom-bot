# Imports
import discord
import json
import logging
import os
import re
import copy
import requests
import github3
import math as m
import glob
import io

from dotenv import load_dotenv
from bs4 import BeautifulSoup as Soup
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound
from pprint import pprint
from PIL import Image

import asyncio
import nest_asyncio
import aiohttp
import html5lib
import ast
import aiosonic

from datetime import datetime
from pytz import timezone
import unicodedata

class BloomBotCog_3(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot
        # self.bot.remove_command("help")
        self.block_color = 3066993
        self.message_objects = {}
        self.msg_count = 0

    @commands.command()
    async def g(self, ctx, guide):
        if guide.lower() == "r":
            priveleged = await self.check_privilege(ctx, "verify author")
            if not priveleged:
                await ctx.send(f"\> User {ctx.author} does not have permissions for `;g r` command.\n")
                return

            self.file_read("guides")
            await ctx.send("Updated Stuff")
            return

        g_name = guide.lower()
        if g_name in self.guides:
            if os.name == "nt": # PC Mode
                self.file_read("guides")

            # sent = False
            guide_data = self.guides[g_name]

            embedVar = discord.Embed(title=guide_data["title"], color=self.block_color)

            note = guide_data["header"]
            description = "**Full guide**: [here](%s)\n**Description**: "%(guide_data["link"])

            for steps in note:
                description += f"{note[steps]}\n"
            # description += "\n\u200b"
            embedVar.description = description

            embedVar.add_field(name="Instructions", value="Click \"🔻\" to go down and \"🔺\" to go up the list.", inline=False)
            embedVar.set_thumbnail(url=guide_data["thumbnail"])
            embedVar.set_footer(text="This short guide is updated as of %s."%(guide_data["update"]))

            embed_object = await ctx.send(embed=embedVar)

            self.message_objects[embed_object.id] = {}
            self.message_objects[embed_object.id]["guide"] = g_name
            self.message_objects[embed_object.id]["n"] = 0
            self.message_objects[embed_object.id]["lim"] = len()

            await embed_object.add_reaction(emoji = "\U0001F53A")
            await embed_object.add_reaction(emoji = "\U0001F53B")

            embedVar.set_field_at(-1, name="\u200b", value="\u200b", inline=False)
            self.msg_count += 1

            for steps in guide_data["content"]:
                embedVar.add_field(name=f"📌 Step {steps.capitalize()}", value=guide_data["content"][steps] + "\n\u200b", inline=False)
            await ctx.author.send(embed=embedVar)
            return

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if int(user.id) != 761955273342320691:
            if reaction.message.id in self.message_objects:
                embedVar = discord.Embed(title="dick", description="pusyy", color=self.block_color)
                obj = reaction.message
                embed = obj.embeds[0]

                msg = self.message_objects[obj.id]
                g_name = msg["guide"]
                if reaction.emoji == "🔻":
                    if msg["n"] == 0:
                        await obj.remove_reaction("🔻", user)
                        return
                    msg["n"] -= 1
                    await obj.remove_reaction("🔻", user)
                if reaction.emoji == "🔺": 
                    msg["n"] += 1
                    await obj.remove_reaction("🔺", user)
                index = msg["n"]
                if index == 0:
                    embed.set_field_at(-1, name="Instructions", value="Click \"🔻\" to go down and \"🔺\" to go up the list.", inline=False)
                else:
                    embed.set_field_at(-1, name=f"📌 Step {index}", value=self.guides[g_name]["content"][str(index)], inline=False)
                await reaction.message.edit(embed=embed)
