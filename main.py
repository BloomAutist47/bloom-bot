"""
Notes:
    prefix:
        "file_fucntion": file refers to functions that deals
                         with locally saved data.
"""


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
from discord import Intents
from discord.utils import get as dis_get
from discord.ext.commands import CommandNotFound
from discord.abc import Snowflake
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


class BreakProgram(Exception):
    pass

class BaseProgram:

    def setup(self):
        self.env_variables()

        self.block_color = 3066993
        self.database_updating = False
        self.url = "https://adventurequest.life/"
        self.settings = {}
        self.classes = {}
        self.data = {}
        self.priveleged_roles = []
        self.mode = ""
        self.author_list_lowercase = []
        self.class_acronyms = {}
        self.guides = {}

        self.github = github3.login(token=self.GIT_BLOOM_TOKEN)
        self.repository = self.github.repository(self.GIT_USER, self.GIT_REPOS)

        self.file_read("all")
        if os.name != "nt":
            self.git_read("all")

    def env_variables(self):
        if os.name == "nt": # PC Mode
            
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            load_dotenv()
            self.DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN2') # test bot token
            self.GIT_REPOS = os.getenv('GITHUB_REPOS')
            self.GIT_USER = os.getenv('GITHUB_USERNAME')
            self.GIT_BLOOM_TOKEN = os.getenv('GITHUB_BLOOMBOT_TOKEN')
            self.PERMISSIONS = os.getenv("PRIVILEGED_ROLE").split(',')
            self.PORTAL_AGENT = os.getenv('PORTAL_AGENT')
        else:              # Heroku
            self.DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
            self.GIT_REPOS = os.environ.get('GITHUB_REPOS')
            self.GIT_USER = os.environ.get('GITHUB_USERNAME')
            self.GIT_BLOOM_TOKEN = os.environ.get('GITHUB_BLOOMBOT_TOKEN')
            self.PERMISSIONS = os.environ.get("PRIVILEGED_ROLE").split(',')
            self.PORTAL_AGENT = os.environ.get("PORTAL_AGENT")

    def database_update(self, mode: str):
        """ Description: Updates the database.json
            Arguments:
            [mode] accepts 'web', 'html'
                - 'web': scrapes directly from the self.url
                - 'html': uses pre-downloaded html of self.url
            Return: Bool
        """
        self.git_read("database-settings")
        self.file_clear_database()
        self.data["sort_by_bot_name"] = {}
        self.data["sort_by_bot_authors"] = {}

        if mode == "web":
            # try:
            headers = {
                'User-Agent': self.PORTAL_AGENT
            }
            row = []
            # scraper = cloudscraper.create_scraper()
            # html = scraper.get(self.url, headers=headers).text
            # html = requests.get(self.url, headers=headers).text


            # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0'}
            # request = urllib.request.Request(self.url, headers=headers)

            # r = urllib.request.urlopen(request).read()

            # http = urllib3.PoolManager(
            #     cert_reqs='CERT_REQUIRED',
            #     ca_certs=certifi.where()
            # )

            # html = http.request('GET', self.url, headers=headers).text
            # s = Session()
            # headers = OrderedDict({
            #     'Accept-Encoding': 'gzip, deflate, br',
            #     # 'Host': "grimaldis.myguestaccount.com",
            #     'User-Agent': self.PORTAL_AGENT
            # })
            # s.headers = headers
            # html = s.get(self.url, headers=headers, verify=False).text
            # print(html)
            try:
                html = requests.get(self.url, headers=headers).text
                page_soup = Soup(html, "lxml")
                body = page_soup.find("table", {"id":"table_id", "class":"display"}).find("tbody")
                row_links = body.find_all("input", {"class":"rainbow"})

                for value in row_links:
                    link = self.url + "bots/" + value["value"]
                    row.append(link)

                self.settings["latest_update"] = "web"
                self.mode = "web"
            except:
                self.git_read("database-settings")
                return False

        elif mode == "html":
            if self.settings["latest_update"] == "web":
                # Checks if the latest update method is web, i.e. the latest most way
                # of updating this.
                print("Didn't update. latest update is Web")
                self.git_read("database-settings")
                return False
            else:
                self.settings["latest_update"] = "html"
                self.mode = "html"
            try:
                soup = Soup(open("./Data/html/aqw.html", encoding="utf8"), "html.parser")
                body = soup.find("table", {"id":"table_id", "class":"display"}).find("tbody")
                row = body.find_all("tr")
            except:
                self.git_read("database-settings")
                return False
        
        for raw_link in row:
            if mode == "web": link = raw_link
            elif mode == "html": link = raw_link.find("td").find("a")["href"]

            item_name = link.split("/")[-1]
            raw_author = item_name
            # Code for finding the bot author. This didn't work easily.
            try:
                raw_data = re.match("(^[a-zA-Z0-9]+[_|-])", item_name)
                raw_author = (re.sub("_|-", "", raw_data[0])).lower()
            except: 
                pass
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
                alias = [alias for alias in self.settings["confirmed_authors"][bot_author]["alias"]]
                for author_nickname in alias:
                    author_replacement = [author_nickname.lower(), author_nickname.capitalize()]
                    for name in author_replacement:
                        bot_name = bot_name.replace(name, "").lstrip()
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


        # Saving
        self.file_save("database-settings")
        self.git_save("database-settings")
        print("lmao")
        return True

    def file_clear_database(self):
        """Description: Clears the database.json"""
        with open('./Data/database.json', 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

    def file_read(self, mode):
        """ Description: Reads data from local .json files
            Arguments:
                [mode] - checks to do. accepts: database, guides, settings, classes
                         or any of the their combination delimited by "-"
                    - 'database'> self.data
                    - 'guides'> self.guides
                    - 'settings'> self.settings
                    - 'classes'> self.classes
        """
        mode = mode.split("-")
        if mode == ["all"]:
            mode = ["database", "guides", "classes", "settings"]

        if "database" in mode:
            with open('./Data/database.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        if "guides" in mode:
            with open('./Data/guides.json', 'r', encoding='utf-8') as f:
                self.guides = json.load(f)
        if "classes" in mode:   
            with open('./Data/classes.json', 'r', encoding='utf-8') as f:
                self.classes = json.load(f)
            self.sort_classes_acronym()

        if "settings" in mode:
            with open('./Data/settings.json', 'r', encoding='utf-8') as f:
                self.settings = json.load(f)

            self.sort_privileged_roles()
            self.sort_author_list_lowercase()

    def file_save(self, mode:str):
        """ Description: Saves data to local .json files
            Arguments:
                [mode] - checks to do. accepts: database, guides, settings, classes
                         or any of the their combination delimited by "-"
                    - 'database'> self.data
                    - 'guides'> self.guides
                    - 'settings'> self.settings
                    - 'classes'> self.classes
        """
        mode = mode.split("-")
        if mode == ["all"]:
            mode = ["database", "guides", "classes", "settings"]

        if "database" in mode:
            with open('./Data/database.json', 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
        if "guides" in mode:
            with open('./Data/guides.json', 'w', encoding='utf-8') as f:
                json.dump(self.guides, f, ensure_ascii=False, indent=4)
        if "classes" in mode:
            with open('./Data/classes.json', 'w', encoding='utf-8') as f:
                json.dump(self.classes, f, ensure_ascii=False, indent=4)
            self.sort_classes_acronym()
        if "settings" in mode:
            with open('./Data/settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)


    def git_save(self, mode:str):
        """ Description: Saves data to github .json files
            Arguments:
                [mode] - checks to do. accepts: database, guides, settings, classes
                         or any of the their combination delimited by "-"
                    - 'database'> self.data
                    - 'guides'> self.guides
                    - 'settings'> self.settings
                    - 'classes'> self.classes
        """
        mode = mode.split("-")
        if mode == ["all"]:
            mode = ["database", "guides", "classes", "settings"]

        if "database" in mode:
            git_data = json.dumps(self.data, indent=4).encode('utf-8')
            contents_object = self.repository.file_contents("./Data/database.json")
            contents_object.update("update", git_data)
            print("Git-database called")

        if "guides" in mode:
            git_guides = json.dumps(self.guides, indent=4).encode('utf-8')
            contents_object = self.repository.file_contents("./Data/guides.json")
            contents_object.update("update", git_guides)

        if "settings" in mode:
            git_settings = json.dumps(self.settings, indent=4).encode('utf-8')
            contents_object = self.repository.file_contents("./Data/settings.json")
            contents_object.update("update", git_settings)
            print("Git-Settings called")

        if "classes" in mode:
            git_classes = json.dumps(self.classes, indent=4).encode('utf-8')
            contents_object = self.repository.file_contents("./Data/classes.json")
            contents_object.update("update", git_classes)

        self.file_save("all")
        return

    def git_read(self, mode:str):
        """ Description: Reads data from github .json files
            Arguments:
                [mode] - checks to do. accepts: database, guides, settings, classes
                         or any of the their combination delimited by "-"
                    - 'database'> self.data
                    - 'guides'> self.guides
                    - 'settings'> self.settings
                    - 'classes'> self.classes
        """
        mode = mode.split("-")
        if mode == ["all"]:
            mode = ["database", "guides", "classes", "settings"]

        if "database" in mode:
            git_data = self.repository.file_contents("./Data/database.json").decoded
            self.data = json.loads(git_data.decode('utf-8'))

        if "guides" in mode:
            git_guides = self.repository.file_contents("./Data/guides.json").decoded
            self.guides = json.loads(git_guides.decode('utf-8'))

        if "classes" in mode:
            git_classes = self.repository.file_contents("./Data/classes.json").decoded
            self.classes = json.loads(git_classes.decode('utf-8'))
            self.sort_classes_acronym()

        if "settings" in mode:
            git_settings = self.repository.file_contents("./Data/settings.json").decoded
            self.settings = json.loads(git_settings.decode('utf-8'))

            self.sort_privileged_roles()
            self.sort_author_list_lowercase()


        # Saving
        self.file_save("all")
        return

    def sort_classes_acronym(self):
        """ Description: sort classes acronyms into one dictionary
                and assigns each acronym as a key and their class name as value.
                Method created for much more efficient class acronym search.
        """

        for class_name in self.classes:
            if "acronym" in self.classes[class_name]:
                list_of_acronyms = self.classes[class_name]["acronym"].split(",")
                acronyms = [acr.replace(" ", "").lower() for acr in list_of_acronyms if acr != "(None)"]
                if acronyms != ['']:
                    for acr in acronyms:
                        self.class_acronyms[acr] = class_name
        return

    def sort_author_list_lowercase(self):
        """ Description: sort author aliases into one dictionary
                and assigns each alias as a key and their author name as value.
                Method created for much more efficient class author alias search.
        """
        self.author_list_lowercase = []
        for author in self.settings["confirmed_authors"]:
            self.author_list_lowercase.append(author.lower())
            for alias in self.settings["confirmed_authors"][author]["alias"]:
                self.author_list_lowercase.append(alias.lower())
        return

    def sort_privileged_roles(self):
        """ Description: Creates a list of privileged roles from self.settings
        """
        self.priveleged_roles = []
        for role in self.settings["EvaluatorSettings"]["role_privilege"]:
            if self.settings["EvaluatorSettings"]["role_privilege"][role] == 1:
                self.priveleged_roles.append(role)
        return


    """ SEARCH METHODS SECTION """
    def find_bot_by_name(self, bot_name_value:str):
        """Description: Finds boats by name
           Arguments:
               [bot_name_value] - search word
        """
        if bot_name_value in self.data["sort_by_bot_name"]:
            link = self.data["sort_by_bot_name"][bot_name_value]["url"]
            author = self.data["sort_by_bot_name"][bot_name_value]["author"]
            return {author: [bot_name_value.capitalize(), link]}

        # Else, divides the bot between words and searches 
        # for bots with those words in them.
        list_of_possible_bots = self.bot_searching_algorithm(bot_name_value)

        if not list_of_possible_bots:
            bot_name_value = bot_name_value.split(" ")
            for bot_name in bot_name_value:
                list_of_possible_bots = self.bot_searching_algorithm(bot_name)

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
            for verified_author in self.settings["confirmed_authors"]:
                alias = [alias.lower() for alias in self.settings["confirmed_authors"][verified_author]["alias"]]
                for author_nickname in alias:
                    if author in author_nickname:
                        list_of_possible_authors.append(alias[0])
                        break
            return (False, list_of_possible_authors)

    def bot_searching_algorithm(self, bot_name_value):
        list_of_possible_bots = {}
        done_searching = []
        for author in self.data["sort_by_bot_authors"]:
            for bot in self.data["sort_by_bot_authors"][author]:
                search_name = bot_name_value.lower()
                bot_by_author = bot.lower()

                if search_name == bot_by_author:
                    link = self.data["sort_by_bot_authors"][author][bot]["url"]
                    return {author:[(bot_name_value, link)]}

                if (search_name in bot_by_author) and ((bot_by_author, author) not in done_searching):
                    done_searching.append((bot_by_author, author))
                    link = self.data["sort_by_bot_authors"][author][bot]["url"]
                    if author not in list_of_possible_bots:
                        list_of_possible_bots[author] = []
                    list_of_possible_bots[author].append([bot, link])
        return list_of_possible_bots

    def find_author_aliases(self, author):
        return [alias.lower() for alias in self.settings["confirmed_authors"][author]["alias"]]


    def find_author_id(self, bot_author):
        test_id = re.sub("<|>|!|@","", bot_author)
        for author in self.settings["confirmed_authors"]:
            if test_id == self.settings["confirmed_authors"][author]["id"]:
                return author.lower()
        return None

    def find_class(self, class_name):
        possible_classes = []

        if len(class_name) <= 4:
            if class_name.lower() in self.class_acronyms:
                class_name_ = self.class_acronyms[class_name.lower()]
                return [
                    ("Authentic", ""), (class_name_, self.classes[class_name_]["discord_url"], self.classes[class_name_]["wiki"])
                    ]


        for class_name_ in self.classes:
            # Search if exact name
            if class_name == class_name_.lower():
                if "discord_url" in self.classes[class_name_]:
                    return [
                        ("Authentic", ""), (class_name_, self.classes[class_name_]["discord_url"], self.classes[class_name_]["wiki"])
                        ]
                else:
                    return [("Basic", ""), (class_name, self.classes[class_name_])]

            duplicates = [dn.lower() for dn in self.classes[class_name_]["duplicates"]]

            # Search duplicate classes
            if class_name in duplicates:
                ind = duplicates.index(class_name)
                if "discord_url" in self.classes[class_name_]:
                    return [
                        ("Duplicate", self.classes[class_name_]["duplicates"][ind]) ,
                        (class_name_, self.classes[class_name_]["discord_url"], self.classes[class_name_]["wiki"])
                        ]
                else:
                    return [("Basic", ""), (self.classes[class_name_]["duplicates"][ind], self.classes[class_name_])]

        if class_name.lower() in self.class_acronyms:
            class_name_ = self.class_acronyms[class_name.lower()]
            return [
                ("Authentic", ""), (class_name_, self.classes[class_name_]["discord_url"], self.classes[class_name_]["wiki"])
                ]

        for class_name_ in self.classes:
            #Search keyword likeness
            class_words = class_name.replace("  ", " ").split(" ")
            for words in class_words:
                if words == "" or len(words) == 1:
                    continue
                if words in class_name_.lower() and class_name_ not in possible_classes:
                    possible_classes.append(class_name_)
                for duplicate in duplicates:
                    if words in duplicate:
                        ind = duplicates.index(duplicate)
                        possible_classes.append(self.classes[class_name_]["duplicates"][ind])
        if possible_classes:
            return [(False, ""), (possible_classes)]
        else:
            return [(False, ""), ([])]


class BaseTools(BaseProgram):
    description = "Sets of tool functions to be used by other Cogs"
    async def check_word_count(self, ctx, value:str):
        """ Description: Checks word is allowed for searching
            Arguments:
                [ctx] - context
                [value] - word to be evaluated
            Return: Bool.
        """
        if value == "":
            await ctx.send(embed=self.embed_single("Warning", "Please input a value to search.")) 
            return False

        test = value.split(" ")
        for word in test:
            for banned_words in self.settings["banned_words"]:
                if banned_words in word.lower():
                    await ctx.send(embed=self.embed_single("Warning", f"The term `{banned_words}` is nerfed.\nIt does not give productive results.")) 
                    return False

        word_value = value.split(" ")
        for word in word_value:
            if word.isdigit() and len(word) != 1:
                return True
            if word.isdigit() and len(word) == 1:
                desc = "Your search entries must have `at least 3 letters`. \n"\
                       "Or it must be a number of `length greater than 1`."
                await ctx.send(embed=self.embed_single("Warning", desc)) 
                return False
        for word in word_value:
            if len(word) < 3:
                desc = "Your search entries must have `at least 3 letters`. \n"\
                       "Or it must be a number of `length greater than 1`."
                await ctx.send(embed=self.embed_single("Warning", desc)) 
                return False
        return True

    async def allow_evaluator(self, ctx, mode:str, command_name:str=""):
        """ Description: An Encapsulated function. Checks if permission checks are passed
                         before proceeding.
            Arguments:
                [ctx] - context
                [mode] - checks to do. 
                    accepts: guild_privilege, user_permissions, role_privilege, all, update
                             note: or any of the their combination delimited by "-".
                    - 'all'> checks all mode below except for 'update'
                    - 'guild_privilege'> if server can use full functionalities.
                    - 'role_privilege'> if the user is allowed to use privileged commands.
                    - 'user_permissions'> if user has permissions. niglist
                    - 'update'> checks if self.database_updating is set to True.
            Return: Bool.
            Example:
                allow_ = await self.allow_evaluator(ctx, mode="all-update", command_name="git")
                if not allow_:
                    return
        """
        mode = mode.split("-")
        if "all" in mode:
            mode.extend(["guild_privilege", "user_permissions", "role_privilege"])

        if "update" in mode:
            if self.database_updating:
                await ctx.send(r"\> Bloom Bot update in progress.")
                return False

        if "guild_privilege" in mode:
            guild_allowed = await self.check_guild_privilege(ctx)
            if not guild_allowed:
                return False

        if "role_privilege" in mode:
            priveleged = await self.check_role_privilege(ctx, command_name)
            if not priveleged:
                return False

        if "user_permissions" in mode:
            permissions_check = await self.check_user_permissions(ctx, command_name)
            if not permissions_check:
                print("WHYA")
                return False
        return True

    async def check_guild_privilege(self, ctx):
        """ Description: Checks if guild is a privileged server that has
                         access to full functionalities
            Arguments:
                [ctx] - context
        """
        try:
            guild_id = ctx.guild.id
        except:
            return False
        if guild_id in self.settings["EvaluatorSettings"]["guild_privilege"]:
            return True
        else:
            return False

    async def check_role_privilege(self, ctx, command_name:str):
        """ Description: Checks if the user is allowed to use privileged commands.
            Arguments:
                [ctx] - context
                [command_name] - command name that is being evaluated
        """
        try:
            roles = [role.name for role in ctx.author.roles]
            for role in roles:
                if role in self.priveleged_roles:
                    return True
                    break
        except:
            desc = f"\> User {ctx.author} does not have permissions for `;{command_name}` command.\n"
            await ctx.send(desc)
            return False

    async def check_user_permissions(self, ctx, command_name:str):
        """ Description: Checks if the user has permissions to use certain functionalities
                         niglist.
            Arguments:
                [ctx] - context
                [command_name] - command name that is being evaluated
        """
        if str(ctx.author.id) not in self.PERMISSIONS:
            return True
        else:
            desc = f"\> User {ctx.author} does not have permissions for `;{command_name}` command.\n"
            await ctx.send(desc)
            return False

    async def check_guild_guide(self, ctx):
        """ Description: Checks whatever some guides are allowed to a server
            Arguments:
                [ctx] - context
        """
        guild_id = str(ctx.guild.id)
        if guild_id in self.settings["server_settings"]:
            if self.settings["server_settings"][guild_id]["server_privilage"] == "Homie":
                return True
        if guild_id not in self.settings["server_settings"]:
            return False

    async def embed_image(self, ctx, discord_url:str, wiki_url:str, class_name:str, duplicate_name:str=""):
        """ Description: Sends an Image embed for the ;c class_name command
            Arguments:
                [ctx] - context
                [discord_url] - str. the url link of the class chart
                [wiki_url] - str. the url link for the class wiki
                [class_name] - str. name of the class
                [duplicate_name] - str. sends an embed stating that the class is a duplicate
        """
        credit_text2 = "Credits:"\
            "\nThanks to Shiminuki and Molevolent for creating the\nClass Tier List and "\
            "to the AuQW Community!\nType ;credits to see their links!"
        if duplicate_name:
            dupliVar = discord.Embed(title="Duplicate", color=self.block_color, 
                description=f"`{duplicate_name[0]}` is a duplicate of the {duplicate_name[1]} Class")
            await ctx.send(embed=dupliVar)

        embedVar = discord.Embed(title="Class Result", color=self.block_color, 
            description=f"\> Check [{class_name}]({wiki_url}) Class on the wiki.\n\> Please use `;legends` to understand the chart.")
        embedVar.set_image(url=discord_url)
        embedVar.set_footer(text=credit_text2)

        await ctx.send(embed=embedVar)


    async def embed_multiple_links(self, ctx, bot_name: str, bot_results: str):
        """ Description: Embeds multiple links sorted by AUTHOR
            Arguments:
                [ctx] - context
                [bot_name] - search command
                [bot_results] - the info chunck containing the boats
        """
        # Properties
        st = "\u200b"
        bot_list = ""
        inline = False
        counts = {"field": 0, "item": 0, "total":0}
        title = "Bot Results"
        desc = "The following matches your keyword: `{}`".format(bot_name)

        embedVar = discord.Embed(title=title, description=desc, color=self.block_color)
        done = []
        for author in bot_results:
            target = self.chunks_list(bot_results[author], 45)
            counts["item"] = 0
            for bot_chunk in target:
                bot_list = ""
                for items in bot_chunk:
                    if counts["total"] == 40:
                        counts["total"] = 0
                        counts["item"] = 0
                        await ctx.send(embed=embedVar)
                        bot_list = ""
                        embedVar = discord.Embed(title=title, description=desc, color=self.block_color)
                    if counts["item"] == 9:
                        embedVar.add_field(name=author.capitalize(), value=bot_list, inline=inline)
                        counts["item"] = 0
                        bot_list = ""
                    counts["item"]+=1
                    counts["total"] += 1
                    bot_list += '\> [{}]({})\n'.format(items[0], items[1])
                embedVar.add_field(name=author.capitalize(), value=bot_list, inline=inline)
        await ctx.send(embed=embedVar)
        return

    # Tools
    def embed_multi_link(self, title, block_title, embed_description, list_var):
        """ Description: Embeds multiple links not sorted by anything.
            Arguments:
                [title] - title
                [block_title] - title of the addfields
                [embed_description] - embed description
                [list_var] - the info chunk of boats
        """

        # Properties
        st = "\u200b" # Spacer title
        bot_list = ""
        inline = True
        counts = {"field": 0, "item": 0}

        embedVar = discord.Embed(title=title, description=embed_description, color=self.block_color)

        for items in list_var:
            if counts["field"] == 2:
                embedVar.add_field(name=st, value=st, inline=inline)
                counts["field"] = 0
            if counts["item"] == 8:
                embedVar.add_field(name=block_title, value=bot_list, inline=inline)
                counts["field"] += 1
                counts["item"] = 0
                bot_list = ""
            counts["item"]+=1
            if title == "Bot Author Result":
                bot_list += '\> [{}]({})\n'.format(items[0], items[2])
            else:
                bot_list += '\> [{}]({})\n'.format(items[0], items[1])
        if counts["field"] == 2:
            embedVar.add_field(name=st, value=st, inline=inline)
        if counts["field"] == 1:
            embedVar.add_field(name=st, value=st, inline=inline)
            embedVar.add_field(name=st, value=st, inline=inline)
        embedVar.add_field(name=block_title, value=bot_list, inline=inline)

        return embedVar

    def embed_multi_text(self, title:str, field_name:str, description:str,
            value_list, block_count:int, two_collumn:bool):
        """ Description: Embeds multiple links not sorted by anything.
            Arguments:
                [title] - title
                [field_name] - title of the fields
                [description] - embed description
                [value_list] - the info chunk of text
                [block_count] - how may items per fields
                [two_collumn] - if the chunks are presented in two column or three column
            Return: Discord embed object
        """
        st = "\u200b"
        counts = {"field": 0, "item": 0}
        text_item = "```css\n"

        embedVar = discord.Embed(title=title, description=description, color=self.block_color)
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

    def embed_single(self, title, description):
        """ Description: Single item embed
            Arguments:
                [title] - title
                [description] - embed description
            Return: Discord embed object
        """
        return discord.Embed(title=title, description=description, color=self.block_color)

    def chunks_list(self, lst, n):
        """ Description: Yield successive n-sized chunks from lst.
            Arguments:
                [lst] - list to be sliced into n parts
                [n] - amount of each sliced parts
            Return: Iterator generator
        """
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

class BaseCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot

    # @commands.command()
    # async def test(self, ctx):
    #     if str(ctx.author.id) == str(252363724894109700):
    #         if os.name == "nt":
    #             await self.bot.fetch_channel(799238286539227136)
    #         else:
    #             await self.bot.fetch_channel(807587012471029760)
    #         desc = f"\> <@&{str(807586780324954123)}>"
    #         await ctx.send(desc)

    @commands.command()
    async def bhelp(self, ctx):
        guild_allowed = await self.allow_evaluator(ctx, "guild_privilege")
        if guild_allowed:
            embedVar = discord.Embed(title="Bloom Help", color=self.block_color,
                description="The following are a list of all commands and "\
                            "how to use them. These commands must be used "\
                            "in the <#802082388451655691> channel. "\
                            "Please ping <@!252363724894109700> if something goes wrong with Bloom Bot.")
            embedVar.add_field(name="\u200b", inline=False,
                value="————————  Commands For Everyone  ————————")
            embedVar.add_field(name="`;bhelp`", inline=False,
                value="Reveals the help embed, showing all commands.")
            embedVar.add_field(name="`;b bot_name`", inline=False,
                value="Searches a bot. Keywords must be letters with atleast 3 characters "\
                      "or numbers with at least 2 digits.")
            embedVar.add_field(name="`;a author`", inline=False,
                value="Searches the bots made by a particular author.")
            embedVar.add_field(name="`;a`", inline=False,
                value="Shows a list of all bot authors.")
            embedVar.add_field(name="`;a u`", inline=False,
                value="Shows a list of all bots with unidentified authors.")
            embedVar.add_field(name="`;c class_name`", inline=False,
                value="Shows the data chart of the searched class.")
            embedVar.add_field(name="`;legends`", inline=False,
                value="Shows the legends for the class data charts.")
            embedVar.add_field(name="`;char character_name`", inline=False,
                value="Pulls up basic player info from the Character page.")
            embedVar.add_field(name="`;credits`", inline=False,
                value="Shows the Credits.")

            embedVar.add_field(name="\u200b", inline=False,
                value="————————  Commands For Priviledge  ————————")
            embedVar.add_field(name="`;bverify author`", inline=False,
                value="Verifies an author name so the Bloom Command ;b author can "\
                      "recognize their bots.")
            embedVar.add_field(name="`;bunverify author`", inline=False,
                value="Unverifies an author name, removing their bot name recognition")

            embedVar.add_field(name="**Lists of Priviledged Roles**", inline=False,
                value="Admin, Staff, Helper, Trial Helper, Verified Bot Makers")
            embedVar.add_field(name="**Note:**", inline=False,
                value="\"Heil Gravelyn!\" -Bloom Autist")
            embedVar.set_thumbnail(url="https://cdn.discordapp.com/attachments/802986034538610708/804373863650558022/Gravelyn.png")

            await ctx.send(embed=embedVar)
            return
        if not guild_allowed:
            embedVar = discord.Embed(title="Bloom Help", color=self.block_color,
                    description="The following are a list of all commands and "\
                                "how to use them. These commands must be used "\
                                "in the <#805413618719260712> channel. "\
                                "Please ping <@!252363724894109700> if something goes wrong with Bloom Bot.")
            embedVar.add_field(name="\u200b", inline=False,
                value="————————  Commands For Everyone  ————————")
            embedVar.add_field(name="`;bhelp`", inline=False,
                value="Reveals the help embed, showing all commands.")
            embedVar.add_field(name="`;g`", inline=False,
                value="Summons a list of all guides.")
            embedVar.add_field(name="`;g guide_name`", inline=False,
                value="Returns a specific guide. Use ;g to get a guide name.")
            embedVar.add_field(name="`;c class_name`", inline=False,
                value="Shows the data chart of the searched class. Can use whole class name or acronym.")
            embedVar.add_field(name="`;legends`", inline=False,
                value="Shows the legends for the class data charts.")
            embedVar.add_field(name="`;char character_name`", inline=False,
                value="Pulls up basic player info from the Character page.")
            embedVar.add_field(name="`;credits`", inline=False,
                value="Shows the Credits.")
            embedVar.add_field(name="**Note:**", inline=False,
                value="\"Heil Gravelyn!\" -Bloom Autist")
            embedVar.set_thumbnail(url="https://cdn.discordapp.com/attachments/802986034538610708/804373863650558022/Gravelyn.png")
            await ctx.send(embed=embedVar)
            return

    @commands.command()
    async def git(self, ctx):
        """ Description: shows the git link
            Arguments:
                [ctx] - context
                [author_name] - author to be unverified
            Return: None
        """
        allow_ = await self.allow_evaluator(ctx, mode="all", command_name="git")
        if not allow_:
            return

        await ctx.send("https://github.com/BloomAutist47/bloom-bot/")
        return

    @commands.command()
    async def credits(self, ctx):
        credit_text = "Bloom Bot and Class Charts made by Bloom Autist.\n"\
            "Thanks to [Shiminuki](https://www.youtube.com/channel/UCyQ5AocDVVDznIslRuGUS3g) and [Molevolent](https://twitter.com/molevolent) for "\
            "creating the [Class Tier List](https://docs.google.com/spreadsheets/d/1Ywl9GcfySXodGA_MtqU4YMEQaGmr4eMAozrM4r00KwI/edit?usp=sharing)."\
            "\nLastly, thanks to the @Satan and to the AutoQuest Worlds Community!"
        await ctx.send(embed=self.embed_single("Credits", credit_text))

    @commands.command()
    async def update(self, ctx, mode:str="", *, value: str=""):
        """ Description: Updates essential variables and read/saves them from github.
            Arguments:
                [ctx] - discord context
                [mode]  accepts: all, database, guides, settings, classes
                    - 'all'> updates all of the variables
                    - 'database'> self.data
                    - 'guides'> self.guides
                    - 'settings'> self.settings
                    - 'classes'> self.classes
                [value] - if certain updates require their own modes.
            Return: None
        """
        allow_ = await self.allow_evaluator(ctx, mode="user_permissions-update",
                command_name="update")
        if not allow_:
            return

        if mode=="":
            await ctx.send("\> Please enter valid update value.")

        if mode == "database":
            self.database_updating = True
            await ctx.send(r"\> Updating Bloom Bot")
            if value == "web":
                result = self.database_update("web")
            elif value == "html" or value == "":
                result = self.database_update("html")
            self.git_read("settings-database-update")
            if result:
                await ctx.send(r"\> Bloom Bot updated!")
                await ctx.send(f"\> Update method: `{self.mode}`")
            else:
                if self.settings["latest_update"] == "web":
                    await ctx.send("\> Nope. Latest method is web. Not gonna use locally saved .html\n"\
                                  "`Error 14: Already up to date`")
                else:
                    await ctx.send("\> Something's wrong. Ping the Autistic Chungus.\n"\
                                  "`Error 69: Web method.`")
            self.database_updating = False
            return

        if mode == "settings":
            self.database_updating = True
            await ctx.send(r"\>Updating `setting.json`")
            self.git_read("settings-update")
            await ctx.send(r"\>Bloom Bot `setting.json` updated!")
            self.database_updating = False
            return

        if mode == "classes":
            self.database_updating = True
            await ctx.send(r"\>Updating `classes.json`")
            self.git_read("classes-update")
            await ctx.send(r"\>Bloom Bot `classes.json` updated!")
            self.database_updating = False
            return

        if mode == "guide":
            self.database_updating = True
            await ctx.send(r"\>Updating `guides.json`")
            self.git_read("guides-update")
            await ctx.send(r"\>Bloom Bot `guides.json` updated!")
            self.database_updating = False
            return


        if mode == "all":
            self.database_updating = True
            await ctx.send(r"\>Updating `all .jsons`")
            self.git_read("all-update")
            await ctx.send(r"\>Bloom Bot `all .jsons` updated!")
            self.database_updating = False
            return

# Illegal Cog lol
class IllegalBoatSearchCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot
        self.bot.remove_command("help")

    @commands.command()
    async def bverify(self, ctx, author_name:str=""):
        """ Description: Verifies an author and adds them to the settings
                         So that bloom bot can identify their name
            Arguments:
                [ctx] - context
                [author_name] - author to be verified
        """
        allow_ = await self.allow_evaluator(ctx, mode="all-update", command_name="bverify")
        if not allow_:
            return

        if not author_name:
            await ctx.send(f"\> Please input valid author name to verify.")
            return

        if author_name.lower() in self.author_list_lowercase:
            await ctx.send(f"\> Author `{author_name}` already verified.")
            return

        self.database_updating = True
        author_name = author_name.capitalize()
        self.settings["confirmed_authors"][author_name] = {}
        try:
            self.settings["confirmed_authors"][author_name]["alias"].append(author_name)
        except:
            self.settings["confirmed_authors"][author_name]["alias"] = []
            self.settings["confirmed_authors"][author_name]["alias"].append(author_name)

        await ctx.send(r"\> Saving Bloom Bot.")
        self.file_save("settings-database")
        self.git_save("settings-database")
        await ctx.send(r"\> Updating Bloom Bot")
        self.database_update("html")

        await ctx.send(r"\> Bloom Bot updated. Author Successfully added!")
        self.database_updating = False
        return
                

    @commands.command()
    async def bunverify(self, ctx, author_name:str=""):
        """ Description: Removes an author from the settings
                         So that bloom bot cannot identify their name
            Arguments:
                [ctx] - context
                [author_name] - author to be unverified
        """
        allow_ = await self.allow_evaluator(ctx, mode="all-update", command_name="bunverify")
        if not allow_:
            return

        if not author_name:
            await ctx.send(f"\> Please input valid author name to unverify.")
            return

        author_removed = False
        self.database_updating = True
        author_name = author_name.lower()

        for author in self.settings["confirmed_authors"]:
            if author_name == author.lower() and not author_removed:
                self.settings["confirmed_authors"].pop(author, None)
                author_removed = True
                break
            aliases = self.find_author_aliases(author)
            if author_name in aliases:
                self.settings["confirmed_authors"].pop(author, None)
                author_removed = True
                break

        if not author_removed:
            await ctx.send(f"\> No author of name `{author_name}` found in the confirmed list.")
            self.database_updating = False
            return

        await ctx.send(r"\> Saving Bloom Bot.")
        self.file_save("settings-database")
        self.git_save("settings-database")
        await ctx.send(r"\> Updating Bloom Bot")
        self.file_clear_database()
        self.database_update("html")
        await ctx.send(r"\> Bloom Bot updated. Author Successfully removed!")
        self.database_updating = False
        return

    @commands.command()
    async def b(self, ctx, *, bot_name:str=""):
        """ Description: Searches the database for a boat
            Arguments:
                [ctx] - context
                [bot_name] - bot search keyword
        """

        # Conditional Checks
        allow_ = await self.allow_evaluator(ctx, mode="guild_privilege-user_permissions",
                command_name="b")
        if not allow_:
            return

        bot_name = bot_name.lower()
        allowed_word = await self.check_word_count(ctx, bot_name)
        if not allowed_word:
            return

        # Bot command search
        if bot_name == "all": # Checks if using all command
            priveleged = self.check_role_privilege(ctx, "b all")
            if not priveleged:
                return
            if priveleged:
                bot_results = self.return_all_bots()
                target = self.chunks_list(bot_results, 48)
                desc = "The following are all of the bots"
                for bot_chunk in target:
                    await ctx.send(embed=embed_multi_link("Bot Results", desc, bot_chunk))
                return

        # Actual Searching of boats 
        bot_results = self.find_bot_by_name(bot_name)
        # No boat came up.
        if not bot_results:
            desc = f"We're sorry. No boat came up with your search word: `{bot_name}`"
            await ctx.send(embed=self.embed_single("Bot Result", desc))
            return

        await self.embed_multiple_links(ctx, bot_name, bot_results)
        return

    @commands.command()
    async def a(self, ctx, *, bot_author: str=""):
        """ Description: Searches for boats by by an author
            Arguments:
                [ctx] - context
                [bot_author] - author search keyword
        """

        # Conditional Checks
        allow_ = await self.allow_evaluator(ctx, mode="guild_privilege-user_permissions",
                command_name="b")
        if not allow_:
            return

        bot_author = bot_author.lower()

        # All bot_author var is empty. Sends list of all authors.
        if bot_author == "":
            author_count = m.ceil((len(self.settings["confirmed_authors"].keys())/3))
            bot_list = sorted([author.lower() for author in self.settings["confirmed_authors"]])
            desc ='List of all verified bot authors.'
            embedVar = self.embed_multi_text("Bot Author Result", "Author", desc, bot_list, author_count, False)
            note_desc = "Some bots have unknown authors or were still not \nmanually listed in the "\
                        "confirmed list. To check bots with \nunknown authors, use command `;a u`."
            embedVar.add_field(name="Note:", value=note_desc, inline=True)
            await ctx.send(embed=embedVar)
            return

        # Checks if using author id
        if "<@!" in bot_author:
            author_id_name = self.find_author_id(bot_author)
            if author_id_name:
                bot_author = author_id_name
            else:
                bot_author = None
                desc = f"No author with id `{bot_list[0]}`."
                await ctx.send(embed=self.embed_single("Bot Author Result", desc))
                return

        # Checks if author is unknown
        if bot_author=="unknown" or bot_author=="u":
            bot_author = "Unknown"

        # Actual author command search
        result = self.find_bot_by_author(bot_author)
        found_author = result[0]    # Returns a bool if an exact author is found
        bot_list = result[1]        # List of found bots or possible authors

        # If an author is found
        if found_author:
            
            target = self.chunks_list(bot_list, 49)
            for bot_set in target:
                desc = f"The following are bots created by `{bot_author}`."
                await ctx.send(embed=self.embed_multi_link("Bot Author Result", "Link", desc, bot_set))
            return

        # if no exact author appeared
        if not found_author:
            # if author has no boats
            if len(bot_list) == 1:
                if bot_list[0] not in self.data["sort_by_bot_authors"].keys():
                    desc = f"Author `{bot_list[0]}` has not created any boats yet. "
                    await ctx.send(embed=self.embed_single("Bot Author Result", desc))
                    return
            # No author found
            if not bot_list:
                desc = f"We're sorry. No author name came up with your search word: `{bot_author}`"
                await ctx.send(embed=self.embed_single("Bot Author Result", desc))
                return

            # No exact author found but gives suggestions.
            if bot_list and not found_author:
                desc = f"Nothing came up with search key `{bot_author}`.\nMaybe one of these authors?."
                author_count = round((len(self.settings["confirmed_authors"].keys())/3))
                embedVar = self.embed_multi_text("Bot Author Result", "Author", desc, bot_list, author_count, False)
                await ctx.send(embed=embedVar)
            return


class ClassSearchCog(BaseTools, commands.Cog):

    def __init__(self, bot):
        self.setup()
        self.bot = bot
        self.bot.remove_command("help")

    @commands.command()
    async def legends(self, ctx):
        credit_text2 = "\nThanks to Shiminuki and Molevolent for creating the\nClass Tier List and "\
            "to the AuQW Community!\nType ;credits to see their links!"

        embedVar = discord.Embed(title="Legends", color=self.block_color, 
            description=f"Please read the following Carefully.")
        embedVar.set_image(url=self.settings["ClassSearchCogSettings"]["legends_link"])
        embedVar.set_footer(text=credit_text2)
        await ctx.send(embed=embedVar)
        return


    @commands.command()
    async def c(self, ctx, *, class_name: str=""):
        allow_ = await self.allow_evaluator(ctx, mode="user_permissions", command_name="c")
        if not allow_:
            return

        if class_name=="":
            desc = f"Please input a valid class name. "
            await ctx.send(embed=self.embed_single("Class Result", desc))
            return

        if len(class_name) == 1:
            desc = f"Please input a search word of atleast two character length. "
            await ctx.send(embed=self.embed_single("Class Result", desc))
            return

        # Boat Searching
        command_title = "Class Search"

        result = self.find_class(class_name.lower())
        found_class = result[0]
        found_data = result[1]
        if found_class[0] == "Authentic":
            await self.embed_image(ctx, found_data[1], found_data[2], found_data[0])
            return
        if found_class[0] == "Duplicate":
            await self.embed_image(ctx, found_data[1], found_data[2], found_data[0], [found_class[1], found_data[0]])
            return
        if found_class[0] == "Basic":
            enh = found_data[1]["enh"].capitalize()
            awe = found_data[1]["awe_enh"].capitalize()
            wiki = found_data[1]["wiki"].capitalize()
            if "note" in found_data[1]:
                note = found_data[1]["note"].capitalize()

            desc = f"```autohotkey\n[Enchancement]: {enh}\n[Awe Enchant]: {awe}\n"
            try:
                if note != "":
                    desc += f"[Note]: {note}\n"
            except: pass
            desc += "```"
            desc += f"\> [Check the Wiki]({wiki})"

            await ctx.send(embed=self.embed_single(found_data[0] + " Class", desc))
            return
        if not found_class[0] and found_data:
            desc = f'Sorry, nothing came up with your search word {class_name}.\nMaybe one of these?'
            embedVar = self.embed_multi_text(command_title, "Classes", desc, found_data, 10, False)
            await ctx.send(embed=embedVar)
            return
        if not found_class[0] and not found_data: 
            desc = f"No class matches your search word `{class_name}`. Please type exact class names."
            await ctx.send(embed=self.embed_single("Class Search Result", desc))
            return



class GuideCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot
        # self.bot.remove_command("help")
        self.fotter = "Tip: Use \";g\" to summon a list of all guides."



    @commands.command()
    async def g(self, ctx, guide=""):
        if os.name == "nt": # PC Mode
            self.file_read("guides") 

        if guide == "":
            embedVar = discord.Embed(title="♦️ List of Guide Commands ♦️", color=self.block_color)
            desc = "To summon this list, use `;g`. Please read the following carefully.\n\n"
            guild_id = str(ctx.guild.id)
            if guild_id in self.settings["server_settings"]:
                if self.settings["server_settings"][guild_id]["server_privilage"] == "Homie":
                    for guide_name in self.guides:
                        guide_data = self.guides[guide_name]
                        if "title" in guide_data:
                            desc += "`;g {}` - {}.\n".format(guide_name, guide_data["title"])
            if guild_id not in self.settings["server_settings"]:

                for guide_name in self.guides:
                    if guide_name not in self.settings["server_settings"]["Basic"]["banned_guides"]:
                        guide_data = self.guides[guide_name]
                        if "title" in guide_data:
                            desc += "`;g {}` - {}.\n".format(guide_name, guide_data["title"])
            embedVar.description = desc
            await ctx.send(embed=embedVar)
            return


        g_name = guide.lower()
        guide_mode = await self.check_guild_guide(ctx)
        if not guide_mode:
            if g_name in self.settings["server_settings"]["Basic"]["banned_guides"]:
                return

        if g_name in self.guides:
            if "common_key" in self.guides[g_name]:
                key = self.guides[g_name]["common_key"]
                guide_data = self.guides[key]
            else:
                guide_data = self.guides[g_name]


            if guide_data["type"] == "guide":
                
                embedVar = discord.Embed(title="♦️ " + guide_data["title"] + " ♦️", color=self.block_color,
                    description="The following is a short guide of %s. "\
                                "For the [Full Guide click this](%s)."%(guide_data["title"], guide_data["full_guide"]))
                embedVar.set_image(url=guide_data["short_link"])
                embedVar.set_thumbnail(url=guide_data["thumbnail"])
                embedVar.set_footer(text=self.fotter)
                await ctx.send(embed=embedVar)
                return

            if guide_data["type"] == "guide_links":

                embedVar = discord.Embed(title="♦️ " + guide_data["title"] + " ♦️", color=self.block_color)
                desc = guide_data["description"]
                for text in guide_data["content"]:
                    desc += "\> [{}]({}).\n".format(text[0], text[1])
                embedVar.description = desc
                embedVar.set_thumbnail(url=guide_data["thumbnail"])
                embedVar.set_footer(text=self.fotter)
                await ctx.send(embed=embedVar)
                return

            if guide_data["type"] == "text":
                embedVar = discord.Embed(title="♦️ " + guide_data["title"] + " ♦️", color=self.block_color)
                desc = guide_data["description"] + "\n\n"
                bullet = ""
                if "bullet" in guide_data:
                    bullet = "%s "%(guide_data["bullet"])
                if type(guide_data["content"]) is list:
                    for sentence in guide_data["content"]:
                        desc += bullet + sentence + "\n"
                else:
                    desc = guide_data["content"]
                embedVar.description = desc
                if "thumbnail" in guide_data:
                    embedVar.set_thumbnail(url=guide_data["thumbnail"])
                embedVar.set_footer(text=self.fotter)
                await ctx.send(embed=embedVar)
                return

            if guide_data["type"] == "text_dict":
                embedVar = discord.Embed(title="♦️ " + guide_data["title"] + " ♦️", color=self.block_color,
                description=guide_data["description"] + "\n\n")
                for item in guide_data["content"]:
                    desc = ""
                    for sentence in guide_data["content"][item]:
                        desc += sentence + "\n"
                    embedVar.add_field(name=item, value=desc, inline=False)
                    # embedVar.add_field(name=, value="\u200b", inline=False)
                if "thumbnail" in guide_data:
                    embedVar.set_thumbnail(url=guide_data["thumbnail"])
                embedVar.set_footer(text=self.fotter)
                await ctx.send(embed=embedVar)
                return

            if guide_data["type"] == "image":
                embedVar = discord.Embed(title="♦️ " + guide_data["title"] + " ♦️", color=self.block_color)
                embedVar.description = guide_data["description"]
                embedVar.set_image(url=guide_data["content"])
                embedVar.set_footer(text=self.fotter)
                await ctx.send(embed=embedVar)
                return


            if guide_data["type"] == "single_link":
                embedVar = discord.Embed(title="♦️ " + guide_data["title"] + " ♦️", color=self.block_color)
                if type(guide_data["description"]) is list:
                    desc = ""
                    for sentence in guide_data["description"]:
                        desc += sentence + "\n"
                else:
                    desc = guide_data["description"] + "\n"
                desc += "\> [Click this link]({}).".format(guide_data["content"])
                embedVar.description = desc
                if "thumbnail" in guide_data:
                    embedVar.set_thumbnail(url=guide_data["thumbnail"])
                embedVar.set_footer(text=self.fotter)
                await ctx.send(embed=embedVar)
                return

class CharacterCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot
        self.char_url = "https://account.aq.com/CharPage?id="
        self.wiki_url = "http://aqwwiki.wikidot.com/"
        self.weapon_type = ["Axe", "Bow", "Dagger", "Gun", "Mace", "Polearm", "Staff", "Sword", "Wand"]
        self.house_items = ["Wall Item", "Floor Item"]
        self.miscs = ["Quest Item", "Item"]
        self.loop = asyncio.get_event_loop()
        nest_asyncio.apply(self.loop)

    async def loop_get_content(self, url):
        return self.loop.run_until_complete(self.get_site_content(url))

    async def get_site_content(self, SELECTED_URL):
        client = aiosonic.HTTPClient()
        response = await client.get(SELECTED_URL)
        text_ = await response.content()
        return Soup(text_.decode('utf-8'), 'html5lib')

    async def multiple_reactions(self, embed_object):
        await embed_object.add_reaction(emoji = "\U0001F9D8") # Classes
        await embed_object.add_reaction(emoji = "\U00002694") # Swords
        await embed_object.add_reaction(emoji = "\U0001F6E1") # Armors
        await embed_object.add_reaction(emoji = "\U0001FA96") # Helm
        await embed_object.add_reaction(emoji = "\U0001F3F4") # Cape
        await embed_object.add_reaction(emoji = "\U0001F415") # Pet
        await embed_object.add_reaction(emoji = "\U0001F392") # Misc Items
        await embed_object.add_reaction(emoji = "\U0001F3C6") # Misc Items
        return


    @commands.command()
    async def char(self, ctx, *, char_name=""):
        url = self.char_url + char_name.replace(" ", "+")
        sites_soup = await self.loop_get_content(url)
        try:
            ccid = re.search("var ccid = [\d]+;", sites_soup.find_all("script")[-2].text)[0][11:-1]
        except:
            try:
                result = sites_soup.find("div", {"class": "card-body"}).find("p").text
                result = result.replace("Disabled", "**Disabled**").replace("wandering", "**wandering**")
                result += f" [Click Here]({url}) to go to their Character Page."
                await ctx.send(embed=self.embed_single("Character Profile Result", result))
                return
            except:
                await ctx.send(embed=self.embed_single("Character Profile Result", "No Character of that name"))

        body = sites_soup.find("div", {"class":"text-dark"})
        char_full_name = body.find("div", {"class":"card-header"}).find("h1").text

        # Character Details
        body_details = body.find("div", {"class": "card-body"}).find("div", {"class":"row"})
        defaults = {
            "Level": "", "Class": "", "Weapon": "", "Armor": "", "Helm": "", "Cape": "",
            "Pet": "", "Faction": "", "Guild": ""
        }

        char_details_raw = [x.text for x in body_details.select("div.col-12.col-md-6")]
        char_details = {}
        for i in char_details_raw:
            item = [x.lstrip() for x in i.split("\n")[1:-1]]
            for cat in item:
                x = cat.split(":")
                char_details[x[0]] = x[1]


        for i in defaults:
            if i not in char_details:
                char_details[i] = ""

        # Inventory stuffs
        char_inv_url = "https://account.aq.com/CharPage/Inventory?ccid="+ccid
        char_inv = self.loop.run_until_complete(self.get_site_content(char_inv_url)).find("body").text[1:-1].replace("false", "False").replace("true", "True")
        char_inv = ast.literal_eval(char_inv)

        item_count = {"Weapon": 0, "House Item": 0, "Misc": 0}
        for item in char_inv:
            item_type = item["strType"]
            if item_type in self.weapon_type:
                item_count["Weapon"] += 1
                continue
            if item_type in self.miscs:
                item_count["Misc"] += 1
                continue
            if item_type not in item_count and item_type:
                item_count[item_type] = 0
            item_count[item_type] += 1

        item_default = ['Armor', 'Cape', 'Class', 'Floor Item', 'Helm',
            'House', 'House Item', 'Misc', 'Necklace', 'Pet',
            'Wall Item', 'Weapon']

        for item in item_default:
            if item not in item_count:
                item_count[item] = 0

        # Inserts stuffs
        embedVar = discord.Embed(title=f"Character Profile", color=self.block_color, description="\u200b")
        embedVar.description = f"__**Name**__: [{char_full_name}](https://account.aq.com/CharPage?id={char_full_name.replace(' ', '+')})."
        li = self.wiki_url
        panel_1_raw = [f"**Level**: {char_details['Level']}" + "\n",
                f"**Class**: [{char_details['Class']}]({li + char_details['Class'].lstrip().replace(' ', '-')})" + "\n",
                f"**Faction**: {char_details['Faction']}" + "\n",
                f"**Guild**: {char_details['Guild']}" + "\n",
                "\u200b".ljust(27, "")]


        panel_2 = f"**Weapon**: [{char_details['Weapon']}]({li+char_details['Weapon'].lstrip().replace(' ', '-')})\n"\
                f"**Armor**: [{char_details['Armor']}]({li+char_details['Armor'].lstrip().replace(' ', '-')})\n"\
                f"**Helm**: [{char_details['Helm']}]({li+char_details['Helm'].lstrip().replace(' ', '-')})\n"\
                f"**Cape**: [{char_details['Cape']}]({li+char_details['Cape'].lstrip().replace(' ', '-')})\n"\
                f"**Pet**: [{char_details['Pet']}]({li+char_details['Pet'].lstrip().replace(' ', '-')})\n"

        vl = 24
        inventories_ =["```css\n",
                      f"Classes: {item_count['Class']}".ljust(vl) + f"Miscs: {item_count['Misc']}\n",
                      f"Weapons: {item_count['Weapon']}".ljust(vl) + f"Pets: {item_count['Pet']}\n",
                      f"Armors: {item_count['Armor']}".ljust(vl) + f"Houses: {item_count['House']}\n",
                      f"Helms: {item_count['Helm']}".ljust(vl) + f"Wall Items: {item_count['Wall Item']}\n",
                      f"Capes: {item_count['Cape']}".ljust(vl) + f"Floor Items: {item_count['Floor Item']}```\n",
                      ]
        panel_1 = ""
        for i in panel_1_raw:
            panel_1 += i

        inventories_2 = ""
        for i in inventories_:
            inventories_2 += i

        embedVar.add_field(name="__**Infos**__", value=panel_1, inline=True)
        embedVar.add_field(name="__**Equips**__", value=panel_2, inline=True)
        embedVar.add_field(name="__**Inventory**__", value=inventories_2, inline=False)



        # embedVar.set_thumbnail(url="https://cdn.discordapp.com/attachments/805367955923533845/807570293501591572/logo-lg-AQW.png")

        embed_object = await ctx.send(embed=embedVar)
        return

    # @commands.command()
    # async def charinv(self, ctx):
    #     url = self.char_url + char_name.replace(" ", "+")
    #     sites_soup = await self.loop_get_content(url)
    #     try:
    #         ccid = re.search("var ccid = [\d]+;", sites_soup.find_all("script")[-2].text)[0][11:-1]
    #     except:
    #         try:
    #             result = sites_soup.find("div", {"class": "card-body"}).find("p").text
    #             result = result.replace("Disabled", "**Disabled**").replace("wandering", "**wandering**")
    #             result += f" [Click Here]({url}) to go to their Character Page."
    #             await ctx.send(embed=self.embed_single("Character Profile Result", result))
    #             return
    #         except:
    #             await ctx.send(embed=self.embed_single("Character Profile Result", "No Character of that name"))

    #     embedVar = discord.Embed(title="Character Profile Help", color=self.block_color)

    #     # Get Badges
    #     char_badge_url = "https://account.aq.com/CharPage/Badges?ccid="+ccid
    #     char_badges = self.loop_get_content(char_badge_url).find("body").text[1:-1]
    #     char_badges = ast.literal_eval(char_badges)

    #     # Get Inventory
    #     char_inv_url = "https://account.aq.com/CharPage/Inventory?ccid="+ccid
    #     char_inv_raw = await self.loop_get_content(char_inv_url)
    #     char_inv = char_inv_raw.find("body").text[1:-1].replace("false", "False").replace("true", "True")
    #     char_inv = ast.literal_eval(char_inv)

    #     # Categorize the items
    #     items = {}
    #     for item in char_inv:
    #         item_type = item["strType"]
    #         if item_type not in items:
    #             items[item_type] = []
    #         items[item_type].append(item)

    #     

    #     await ctx.send(embed=embedVar)
    #     return

# class EventCalendarCog(commands.Cog):
#     def __init__(self, bot, *args, **kwargs):
#         self.bot = bot
#         self.block_color = 3066993

#         self.counter = 0
#         self.my_background_task.start()

#     @tasks.loop(seconds=10.0)
#     async def my_background_task(self):

            
class EventCalendarCog(commands.Cog, BaseTools):
    def __init__(self, Bot):
        self.setup()
        self.bot = Bot

        self.est_dt = datetime.now(timezone('est'))
        self.current_day = self.est_dt.strftime("%d")
        self.current_month = self.est_dt.strftime("%B")

        self.events = self.settings["EventCalendarCogSettings"]["events"]
        self.check_current_month()

        self.printer.start()


    async def get_site_content(self, SELECTED_URL):
        client = aiosonic.HTTPClient()
        response = await client.get(SELECTED_URL)
        text_ = await response.content()
        return Soup(text_.decode('utf-8'), 'html5lib')

    def check_current_month(self):
        self.current_month = self.est_dt.strftime("%B")
        if self.current_month != self.settings["EventCalendarCogSettings"]["latest_update"]:
            self.settings["EventCalendarCogSettings"]["latest_update"] = self.current_month
            self.check_calendar()
            self.file_save("settings")
            self.git_save("settings")
            print("System: Updated month EventCalendarCogSettings[\"events\"].")
        else:
            print("System: Not updating month EventCalendarCogSettings[\"events\"].")
        return

    def check_calendar(self):
        url = "https://www.aq.com/aq.com/lore/calendar"
        loop = asyncio.get_event_loop()
        sites_soup = loop.run_until_complete(self.get_site_content(url))
        body = sites_soup.find("section", {"id":"main-content"}).find("div", class_="container").find("div", class_="row").find_all("div", class_="col-xs-12 col-sm-12 col-md-12 col-lg-12")[1]
        list_of_events_raw = body.find_all("p")[2:]

        for i in list_of_events_raw:
            data = unicodedata.normalize("NFKD", i.text)
            data = re.split(r"([\w]+\s[\d]+\s)", data)[1:]
            date = data[0].strip().split(" ")
            info = data[1].split("                  ")
            day = date[1].zfill(2)
            # self.events = {}
            self.events[day] = {}
            self.events[day]["month"] = date[0]
            self.events[day]["info"] = info
        self.settings["EventCalendarCogSettings"]["events"] = self.events
        self.file_save("settings")
        self.git_save("settings")
        return

    async def check_event_today(self):

        if self.current_day in self.events:
            if self.events[self.current_day]["month"] == self.current_month:
                info = self.events[self.current_day]["info"]
                return info
        else:
            return None


    @tasks.loop(seconds=3600)
    async def printer(self):
        self.current_day = self.est_dt.strftime("%d")
        print("Checked", self.current_day)
        if self.current_day != self.settings["EventCalendarCogSettings"]["current_day"]:
            for guild in self.bot.guilds:
                print(f"Guild: {guild}\tID: {guild.id}")
                if os.name == "nt":
                    # Testing
                    channel = await self.bot.fetch_channel(799238286539227136)
                else:
                    guild_id = str(guild.id)
                    if guild_id not in self.settings["server_settings"]:
                        continue
                    else:
                        try:
                            guild_set = self.settings["server_settings"][guild_id]
                            channel = await self.bot.fetch_channel(guild_set["event_channel_id"])
                        except:
                            continue 

                self.settings["EventCalendarCogSettings"]["current_day"] = self.current_day
                self.file_save("settings")
                self.git_save("settings")
                result = await self.check_event_today()
                if not result:
                    return
                if result:
                    if os.name == "nt":
                        desc = "\> <@&807655230467604510>\n"
                    else:
                        desc = f"\> <@&{str(guild_set['server_noice_role'])}>\n"
                    for text in result:
                        desc += f"\> {text.strip()}"
                    await channel.send(embed=self.embed_single("Event Today", desc))
                    return
            return

    @printer.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()

intents = Intents.all()
Bot = commands.Bot(command_prefix=[";", ":"], description='Bloom Bot Revamped', intents=intents)

@Bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        print("System: lmao a nigger used", error)
        return
    raise error

@Bot.event
async def on_member_update(before, after):
    print("WORKING")
    satanId = 212913871466266624
    if os.name == "nt":
        satanRoleId = 808657429784035338
        guild_id = 761956630606250005
    else:
        satanRoleId = 775824347222245426
        guild_id = 766627412179550228

    guild = Bot.get_guild(guild_id)
    role = dis_get(guild.roles, name='satan', id=satanRoleId)
    role_ids = [x.id for x in after.roles]

    if after.id != satanId and satanRoleId in role_ids:
        print("TRIED")
        await after.remove_roles(role)



@Bot.event
async def on_ready():
    print('Starting Bloom bot 2')
    if os.name == "nt":
        channel = Bot.get_channel(799238286539227136)
        await channel.send("HOLA")
    name = "A bot Created by Bloom Autist. Currently Beta V.1.4.8.01"
    await Bot.change_presence(status=discord.Status.idle,
        activity=discord.Game(name=name, type=3))


if os.name == "nt": # PC Mode
    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN2') # test bot token
else:              # Heroku
    DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

# Essential Cog
Bot.add_cog(BaseCog(Bot))

# Feature Cogs
# Bot.add_cog(IllegalBoatSearchCog(Bot))
# Bot.add_cog(ClassSearchCog(Bot))
# Bot.add_cog(GuideCog(Bot)) 
# Bot.add_cog(CharacterCog(Bot))
# Bot.add_cog(EventCalendarCog(Bot))
Bot.run(DISCORD_TOKEN)