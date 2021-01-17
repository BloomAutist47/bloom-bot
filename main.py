
import discord
import json
import logging
import os

from dotenv import load_dotenv
from bs4 import BeautifulSoup as Soup
from discord.ext import commands
from itertools import islice
from math import floor


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./Data/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

if os.name == "nt": # PC Mode
    from pprint import pprint
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv()
    # DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN') # officia bot token
    DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN2') # test bot token
else:               # github
    DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')


"""GIT Mode"""


# Scraper
class BloomScraper:

    def __init__(self):
        self.url = "https://adventurequest.life/"
        self.settings = {}
        self.data = {}
        self.priveleged_roles = []

    # System handling
    def database_update(self):
        # Loads locallly saved .html portal site.
        # A workwaround because I couldn't figure out how to bypass the fucking Cloudflare shit protection
        # If I can find a way to bypass cloudflare or be whitelisted or direct access to the website...
        # this can become updated dynamically.
        self.read()
        soup = Soup(open("./Data/html/aqw.html", encoding="utf8"), "html.parser")
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
        with open('./Data/settings.json', 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def read(self):
        with open('./Data/database.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        with open('./Data/settings.json', 'r', encoding='utf-8') as f:
            self.settings = json.load(f)
        self.priveleged_roles = []
        for role in self.settings["priveleged_roles"]:
            if self.settings["priveleged_roles"][role] == 1:
                self.priveleged_roles.append(role)

    # Search Methods
    def list_bot_names(self):
        return [name for name in self.data.keys()]

    def find_bot_by_name(self, bot_name):
            list_of_possible_bots = []
            for author in self.data:
                for bot in self.data[author]:
                    selected_bot = bot_name.lower()
                    current_bot = bot.lower()

                    if selected_bot == current_bot:
                        return [(bot_name, self.data[author][bot], author)]
                    if selected_bot in current_bot:
                        list_of_possible_bots.append([bot, self.data[author][bot], author])
            return list_of_possible_bots

    def find_bot_by_author(self, bot_author):
        if bot_author in self.data:
            list_of_bots = []
            for bot in self.data[bot_author]:
                list_of_bots.append([bot, self.data[bot_author][bot], bot_author])
            return (True, list_of_bots)
        else:		
            list_of_possible_authors = []
            for author in self.data:
                if bot_author in author:
                    list_of_possible_authors.append(author)
            return (False, list_of_possible_authors)


# Sets up Database
DataBase = BloomScraper()
DataBase.database_update()

# the problem though, is that cloudflare is too strong. Cloudscraper won't work. I need 
description = '''An example bot to showcase the discord.ext.commands extension
module.\nThere are a number of utility commands being showcased here.'''

bloom_bot = commands.Bot(command_prefix='$', description=description)

# Tools
def embed_multi(title, list_var, *args):
    add_field_title = "\u200b"
    description = ""
    inline = True
    field_count = 0

    embedVar = discord.Embed(title=title, description="The following matches your keyword: `{}`".format(args[0]), color=0x00ff00)
    for items in list_var:
        if field_count == 2:
            embedVar.add_field(name=add_field_title, value=add_field_title, inline=inline)
            field_count = 0
        if len(description) > 900:
            embedVar.add_field(name=add_field_title, value=description, inline=inline)
            field_count += 1
            description = ""
        # if len(items[0]) > 20:
        #     name = items[0][:21] + "\n" + "\u2000" + "\u2005"+ items[0][21:]
        #     print(name)
        description += '\> [{}]({} "by {}")\n'.format(items[0], items[1]["url"], items[2])
    if field_count == 1:
        embedVar.add_field(name=add_field_title, value=add_field_title, inline=inline)
        embedVar.add_field(name=add_field_title, value=add_field_title, inline=inline)
    embedVar.add_field(name=add_field_title, value=description, inline=inline)

    return embedVar

def embed_single(title, description):
     return discord.Embed(title=title, description=description, color=0x00ff00)

def chunks_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Checks if on PC. Otherwise on heroku
if os.name == "nt":
    @bloom_bot.event
    async def on_ready():
        print("STarting Bloom Bot")
        await bloom_bot.get_channel(799238286539227136).send('hello')

# Start of Commands
@bloom_bot.command()
async def b(ctx, command_code, *, value: str=""):
    if command_code == "u" or command_code == "update":
        priveleged = False
        roles = [role.name for role in ctx.author.roles]
        for role in roles:
            if role in DataBase.priveleged_roles:
                priveleged = True
                break
        if priveleged:
            await ctx.send("**[**System**]** Updating Bloom Bot")
            DataBase.database_update()
            await ctx.send("**[**System**]** Bloom Bot updated!")
        else:
            await ctx.send("**[**System**]** User {} does not have permissions for `$b update` command.".format(ctx.author))

    if command_code == "boat" or command_code == "b":
        bot_name = value
        if bot_name == "":
            embedVar = embed_single("Bloom Bot", "Nigga, did you just give me an empty value?")
            await ctx.send(embed=embedVar)
            return
        if len(bot_name) < 3:
            embedVar = embed_single("Bloom Bot", "Keyword `{}` too small. Must be at least 3 letters.".format(value))
            await ctx.send(embed=embedVar)
            return
        bot_find = DataBase.find_bot_by_name(bot_name)

        if not bot_find:
            embedVar = embed_single("Bots Result.", "We're sorry. No boat came up with your search word: `{}`".format(bot_name))
            await ctx.send(embed=embedVar)
            return
        target = chunks_list(bot_find, 48)
        for bots in target:
            embeded_object = embed_multi("Bot Results", bots, bot_name)
            await ctx.send(embed=embeded_object)

    if command_code == "author" or command_code == "a":
        bot_author = value
        result = DataBase.find_bot_by_author(bot_author)
        bot_find = result[1]
        found_author = result[0]
        if found_author:
            target = chunks_list(bot_find, 49)
            for bot_set in target:
                embeded_object = embed_multi("Bot Author Result", bot_set, bot_author)
                await ctx.send(embed=embeded_object)
        else:
            if not bot_find:
                embedVar = embed_single("Bot Author Result", "We're sorry. No author name came up with your search word: `{}`".format(bot_author))
                await ctx.send(embed=embedVar)
                return
            embedVar = discord.Embed(title="Bot Author Result", color=0x00ff00)
            description = "None of the authors matched your search key. Maybe one of these is what you're looking for?\n\n"
            to_be_added_author = ""
            for author in bot_find:
                if len(to_be_added_author) > 40:
                    description += to_be_added_author + "\n"
                    to_be_added_author = ""
                to_be_added_author += "【 {} 】\u2004".format(author)
            embedVar.description = description + to_be_added_author
            await ctx.send(embed=embedVar)



bloom_bot.run(DISCORD_TOKEN)
