
import discord
import json
import logging
import os

from dotenv import load_dotenv
from bs4 import BeautifulSoup as Soup
from discord.ext import commands
from itertools import islice
from math import floor
from pprint import pprint

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./Data/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


os.chdir(os.path.dirname(os.path.abspath(__file__)))


# Scraper
class BloomScraper:

    def __init__(self):
        self.url = "https://adventurequest.life/"
        self.data = {}

    # System handling
    def update(self):
        # Loads locallly saved .html portal site.
        # A workwaround because I couldn't figure out how to bypass the fucking Cloudflare shit protection
        # If I can find a way to bypass cloudflare or be whitelisted or direct access to the website...
        # this can become updated dynamically.
        soup = Soup(open("./Data/html/Auto Quest Worlds _ Aqw Bots.html", encoding="utf8"), "html.parser")
        body = soup.find("table", {"id":"table_id", "class":"display"}).find("tbody")
        row = body.find_all("tr")
        for i in row:
            link = i.find("td").find("a")["href"]
            data_name = link.split("/")[-1].split("_")
            file_type = link.split(".")[-1]

            bot_author = data_name[0].lower()
            bot_name = (("".join(" ".join(data_name[1:]).split(".")[0])).replace("- ", "")).replace('%', " ")

            if bot_author not in self.data:
	            self.data[bot_author] = {}
            self.data[bot_author][bot_name] = {}
            self.data[bot_author][bot_name]["url"] = link
            self.data[bot_author][bot_name]["file_type"] = file_type

        # pprint(self.data)
        self.save()

    def save(self):
        with open('./Data/database.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
    def read(self):
        with open('./Data/database.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)


    # Search Methods
    def list_bot_names(self):
        return [name for name in self.data.keys()]

    def find_bot(self, bot_name):
        # Finds one specific bot
        if bot_name in self.data:
            bot_author = bot_name.split("_")[0]
            return [bot_author, self.data[bot_name.lower()]]

    def find_bot_by_name(self, bot_name):
            list_of_possible_bots = []
            for author in self.data:
                for bot in self.data[author]:
                    selected_bot = bot_name.lower()
                    current_bot = bot.lower()

                    if selected_bot == current_bot:
                        return (self.data[author][bot], author)
                    if selected_bot in current_bot:
                        list_of_possible_bots.append([bot, self.data[author][bot], author])
            return list_of_possible_bots



    def find_bot_by_author(self, bot_author):
        if bot_author in self.data:
            return self.data[bot_author]
        else:		
            list_of_possible_authors = []
            for author in self.data:
                if bot_author in author:
                    list_of_possible_authors.append(author)
            return list_of_possible_authors


    def search_bots(self, bot_name):
        # find bots
        return self.check_length([bot for bot in self.data.keys() if bot_name.lower() in bot.lower()])

    def check_length(self, value):
        char_length = 0
        index = 0
        for item in value:
            char_length += len(item)
            index += 1
            if char_length >= 2000:
                break
        return value[:index-10]

def chunks(data, SIZE=10000):
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k:data[k] for k in islice(it, SIZE)}

def chunks_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Sets up Database
DataBase = BloomScraper()
DataBase.update()
DataBase.read()


# Discord bot
load_dotenv()

# pprint(os.environ)
# for i in os.environ:
#     print(i)

# DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# GUILD = getenv('DISCORD_GUILD')


description = '''An example bot to showcase the discord.ext.commands extension
module.
There are a number of utility commands being showcased here.'''

bloom_bot = commands.Bot(command_prefix='?', description=description)


@bloom_bot.event
async def on_ready():
    print("STarting Bloom Bot")
    await bloom_bot.get_channel(799668639128485918).send('hello')

@bloom_bot.command()
async def boat(ctx, *, bot_name: str):
    bot_find = DataBase.find_bot_by_name(bot_name)
    if not bot_find:
        embedVar = discord.Embed(title="Bots Result", description="We're sorry, nothing come up. Please try a different search word.", color=0x00ff00)
        await ctx.send(embed=embedVar)
        return
    if type(bot_find) != list:
        embedVar = discord.Embed(title="Bot Result", description="Enjoy your bot!", color=0x00ff00)
        embedVar.add_field(name="Link", value='[{}]({} "Created by {}")'.format(bot_name, bot_find[0]["url"], bot_find[1]), inline=True)
        await ctx.send(embed=embedVar)
    else:
        if len(bot_find) > 20:
            target = chunks_list(bot_find, 24)
            for bots in target:
                embedVar = discord.Embed(title="Bots Result", description="The following matches your search word.", color=0x00ff00)
                for bot in bots:
                    embedVar.add_field(name="Link", value='[{}]({} "Created by {}")'.format(bot[0], bot[1]["url"], bot[2]), inline=True)
                await ctx.send(embed=embedVar)

        else:
            embedVar = discord.Embed(title="Bots Result", description="The following matches your search word.", color=0x00ff00)
            for bot in bot_find:
                embedVar.add_field(name="Link", value='[{}]({} "Created by {}")'.format(bot[0], bot[1]["url"], bot[2]), inline=True)
            await ctx.send(embed=embedVar)


@bloom_bot.command()
async def author(ctx, *,bot_author: str):
    bot_find = DataBase.find_bot_by_author(bot_author)
    if type(bot_find) != list:
        if len(bot_find) > 20:
            target = chunks(bot_find, 53)

            for bot_set in target:
                embedVar = discord.Embed(title="Bot Author Result", description="Bots Created by {}".format(bot_author), color=0x00ff00)
                
                for bot in bot_set:
                    bot_name = bot
                    bot_url = bot_set[bot]["url"]    			# bot_file_type = bot_find[bot]["file_type"]

                    embedVar.add_field(name="Link", value="[{}]({})".format(bot_name, bot_url), inline=True)
                await ctx.send(embed=embedVar)
        else:
            embedVar = discord.Embed(title="Bot Author Result", description="Bots Created by {}".format(bot_author), color=0x00ff00)
            
            for bot in bot_find:
                bot_name = bot
                bot_url = bot_find[bot]["url"]               # bot_file_type = bot_find[bot]["file_type"]

                embedVar.add_field(name="Link", value="[{}]({})".format(bot_name, bot_url), inline=True)
            await ctx.send(embed=embedVar)
        return
    else:
        embedVar = discord.Embed(title="Bot Author Result", description="None of the authors matched your search key. Maybe one of these are what you're looking for?", color=0x00ff00)
        for author in bot_find:
            embedVar.add_field(name="Result", value="{}".format(author), inline=True)
        await ctx.send(embed=embedVar)



bloom_bot.run(DISCORD_TOKEN)
