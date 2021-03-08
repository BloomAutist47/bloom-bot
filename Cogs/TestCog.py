from .Base import *
from discord.ext import commands
from discord.utils import get

class TestCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot
        self.list_links = {}
        self.compare = {}


    @commands.command()
    async def test(self, ctx, *, value=""):

        # searched_role = get(ctx.guild.roles, name='Daily Gifts')
        channel = await self.bot.fetch_channel(801384957364142101)
        # await channel.send(searched_role.mention)
        await channel.send("<@&814054683651342366>")
        # await channel.send("<&@814054683651342366>")
        # await channel.send("<@!>")

    @commands.command()
    async def ee(self, ctx):
        url="http://aqwwiki.wikidot.com/ewfwefwefwf"
        soup = await self.contentcreator(url)
        print("Retards: ", soup)
        if soup =="None":
            print("yes")
        print(soup)