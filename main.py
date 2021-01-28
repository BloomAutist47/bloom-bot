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

from dotenv import load_dotenv
from bs4 import BeautifulSoup as Soup
from discord.ext import commands
# from discord_slash import cog_ext
# from discord_slash import SlashCommand
# from discord_slash import SlashContext
from pprint import pprint

class BreakProgram(Exception):
    pass

class BloomBot(commands.Cog):
    def __init__(self, bot):
        self.setup()
        self.command_description_lists()
        self.database_update("web")
        self.bot = bot
        self.block_color = 3066993
        self.database_updating = False
        

    def setup(self):
        self.env_variables()

        self.url = "https://adventurequest.life/"
        self.settings = {}
        self.classes = {}
        self.data = {}
        self.sets = {}
        self.priveleged_roles = []
        self.mode = ""
        self.author_list_lowercase = []

        self.github = github3.login(token=self.GIT_BLOOM_TOKEN)
        self.repository = self.github.repository(self.GIT_USER, self.GIT_REPOS)

        self.file_read()
        self.git_read()

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
        """Description: Updates the database.json
           Arguments:
           [mode] accepts 'web', 'html'
                - 'web': scrapes directly from the self.url
                - 'html': uses pre-downloaded html of self.url
        """
        self.git_read()
        self.file_clear_database()
        self.data["sort_by_bot_name"] = {}
        self.data["sort_by_bot_authors"] = {}

        if mode == "web":
            try:

                headers = {
                    'User-Agent': self.PORTAL_AGENT
                }
                row = []
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
                self.git_read()
                return False

        elif mode == "html":
            if self.settings["latest_update"] == "web":
                # Checks if the latest update method is web, i.e. the latest most way
                # of updating this.
                print("Didn't update. latest update is Web")
                self.git_read()
                return False
            else:
                self.settings["latest_update"] = "html"
                self.mode = "html"
            try:
                soup = Soup(open("./Data/html/aqw.html", encoding="utf8"), "html.parser")
                body = soup.find("table", {"id":"table_id", "class":"display"}).find("tbody")
                row = body.find_all("tr")
            except:
                self.git_read()
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
        self.file_save()
        self.git_save()
        print("lmao")
        return True

    def file_clear_database(self):
        """Description: Clears the database.json"""
        with open('./Data/database.json', 'w', encoding='utf-8') as f:
            json.dump({}, f, ensure_ascii=False, indent=4)

    def file_set_save(self):
        """Description: Saves self.Sets on pre-saved sets.json"""
        with open('./Data/sets.json', 'w', encoding='utf-8') as f:
            json.dump(self.sets, f, ensure_ascii=False, indent=4)


    def file_read(self):
        """Description: Reads pre-saved .json files"""
        with open('./Data/database.json', 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        with open('./Data/sets.json', 'r', encoding='utf-8') as f:
            self.sets = json.load(f)
        with open('./Data/settings.json', 'r', encoding='utf-8') as f:
            self.settings = json.load(f)
        with open('./Data/classes.json', 'r', encoding='utf-8') as f:
            self.classes = json.load(f)
        self.priveleged_roles = []
        for role in self.settings["priveleged_roles"]:
            if self.settings["priveleged_roles"][role] == 1:
                self.priveleged_roles.append(role)

        self.author_list_lowercase = []
        for author in self.settings["confirmed_authors"]:
            self.author_list_lowercase.append(author.lower())
            for alias in self.settings["confirmed_authors"][author]["alias"]:
                self.author_list_lowercase.append(alias.lower())

    def file_save(self):
        """Description: Saves data to pre-saved .json files"""
        with open('./Data/database.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        with open('./Data/settings.json', 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def git_save(self):
        """Description: Saves data to github .json files"""
        git_data = json.dumps(self.data, indent=4).encode('utf-8')
        contents_object = self.repository.file_contents("./Data/database.json")
        contents_object.update("update", git_data)

        git_sets = json.dumps(self.sets, indent=4).encode('utf-8')
        contents_object = self.repository.file_contents("./Data/sets.json")
        contents_object.update("update", git_sets)

        git_settings = json.dumps(self.settings, indent=4).encode('utf-8')
        contents_object = self.repository.file_contents("./Data/settings.json")
        contents_object.update("update", git_settings)

        self.file_save()

    def git_read(self):
        """Description: Reads data from github .json files"""
        git_data = self.repository.file_contents("./Data/database.json").decoded
        self.data = json.loads(git_data.decode('utf-8'))

        git_sets = self.repository.file_contents("./Data/sets.json").decoded
        self.sets = json.loads(git_sets.decode('utf-8'))

        git_classes = self.repository.file_contents("./Data/classes.json").decoded
        self.classes = json.loads(git_classes.decode('utf-8'))

        git_settings = self.repository.file_contents("./Data/settings.json").decoded
        self.settings = json.loads(git_settings.decode('utf-8'))
        self.priveleged_roles = []
        for role in self.settings["priveleged_roles"]:
            if self.settings["priveleged_roles"][role] == 1:
                self.priveleged_roles.append(role)

        self.author_list_lowercase = []
        for author in self.settings["confirmed_authors"]:
            self.author_list_lowercase.append(author.lower())
            for alias in self.settings["confirmed_authors"][author]["alias"]:
                self.author_list_lowercase.append(alias.lower())
                

        # Saving
        self.file_save()
        self.file_set_save()

    """ SEARCH METHODS SECTION """
    def find_bot_by_name(self, bot_name_value):
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
        for class_name_ in self.classes:
            # Search if exact name
            if class_name == class_name_.lower():
                return (True, (class_name_, self.classes[class_name_]))
            duplicates = [dn.lower() for dn in self.classes[class_name_]["duplicates"]]

            # Search duplicate classes
            if class_name in duplicates:
                ind = duplicates.index(class_name)
                return (True, (self.classes[class_name_]["duplicates"][ind], self.classes[class_name_]))

            # if class_name_ in class_name_.lower():
            #     possible_classes.append(class_name_)
            # for duplicate in duplicates:
            #     if class_name_ in duplicate:
            #         possible_classes.append(duplicate)

            #Search keyword likeness
            class_words = class_name.split(" ")
            for words in class_words:
                if words in class_name_.lower():
                    possible_classes.append(class_name_)
                for duplicate in duplicates:
                    if words in duplicate:
                        ind = duplicates.index(duplicate)
                        possible_classes.append(self.classes[class_name_]["duplicates"][ind])
        if possible_classes:
            return (False, possible_classes)
        else:
            return (False, [])




    def command_description_lists(self):
        self.desc_dict = {"boat":
            "A command for searching boats. Cannot accept keywords whose length are less than 3 chars, "\
            "however, accepts numerical keywords of any length.",
            }

        

    async def check_word_count(self, ctx, value):
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

    async def check_permissions(self, ctx, command_name):
        if str(ctx.author.id) not in self.PERMISSIONS:
            return True
        else:
            desc = f"\> User {ctx.author} does not have permissions for `;{command_name}` command.\n"
            await ctx.send(desc)
            return False

    async def check_privilege(self, ctx, command_name):
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

    async def check_author_id(self, ctx, bot_author):
        author_id_name = self.find_author_id(bot_author)
        if author_id_name:
            return author_id_name
        else:
            await ctx.send(embed=self.embed_single("Bot Author Result", "No verified author of that name."))
            return None

    @commands.command()
    async def update(self, ctx, value: str=""):
        permissions_check = await self.check_permissions(ctx, "update")
        if not permissions_check:
            return

        priveleged = await self.check_privilege(ctx, "update")
        if not priveleged:
            return

        if value not in ["web", "html", ""]:
            await ctx.send(r"\> Please input valid value")
            return

        if self.database_updating:
            await ctx.send(r"\> Bloom Bot update in progress.")
            return
        if not self.database_updating:
            self.database_updating = True
            await ctx.send(r"\> Updating Bloom Bot")
            if value == "web" or value == "":
                result = self.database_update("web")
            elif value == "html":
                result = self.database_update("html")
            self.git_read()
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
        

    @commands.command()
    async def verify(self, ctx, author_name="", author_id="", brief='Author Verification command'):
        permissions_check = await self.check_permissions(ctx, "verify author")
        if not permissions_check:
            return

        priveleged = await self.check_privilege(ctx, "verify author")
        if not priveleged:
            await ctx.send(f"\> User {ctx.author} does not have permissions for `;verify author @author` command.\n")
            return

        if not author_name:
            await ctx.send(f"\> Please input valid author name to verify.")
            return

        if author_name.lower() in self.author_list_lowercase:
            await ctx.send(f"\> Author `{author_name}` already verified.")
            return

        if self.database_updating:
            await ctx.send(r"\> Bloom Bot update in progress.")
            return

        self.database_updating = True
        if author_id != "":
            try:
                author_id = re.sub("<|>|!|@","", author_id)
            except:
                await ctx.send(r"\> Please input valid author ID.")
                return
        

        author_name = author_name.capitalize()
        self.settings["confirmed_authors"][author_name] = {}
        try:
            self.settings["confirmed_authors"][author_name]["alias"].append(author_name)
        except:
            self.settings["confirmed_authors"][author_name]["alias"] = []
            self.settings["confirmed_authors"][author_name]["alias"].append(author_name)
        if x:
            self.settings["confirmed_authors"][author_name]["id"] = author_id
        else:
            self.settings["confirmed_authors"][author_name]["id"] = ""
        await ctx.send(r"\> Saving Bloom Bot.")
        self.git_save()
        await ctx.send(r"\> Updating Bloom Bot")
        self.database_update("web")
        await ctx.send(r"\> Bloom Bot updated. Author Successfully added!")
        self.database_updating = False
        return
                

    @commands.command()
    async def unverify(self, ctx, author_name="", brief='Author Removal command'):
        permissions_check = await self.check_permissions(ctx, "verify author")
        if not permissions_check:
            return

        priveleged = await self.check_privilege(ctx, "unverify author")
        if not priveleged:
            await ctx.send(f"\> User {ctx.author} does not have permissions for `;unverify author` command.\n")
            return

        if not author_name:
            await ctx.send(f"\> Please input valid author name to unverify.")
            return

        if self.database_updating:
            await ctx.send(r"\> Bloom Bot update in progress.")
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
        self.git_save()
        await ctx.send(r"\> Updating Bloom Bot")
        self.database_update("web")
        await ctx.send(r"\> Bloom Bot updated. Author Successfully removed!")
        self.database_updating = False
        return

    @commands.command()
    async def git(self, ctx):
        permissions_check = await self.check_permissions(ctx, "git")
        if not permissions_check:
            return

        await ctx.send("https://github.com/BloomAutist47/bloom-bot/")
        return

    @commands.command()
    async def b(self, ctx, *, bot_name: str="",
        brief='Bot Searching command'):

        # Conditional Checks
        bot_name = bot_name.lower()
        permissions_check = await self.check_permissions(ctx, "b bot_name")
        if not permissions_check:
            return

        allowed_word = await self.check_word_count(ctx, bot_name)
        if not allowed_word:
            return

        # Bot command search
        if bot_name == "all": # Checks if using all command
            priveleged = self.check_privilege(ctx, "b all")
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

    @commands.command()
    async def a(self, ctx, *, bot_author: str=""):
        # Conditional Checks
        permissions_check = await self.check_permissions(ctx, "a author")
        if not permissions_check:
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
            bot_author = await self.check_author_id(ctx, bot_author)
            if not bot_author:
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

    @commands.command()
    async def c(self, ctx, *, class_name: str=""):
        # Conditional Checks
        permissions_check = await self.check_permissions(ctx, "a author")
        if not permissions_check:
            return

        command_title = "Class Search"

        result = self.find_class(class_name.lower())
        found_class = result[0]
        found_data = result[1]

        if class_name=="":
            desc = f"Please input a valid class name. "
            await ctx.send(embed=self.embed_single("Class Search Result", desc))
            return

        if not found_class and not found_data:
            desc = f"No class matches your search word `{class_name}`. Please type exact class names. "
            await ctx.send(embed=self.embed_single("Class Search Result", desc))
            return
        if found_class and found_data:
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
        if not found_class and found_data:
            desc = f'Sorry, nothing came up with your search word {class_name}.\nMaybe one of these?'
            embedVar = self.embed_multi_text(command_title, "Classes", desc, found_data, 10, False)
            await ctx.send(embed=embedVar)
            return


    def embed_single(self, title, description):
         return discord.Embed(title=title, description=description, color=self.block_color)

    def chunks_list(self, lst, n):
        # Yield successive n-sized chunks from lst.
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    async def embed_multiple_links(self, ctx, bot_name, bot_results):
        # Properties
        st = "\u200b"
        bot_list = ""
        inline = False
        counts = {"field": 0, "item": 0, "total":0}
        title = "Bot Results"
        desc = "The following matches your keyword: `{}`".format(bot_name)

                    # if counts["field"] == 2:
                    #     embedVar.add_field(name=st, value=st, inline=inline)
                    #     counts["field"] = 0

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
                        # counts["field"] += 1
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

    def embed_multi_text(self, title, field_name, description, value_list, block_count, two_collumn):
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

# class Slash(commands.Cog):
#     def __init__(self, bot):
#         if not hasattr(bot, "slash"):
#             # Creates new SlashCommand instance to bot if bot doesn't have.
#             bot.slash = SlashCommand(bot, override_type=True)
#         self.bot = bot
#         self.bot.slash.get_cog_commands(self)

#     def cog_unload(self):
#         self.bot.slash.remove_cog_commands(self)

#     # @cog_ext.cog_slash(name="test")
#     # async def _test(self, ctx: SlashContext):
#     #     embed = discord.Embed(title="embed test")
#     #     await ctx.send(content="test", embeds=[embed])

#     @cog_ext.cog_slash(name="pingpong")
#     async def _ping(self, ctx): # Defines a new "context" (ctx) command called "ping."
#         await ctx.send(content=f"HOLA NIGGERS")



Bot = commands.Bot(command_prefix=[";", ":"], description='Bloom Bot Revamped')

@Bot.event
async def on_ready():
    # Bot.BloomBot.database_update("web")
    print('Starting Bloom bot 2')
    if os.name == "nt":
        await Bot.get_channel(799238286539227136).send('hello')
    name = "A bot Created by Bloom Autist. Currently Beta V.1.4.0."
    await Bot.change_presence(status=discord.Status.idle,
        activity=discord.Game(name=name, type=3))


if os.name == "nt": # PC Mode
    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN2') # test bot token
else:              # Heroku
    DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

Bot.add_cog(BloomBot(Bot))
# Bot.add_cog(Slash(Bot))


Bot.run(DISCORD_TOKEN)