# Imports
import discord
import json
import logging
import os
import re
import copy
import requests
import github3

from dotenv import load_dotenv
from bs4 import BeautifulSoup as Soup
from discord.ext import commands

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
    GITHUB_REPOS = os.getenv('GITHUB_REPOS')
    GITHUB_USER = os.getenv('GITHUB_USERNAME')
    GITHUB_BLOOM_BOT_TOKEN = os.getenv('GITHUB_BLOOMBOT_TOKEN')
    PERMISSIONS = os.getenv("PRIVILEGED_ROLE").split(',')
else:              # Heroku
    DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
    GITHUB_REPOS = os.environ.get('GITHUB_REPOS')
    GITHUB_USER = os.environ.get('GITHUB_USERNAME')
    GITHUB_BLOOM_BOT_TOKEN = os.environ.get('GITHUB_BLOOMBOT_TOKEN')
    PERMISSIONS = os.environ.get("PRIVILEGED_ROLE").split(',')


class BreakProgram(Exception):
    pass

# Scraper
class BloomScraper:

    def __init__(self):
        global GITHUB_BLOOM_BOT_TOKEN
        global GITHUB_USER
        global GITHUB_REPOS
        self.url = "https://adventurequest.life/"
        self.settings = {}
        self.data = {}
        self.priveleged_roles = []
        self.sets = {}

        self.github = github3.login(token=GITHUB_BLOOM_BOT_TOKEN)
        self.repository = self.github.repository(GITHUB_USER, GITHUB_REPOS)

    # System handling
    def database_update(self):
        # Loads locallly saved .html portal site.
        # A workwaround because I couldn't figure out how to bypass the fucking Cloudflare shit protection
        # If I can find a way to bypass cloudflare or be whitelisted or direct access to the website...
        # this can become updated dynamically.
        # try:
        self.clear_database()
        self.git_read()
        # except:
        #     pass
        self.data["sort_by_bot_name"] = {}
        self.data["sort_by_bot_authors"] = {}
        self.mode = ""

        try:
            row = []
            url = "https://adventurequest.life/"
            html = requests.get(url).text
            page_soup = Soup(html, "lxml")

            body = page_soup.find("table", {"id":"table_id", "class":"display"}).find("tbody")
            row_links = body.find_all("input", {"class":"rainbow"})

            for value in row_links:
                link = url + "bots/" + value["value"]
                row.append(link)
            self.mode = "web"
        except:
            self.git_read()
            return False

            soup = Soup(open("./Data/html/aqw.html", encoding="utf8"), "html.parser")
            body = soup.find("table", {"id":"table_id", "class":"display"}).find("tbody")
            row = body.find_all("tr")
            self.mode = "html"
        
        for i in row:
            if self.mode == "web":
                link = i
            elif self.mode == "html":
                link = i.find("td").find("a")["href"]
            item_name = link.split("/")[-1]
            raw_author = item_name
            # Code for finding the bot author. This didn't work easily.
            try:
                raw_data = re.match("(^[a-zA-Z0-9]+[_|-])", item_name)
                raw_author = (re.sub("_|-", "", raw_data[0])).lower()
            except: pass
            if raw_author in self.settings["confirmed_authors"]:
                bot_author = raw_author
            else:
                raw_author = item_name
                try:
                    for verified_author in self.settings["confirmed_authors"]:
                        for alias in self.settings["confirmed_authors"][verified_author]["alias"]:
                            if alias in raw_author:
                                bot_author = verified_author
                                raise BreakProgram
                            else:   # inefficient shit. but it works
                                bot_author = "Unknown"
                except:
                    pass

            # Code for refining bot name.
            if bot_author != "Unknown":
                bot_name = item_name
                alias = [alias for alias in DataBase.settings["confirmed_authors"][bot_author]["alias"]]
                for author_nickname in alias:
                    bot_name = bot_name.replace(author_nickname, "")
            else:
                bot_name = item_name
            bot_name = re.sub(r"_|-", " ", bot_name).lstrip().replace("%", "")  # replaces "_" & "-" with spaces
            bot_name = re.sub(r"\s\s\.|\s\.", ".", bot_name)# removes space between file format
            bot_name = re.sub(r"\s\s", " ", bot_name)       # replaces "  " double spaces into single space
            bot_name = re.sub(r"^[s\s]", "", bot_name)      # removes "s " from the name.
            bot_name = re.sub("Non\s|NON\s", "Non-", bot_name)  # replaces "non mem" to "non-mem"
            bot_name = bot_name.lstrip().rstrip()
            bot_author = bot_author.lower()
            self.data["sort_by_bot_name"][bot_name] = {}
            self.data["sort_by_bot_name"][bot_name]["url"] = link
            self.data["sort_by_bot_name"][bot_name]["author"] = bot_author

            # Sort by Author

            if bot_author not in self.data["sort_by_bot_authors"]:
                self.data["sort_by_bot_authors"][bot_author] = {}
                
            self.data["sort_by_bot_authors"][bot_author][bot_name] = {}
            self.data["sort_by_bot_authors"][bot_author][bot_name]["url"] = link

        self.git_save()
        return True

    def clear_database(self):
        with open('./Data/database.json', 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

    def save(self):
        with open('./Data/database.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        with open('./Data/settings.json', 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def save_set(self):
        with open('./Data/sets.json', 'w', encoding='utf-8') as f:
            json.dump(self.sets, f, ensure_ascii=False, indent=4)

    def read(self):
        with open('./Data/database.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        with open('./Data/sets.json', 'r', encoding='utf-8') as f:
            self.sets = json.load(f)
        with open('./Data/settings.json', 'r', encoding='utf-8') as f:
            self.settings = json.load(f)
        self.priveleged_roles = []
        for role in self.settings["priveleged_roles"]:
            if self.settings["priveleged_roles"][role] == 1:
                self.priveleged_roles.append(role)

    def git_save(self):
        git_data = json.dumps(self.data, indent=4).encode('utf-8')
        contents_object = self.repository.file_contents("./Data/database.json")
        contents_object.update("update", git_data)

        git_sets = json.dumps(self.sets, indent=4).encode('utf-8')
        contents_object = self.repository.file_contents("./Data/sets.json")
        contents_object.update("update", git_sets)

        git_settings = json.dumps(self.settings, indent=4).encode('utf-8')
        contents_object = self.repository.file_contents("./Data/settings.json")
        contents_object.update("update", git_settings)


    def git_read(self):
        git_data = self.repository.file_contents("./Data/database.json").decoded
        self.data = json.loads(git_data.decode('utf-8'))

        git_sets = self.repository.file_contents("./Data/sets.json").decoded
        self.sets = json.loads(git_sets.decode('utf-8'))

        git_settings = self.repository.file_contents("./Data/settings.json").decoded
        self.settings = json.loads(git_settings.decode('utf-8'))
        self.priveleged_roles = []
        for role in self.settings["priveleged_roles"]:
            if self.settings["priveleged_roles"][role] == 1:
                self.priveleged_roles.append(role)

        self.save()
        self.save_set()

    # Search Methods
    def find_bot_by_name(self, bot_name_value):
        # If bot_name_value is exact bot value
        if bot_name_value in self.data["sort_by_bot_name"]:
            link = self.data["sort_by_bot_name"][bot_name_value]["url"]
            author = self.data["sort_by_bot_name"][bot_name_value]["author"]
            return [[bot_name_value, author, link]]

        # Else, divides the bot between words and searches 
        # for bots with those words in them.
        list_of_possible_bots = []
        done_searching = []

        for author in self.data["sort_by_bot_authors"]:
            for bot in self.data["sort_by_bot_authors"][author]:
                search_name = bot_name_value.lower()
                bot_by_author = bot.lower()

                if search_name == bot_by_author:
                    link = self.data["sort_by_bot_authors"][author][bot]["url"]
                    return [(bot_name_value, author, link)]

                if (search_name in bot_by_author) and (bot_by_author not in done_searching):
                    done_searching.append(bot_by_author)
                    link = self.data["sort_by_bot_authors"][author][bot]["url"]
                    list_of_possible_bots.append([bot, author, link])
        if not list_of_possible_bots:
            done_searching = []
            bot_name_value = bot_name_value.split(" ")
            for bot_name in bot_name_value:
                for author in self.data["sort_by_bot_authors"]:
                    for bot in self.data["sort_by_bot_authors"][author]:
                        search_name = bot_name.lower()
                        bot_by_author = bot.lower()

                        if search_name == bot_by_author:
                            link = self.data["sort_by_bot_authors"][author][bot]["url"]
                            return [(bot_name, author, link)]

                        if (search_name in bot_by_author) and (bot_by_author not in done_searching):
                            done_searching.append(bot_by_author)
                            link = self.data["sort_by_bot_authors"][author][bot]["url"]
                            list_of_possible_bots.append([bot, author, link])
        return list_of_possible_bots

    def find_bot_by_author(self, author):
        author = author.lower()
        if author in self.data["sort_by_bot_authors"]:
            list_of_bots = []
            for bot in self.data["sort_by_bot_authors"][author]:
                link = self.data["sort_by_bot_authors"][author][bot]["url"]
                list_of_bots.append([bot, author, link])
            return (True, list_of_bots)
        else:
            list_of_possible_authors = []

            for verified_author in DataBase.settings["confirmed_authors"]:
                alias = [alias.lower() for alias in DataBase.settings["confirmed_authors"][verified_author]["alias"]]
                for author_nickname in alias:
                    if author in author_nickname:
                        list_of_possible_authors.append(alias[0])
                        break
            return (False, list_of_possible_authors)

    def find_author_id(self, value):
        test_id = re.sub("<|>|!|@","", value)
        for author in self.settings["confirmed_authors"]:
            if test_id == self.settings["confirmed_authors"][author]["id"]:
                return author.lower()
        return None

    def return_all_bots(self):
        all_bots = []
        for bot in self.data["sort_by_bot_name"]:
            bot_name = bot
            bot_link = self.data["sort_by_bot_name"][bot]["url"]
            bot_author = self.data["sort_by_bot_name"][bot]["author"]
            all_bots.append([bot_name, bot_author, bot_link])
        return all_bots


    def verified_author_check(self, author):
        if author == "":
            return ""
        author = author.lower()
        for verified_author in DataBase.settings["confirmed_authors"]:
            alias = [alias.lower() for alias in DataBase.settings["confirmed_authors"][verified_author]["alias"]]
            if author in alias:
                return alias[0]
        return "empty_value"

    def set_creation(self, set_name, set_value):
        not_addded_bot = []
        for bot in set_value:
            bot_name = bot.lstrip().rstrip()
            if bot_name in self.data["sort_by_bot_name"]:
                self.sets[set_name][bot_name] = self.data["sort_by_bot_name"][bot_name]
            else:
                not_addded_bot.append(bot_name)
        return not_addded_bot

    def set_validator(self, command_title, set_name):
        if self.sets[set_name] == {}:
            self.sets.pop(set_name, None)
            return embed_single(command_title, "None of what you entered were valid.")
        else:
            return None
            
# Sets up Database
DataBase = BloomScraper()
x = DataBase.database_update()


# block_color = 0x00ff00
block_color = 3066993
database_updating = False
set_creation_commands = [
                "create", "cre", "c",
                "append", "app", "a",
                "overwrite", "over", "o",
                "all"
                ]

# the problem though, is that cloudflare is too strong. Cloudscraper won't work. I need 
description = '''An example bot to showcase the discord.ext.commands extension
module.\nThere are a number of utility commands being showcased here.'''

bloom_bot = commands.Bot(command_prefix=';', description=description)

# Tools
def embed_multi_link(title, embed_description, list_var):
    # block_title = "⬛ ⬛ ⬛ ⬛ ⬛ ⬛ ⬛"
    # block_title = "\> ◼️ ◼️ ◼️ ◼️ ◼️ ◼️ ◼️"
    # Properties
    st = "\u200b" # Spacer title
    block_title = "Link:"
    bot_list = ""
    inline = True
    counts = {"field": 0, "item": 0}

    embedVar = discord.Embed(title=title, description=embed_description, color=block_color)

    for items in list_var:
        if counts["field"] == 2:
            embedVar.add_field(name=st, value=st, inline=inline)
            counts["field"] = 0
        if counts["item"] == 8:
            embedVar.add_field(name=block_title, value=bot_list, inline=inline)
            counts["field"] += 1
            counts["item"] = 0
            bot_list = ""
        counts["item"]+=1                            # Bot Name, # Link, # Author
        bot_list += '\> [{}]({} "by {}")\n'.format(items[0], items[2], items[1])

    if counts["field"] == 2:
        embedVar.add_field(name=st, value=st, inline=inline)
    if counts["field"] == 1:
        embedVar.add_field(name=st, value=st, inline=inline)
        embedVar.add_field(name=st, value=st, inline=inline)
    embedVar.add_field(name=block_title, value=bot_list, inline=inline)

    return embedVar

def embed_multi_text(title, field_name, description, value_list, block_count, two_collumn):
    st = "\u200b"
    counts = {"field": 0, "item": 0}
    text_item = "```css\n"

    embedVar = discord.Embed(title=title, description=description, color=block_color)
    for text in value_list:
        if counts["field"] == 2 and two_collumn:
            embedVar.add_field(name=st, value=st, inline=True)
            counts["field"] = 0

        if counts["item"] == block_count:
            embedVar.add_field(name=field_name, value=text_item+ "```", inline=True)
            text_item = "```css\n"
            counts["item"] = 0
            counts["field"]+=1

        text_item += text + "\n"
        counts["item"] += 1
    if two_collumn:
        if counts["field"] == 2:
            embedVar.add_field(name=st, value=st, inline=True)
            embedVar.add_field(name=st, value=st, inline=True)
        embedVar.add_field(name=field_name, value=text_item + "```", inline=True)

        if counts["field"] == 0:
            embedVar.add_field(name=st, value=st, inline=True)
            embedVar.add_field(name=st, value=st, inline=True)
        if counts["field"] == 1:
            embedVar.add_field(name=st, value=st, inline=True)
    if not two_collumn:
        embedVar.add_field(name=field_name, value=text_item + "```", inline=True)
    return embedVar

def embed_single(title, description):
     return discord.Embed(title=title, description=description, color=block_color)

def chunks_list(lst, n):
    # Yield successive n-sized chunks from lst.
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def privilege_check(ctx):
    try:
        roles = [role.name for role in ctx.author.roles]
        for role in roles:
            if role in DataBase.priveleged_roles:
                return True
                break
    except: False


# Checks if on PC. Otherwise on heroku
if os.name == "nt":
    @bloom_bot.event
    async def on_ready():
        print("Starting Bloom Bot")
        await bloom_bot.get_channel(799238286539227136).send('hello')
else:
    try:
        print(os.name)
    except:
        print("DIDN'T WORKING BITCH")
# Start of Commands
@bloom_bot.command()
async def verify(ctx, *, value: str=""):
    global database_updating
    priveleged = privilege_check(ctx)
    if priveleged:
        if not database_updating:
            database_updating = True
            value_data = value.split(" ")
            author_name = value_data[0]
            author_id = re.sub("<|>|!|@","", value_data[1])
            
            DataBase.settings["confirmed_authors"][author_name] = {}
            try:
                DataBase.settings["confirmed_authors"][author_name]["alias"].append(author_name)
            except:
                DataBase.settings["confirmed_authors"][author_name]["alias"] = []
                DataBase.settings["confirmed_authors"][author_name]["alias"].append(author_name)
            DataBase.settings["confirmed_authors"][author_name]["id"] = author_id
            await ctx.send(r"\> Saving Bloom Bot.")
            DataBase.git_save()
            await ctx.send(r"\> Updating Bloom Bot")
            DataBase.database_update()
            await ctx.send(r"\> Bloom Bot updated. Author Successfully added!")
            database_updating = False
            return
        else:
            await ctx.send(r"\> Bloom Bot update in progress.")

    else:
        desc = f"\> User {ctx.author} does not have permissions for `;verify author @author` command.\n"
        await ctx.send(desc)
        return

# Start of Commands
@bloom_bot.command()
async def update(ctx, *, value: str=""):
    if str(ctx.author.id) not in PERMISSIONS:
        pass
    else:
        desc = f"\> User {ctx.author} does not have permissions for `;update` command.\n"
        await ctx.send(desc)
        return

    global database_updating
    priveleged = privilege_check(ctx)
    if priveleged:
        if not database_updating:
            database_updating = True
            await ctx.send(r"\> Updating Bloom Bot")
            result = DataBase.database_update()
            if result:
                await ctx.send(r"\> Bloom Bot updated!")
                await ctx.send(f"\> Update method: `{DataBase.mode}`")
            else:
                await ctx.send("\> Something's wrong. Ping the Autistic Chungus.\n`Error 69: Web method is fucked.`")
            database_updating = False
            return
        else:
            await ctx.send(r"\> Bloom Bot update in progress.")
    else:
        desc = f"\> User {ctx.author} does not have permissions for `;u` command.\n"\
                "> Please make sure you're in a server to use this command."
        await ctx.send(desc)
        return


@bloom_bot.command()
async def b(ctx, *, value: str=""):
    if str(ctx.author.id) not in PERMISSIONS:
        pass
    else:
        desc = f"\> User {ctx.author} does not have permissions for `;b bot_value` command.\n"
        await ctx.send(desc)
        return


    check = value.split()
    allowed = True
    for i in check:
        if len(i) < 3:
            allowed = False
            break
    if allowed:
        # Bot command search
        if value.lower() == "all":
            priveleged = privilege_check(ctx)
            if priveleged:
                bot_results = DataBase.return_all_bots()
                target = chunks_list(bot_results, 48)
                desc = "The following are all of the bots"
                for bot_chunk in target:
                    await ctx.send(embed=embed_multi_link("Bot Results", desc, bot_chunk))
                return
            else:
                desc = f"\> User {ctx.author} does not have permissions for `;b all` command.\n"
                await ctx.send(desc)
                return
        else:
            bot_name = value
            if bot_name == "":
                # If keyword is empty
                await ctx.send(embed=embed_single("Warning", "Please input a value to search.")) 
                return
            if len(bot_name) < 3:
                # if keyword is too short
                desc = f"Keyword `{value}` too small. Must be at least 3 letters."
                await ctx.send(embed=embed_single("Warning", desc))
                return

            bot_results = DataBase.find_bot_by_name(bot_name)
            if not bot_results:
                desc = f"We're sorry. No boat came up with your search word: `{bot_name}`"
                await ctx.send(embed=embed_single("Bot Result", desc))
                return
            
            # Actual Searching of boats
            target = chunks_list(bot_results, 45)
            desc = "The following matches your keyword: `{}`".format(bot_name)
            for bot_chunk in target:
                await ctx.send(embed=embed_multi_link("Bot Results", desc, bot_chunk))
            return
    else:
        await ctx.send(embed=embed_single("Warning", "Your search entries must have at least 3 letters.")) 
        return

@bloom_bot.command()
async def a(ctx, *, value: str=""):
    if str(ctx.author.id) not in PERMISSIONS:
        pass
    else:
        desc = f"\> User {ctx.author} does not have permissions for `;a bot_author` command.\n"
        await ctx.send(desc)
        return

    # Author command search
    value = value.lower()
    if "<@!" in value:
        author_id_name = DataBase.find_author_id(value)
        if author_id_name:
            bot_author = author_id_name
        else:
            await ctx.send(embed=embed_single("Bot Author Result", "No verified author of that name."))
            return
    else:
        if value=="unknown" or value=="u":
            bot_author = "Unknown"
        else:
            bot_author = value

    result = DataBase.find_bot_by_author(bot_author)
    found_author = result[0]    # Returns a bool if an exact author is found
    bot_list = result[1]        # List of found bots or possible authors
    if found_author:
        # Actual Author bots sending
        target = chunks_list(bot_list, 49)
        for bot_set in target:
            desc = f"The following are bots created by `{bot_author}`."
            await ctx.send(embed=embed_multi_link("Bot Author Result", desc, bot_set))
        return
    else:
        # if no exact author appeared
        if len(bot_list) == 1:
            if bot_list[0] not in DataBase.data["sort_by_bot_authors"].keys():
                desc = f"Author `{value}` has not created any boats yet. "
                await ctx.send(embed=embed_single("Bot Author Result", desc))
                return
        if not bot_list:
            desc = f"We're sorry. No author name came up with your search word: `{value}`"
            await ctx.send(embed=embed_single("Bot Author Result", desc))
            return

        if value:
            desc = f"Nothing came up with search key `{bot_author}`.\nMaybe one of these authors?."
            embedVar = embed_multi_text("Bot Author Result", "Author", desc, bot_list, 7, False)
        else:
            # Sends a list of possible authors
            desc ='List of all verified bot authors.'
            embedVar = embed_multi_text("Bot Author Result", "Author", desc, bot_list, 10, False)
            note_desc = "Some bots have unknown authors or were still not \nmanually listed in the confirmed list. To check bots with \nunknown authors, use command `;a u`."
            embedVar.add_field(name="Note:", value=note_desc, inline=True)
        await ctx.send(embed=embedVar)
        return

@bloom_bot.command()
async def set(ctx, *, value: str=""):
    if str(ctx.author.id) not in PERMISSIONS:
        pass
    else:
        desc = f"\> User {ctx.author} does not have permissions for `;set mode set_value` command.\n"
        await ctx.send(desc)
        return

    # Bot command set creation
    priveleged = privilege_check(ctx)
    if priveleged:
        set_command = value.split(" ")[0].lower()
        # Test if command is part of creation commands
        if set_command in set_creation_commands and set_command != "all":
            try:
                set_name = value.split(" ")[1].split("=")[0].lower()
                set_value = re.sub(r"\[|\]", "", value.split("=")[1]).split(",")
                set_value = [value.rstrip().lstrip() for value in set_value]
            except:
                await ctx.send(embed=embed_single("Bot Set", "Please input valid value"))
            # Return if "[]" is empty
            try:
                if set_value == ['']:
                    await ctx.send(embed=embed_single("Bot Set", "Please add at least one bot name between `[ ]`"))
                    return
            except: pass

            # Create command
            if set_command == "create" or set_command == "c":
                command_title = "Bot Set - Create"
                await ctx.send(embed=embed_single(command_title, "Starting"))
                if set_name in DataBase.sets:
                    desc = f"Set `{set_name}` already exists. Please pick a different set name.\n"\
                           f"> Use `;set append {set_name}=[]` to add bots to this set.\n"\
                           f"> Use `;set overwite {set_name}=[]` to overwrite current set."
                    await ctx.send(embed=embed_single("Bot Set - Create", desc))
                    return
                
                DataBase.sets[set_name] = {}
                not_addded_bot = DataBase.set_creation(set_name, set_value)

                # Checks if set is empty
                invalid = DataBase.set_validator(command_title, set_name)
                if invalid:
                    await ctx.send(embed=invalid)
                    return

                # Saves the set
                DataBase.git_save()
                desc = f"Set `{set_name}` was Created Successfully!"\
                       f"\nPlease use `;s {set_name}` to summon the set."
                embedVar = embed_single(command_title, desc)
                await ctx.send(embed=embedVar)

                # If there are invalid bot names
                if not_addded_bot:
                    desc = "Some of these bots weren't added. "\
                           "Either you mistyped the\nbot name, the database is not updated, or they don't exists."
                    embedVar = embed_multi_text("Note", "Not added bots", desc, not_addded_bot, 10, True)
                    await ctx.send(embed=embedVar)
                return

            # Append command
            if set_command == "append" or set_command == "app" or set_command == "a":
                command_title = "Bot Set - Append"
                await ctx.send(embed=embed_single(command_title, "Starting"))
                if set_name not in DataBase.sets:
                    desc = f"Set `{set_name}` does not exists."\
                           f"\nUse `;set create {set_name}=[]` to create the set."
                    await ctx.send(embed=embed_single(command_title, desc))
                    return

                # Actual append
                old_set = copy.copy(DataBase.sets[set_name])
                not_addded_bot = DataBase.set_creation(set_name, set_value)

                if DataBase.sets[set_name] == old_set:
                    desc = "None of what you entered were valid.\n"\
                           "Either they're already part of the set or you mistyped them."
                    await ctx.send(embed=embed_single(command_title, desc))
                    return

                DataBase.git_save()
                desc = f"Set `{set_name}` was Appended Successfully!"\
                       f"\nPlease use `;s {set_name}` to summon the set."
                embedVar = embed_single(command_title, desc)
                await ctx.send(embed=embedVar)

                if not_addded_bot:
                    desc = "Some of these bots weren't added. "\
                           "Either you mistyped the\nbot name, the database is not updated, or they don't exists."
                    embedVar = embed_multi_text("Note", "Not added bots", desc, not_addded_bot, 10, True)
                    await ctx.send(embed=embedVar)
                return

            # Overwrite command
            if set_command == "overwrite" or set_command == "over" or set_command == "o":

                command_title = "Bot Set - Overwrite"
                await ctx.send(embed=embed_single(command_title, "Starting"))
                if set_name not in DataBase.sets:
                    desc = f"Set `{set_name}` does not exists."\
                           f"\nUse `;set create {set_name}=[]` to create the set."
                    await ctx.send(embed=embed_single(command_title, desc))
                    return
                

                DataBase.sets[set_name] = {}
                not_addded_bot = DataBase.set_creation(set_name, set_value)

                # Checks if set is empty
                invalid = DataBase.set_validator(command_title, set_name)
                if invalid:
                    await ctx.send(embed=invalid)
                    return

                # Saves the set
                DataBase.git_save()
                desc = f"Set `{set_name}` was Overwritten Successfully!"\
                       f"\nPlease use `;s {set_name}` to summon the set."
                await ctx.send(embed=embed_single(command_title, desc))

                # If there are invalid bot names
                if not_addded_bot:
                    desc = "Some of these bots weren't added. "\
                           "Either you mistyped the\nbot name, the database is not updated, or they don't exists."
                    embedVar = embed_multi_text("Note", "Not added bots", desc, not_addded_bot, 10, True)
                    await ctx.send(embed=embedVar)
                return

        if set_command == "delete" or set_command == "del" or set_command == "d":
            command_title = "Bot Set - Delete"
            await ctx.send(embed=embed_single(command_title, "Starting"))
            set_name = value.split(" ")[1].lower()
            if set_name in DataBase.sets:
                DataBase.sets.pop(set_name, None)
                DataBase.git_save()
                await ctx.send(embed=embed_single(command_title, f"Set `{set_name}` set was deleted Successfully!"))
            else:
                await ctx.send(embed=embed_single(command_title, f"Set `{set_name}` does not exists."))


    else:
        desc = f"\> User {ctx.author} does not have permissions for `;set command value` command.\n"
        await ctx.send(desc)
        return

@bloom_bot.command()
async def s(ctx, *, value: str=""):
    if str(ctx.author.id) not in PERMISSIONS:
        pass
    else:
        desc = f"\> User {ctx.author} does not have permissions for `;s set_name` command.\n"
        await ctx.send(desc)
        return

    set_name = value
    if set_name == "":
        if DataBase.sets:
            set_list = [set_name for set_name in DataBase.sets]
            target = chunks_list(set_list, 48)
            for sets in target:
                desc = "The following is a list of all sets.\n"\
                       "Please use `;s set_name` to summon a set."
                embedVar = embed_multi_text("Bot Set - All", "Sets", desc, sets, 10, True)
                await ctx.send(embed=embedVar)
            return
        else: 
            # sets are empty
            await ctx.send(embed=embed_single("Bot Set", "No set currently exists"))
    else:
        if set_name in DataBase.sets:
            sets = DataBase.sets[set_name]
            set_data = []
            for bot in sets:
                url = sets[bot]["url"]
                author = sets[bot]["author"]
                set_data.append([bot, author, url])

            target = chunks_list(set_data, 48)
            for bots in target:
                desc = f"The following are the bots under `{set_name}` set."
                embeded_object = embed_multi_link("Bot Set", desc, bots)
                await ctx.send(embed=embeded_object)
            return
        else:
            await ctx.send(embed=embed_single("Bot Set", f"Set `{set_name}` does not exists."))
            return

@bloom_bot.command()
async def git(ctx):
    if str(ctx.author.id) not in PERMISSIONS:
        pass
    else:
        desc = f"\> User {ctx.author} does not have permissions for `;git` command.\n"
        await ctx.send(desc)
        return

    await ctx.send("https://github.com/BloomAutist47/bloom-bot/")
    return


bloom_bot.run(DISCORD_TOKEN)



