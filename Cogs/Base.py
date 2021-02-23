
import os
import re
import json
import github3
import requests
import asyncio
import aiosonic
import aiohttp
import discord
import nest_asyncio
import html5lib

from discord.ext import commands
from bs4 import BeautifulSoup as Soup
from dotenv import load_dotenv



os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir('..')

class BaseProgram:
    data = {}
    settings = {}
    database_updating = False
    classes = {}
    priveleged_roles = []
    mode = ""
    author_list_lowercase = []
    class_acronyms = {}
    guides = {}
    loop = asyncio.get_event_loop()
    loop_2 = asyncio.new_event_loop()
    nest_asyncio.apply(loop)
    sqlock = True
    texts = {}
    tweet_text = ""
    block_color = 3066993


    url = "https://adventurequest.life/"
    CONSUMER_KEY = ""
    CONSUMER_SECRET = ""
    ACCESS_TOKEN = ""
    ACCESS_TOKEN_SECRET = ""

    DISCORD_TOKEN = ""
    PERMISSIONS = ""
    PORTAL_AGENT = ""

    tweets_listener = ""
    streams = ""

    git_already = False
    

    icon_bloom = "https://cdn.discordapp.com/attachments/805367955923533845/813066459281489981/icon3.png"
    icon_aqw = "https://cdn.discordapp.com/attachments/805367955923533845/812991601714397194/logo_member.png"
    icon_auqw = "https://images-ext-2.discordapp.net/external/HYh_FWKYc_DqZZAmoIg1ZR0sMSB34aDf0YAFGGLFGSE/%3Fsize%3D1024/https/cdn.discordapp.com/icons/782192889723748362/a_d4c8307eb1dc364f207183a2ee144b4d.gif"
    icon_aqw_g = "https://cdn.discordapp.com/attachments/805367955923533845/813015948256608256/aqw.png"
    icon_google = "https://cdn.discordapp.com/attachments/805367955923533845/813340480330137650/google_chrome_new_logo-512.png"

    icons = {
                "auqw": {
                    "title": "AutoQuest Worlds",
                    "icon": icon_auqw
                },
                "aqw": {
                    "title": "AdventureQuest Worlds",
                    "icon": icon_aqw
                }
            }

    usr_agent = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/61.0.3163.100 Safari/537.36'}

    def git_prepare(self):
        self.env_variables()
        
        while True:
            try:
                # self.block_color = 4521077
                BaseProgram.github = github3.login(token=BaseProgram.GIT_BLOOM_TOKEN)
                BaseProgram.repository = BaseProgram.github.repository(BaseProgram.GIT_USER, BaseProgram.GIT_REPOS)
                print("> Github Connection...Success!")
                break
            except: 
                print("> Failed Connecting to Github... Trying again.")
                print("> Reconnecting...")
                continue

        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        os.chdir('..')
        self.file_read("all")
        self.git_read("all")

    def env_variables(self):
        if os.name == "nt": # PC Mode

            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            load_dotenv()
            BaseProgram.DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN2') # test bot token
            BaseProgram.GIT_REPOS = os.getenv('GITHUB_REPOS')
            BaseProgram.GIT_USER = os.getenv('GITHUB_USERNAME')
            BaseProgram.GIT_BLOOM_TOKEN = os.getenv('GITHUB_BLOOMBOT_TOKEN')
            BaseProgram.PERMISSIONS = os.getenv("PRIVILEGED_ROLE").split(',')
            BaseProgram.PORTAL_AGENT = os.getenv('PORTAL_AGENT')

            BaseProgram.CONSUMER_KEY = os.getenv('TWITTER_NOTIFIER_API_KEY')
            BaseProgram.CONSUMER_SECRET = os.getenv('TWITTER_NOTIFIER_API_KEY_SECRET')
            BaseProgram.ACCESS_TOKEN = os.getenv('TWITTER_NOTIFIER_ACCESS_TOKEN')
            BaseProgram.ACCESS_TOKEN_SECRET = os.getenv('TWITTER_NOTIFIER_ACCESS_TOKEN_SECRET')

        else:              # Heroku
            BaseProgram.DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
            BaseProgram.GIT_REPOS = os.environ.get('GITHUB_REPOS')
            BaseProgram.GIT_USER = os.environ.get('GITHUB_USERNAME')
            BaseProgram.GIT_BLOOM_TOKEN = os.environ.get('GITHUB_BLOOMBOT_TOKEN')
            BaseProgram.PERMISSIONS = os.environ.get("PRIVILEGED_ROLE").split(',')
            BaseProgram.PORTAL_AGENT = os.environ.get("PORTAL_AGENT")

            BaseProgram.CONSUMER_KEY = os.environ.get('TWITTER_NOTIFIER_API_KEY')
            BaseProgram.CONSUMER_SECRET = os.environ.get('TWITTER_NOTIFIER_API_KEY_SECRET')
            BaseProgram.ACCESS_TOKEN = os.environ.get('TWITTER_NOTIFIER_ACCESS_TOKEN')
            BaseProgram.ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_NOTIFIER_ACCESS_TOKEN_SECRET')

    def database_update(self, mode: str):
        """ Description: Updates the database.json
            Arguments:
            [mode] accepts 'web', 'html'
                - 'web': scrapes directly from the BaseProgram.url
                - 'html': uses pre-downloaded html of BaseProgram.url
            Return: Bool
        """

        self.git_read("settings")
        self.file_clear_database()
        BaseProgram.data["sort_by_bot_name"] = {}
        BaseProgram.data["sort_by_bot_authors"] = {}

        if mode == "web":
            # try:
            headers = {
                'User-Agent': "DiscordBot"
            }
            row = []
            try:
                html = requests.get(BaseProgram.url, headers=headers).text
                page_soup = Soup(html, "html.parser")
                body = page_soup.find("table", {"id":"table_id", "class":"display"}).find("tbody")
                row_links = body.find_all("input", {"class":"rainbow"})

                for value in row_links:
                    link = BaseProgram.url + "bots/" + value["value"]
                    row.append(link)

                BaseProgram.settings["latest_update"] = "web"
                BaseProgram.mode = "web"
            except:
                self.git_read("database-settings")
                return False

        elif mode == "html":
            if BaseProgram.settings["latest_update"] == "web":
                # Checks if the latest update method is web, i.e. the latest most way
                # of updating this.
                print("Didn't update. latest update is Web")
                self.git_read("database-settings")
                return False
            else:
                BaseProgram.settings["latest_update"] = "html"
                BaseProgram.mode = "html"
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
            if raw_author in BaseProgram.settings["confirmed_authors"]:
                bot_author = raw_author
            else:
                raw_author = item_name
                try:
                    for verified_author in BaseProgram.settings["confirmed_authors"]:
                        for alias in BaseProgram.settings["confirmed_authors"][verified_author]["alias"]:
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
                alias = [alias for alias in BaseProgram.settings["confirmed_authors"][bot_author]["alias"]]
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
            BaseProgram.data["sort_by_bot_name"][bot_name] = {}
            BaseProgram.data["sort_by_bot_name"][bot_name]["url"] = link
            BaseProgram.data["sort_by_bot_name"][bot_name]["author"] = bot_author

            # Sort by Author
            if bot_author not in BaseProgram.data["sort_by_bot_authors"]:
                BaseProgram.data["sort_by_bot_authors"][bot_author] = {}
                
            BaseProgram.data["sort_by_bot_authors"][bot_author][bot_name] = {}
            BaseProgram.data["sort_by_bot_authors"][bot_author][bot_name]["url"] = link


        # Saving
        self.file_save("database-settings")
        self.git_save("database-settings")
        print("========DATABASE===========")
        print("===================")
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
                    - 'database'> BaseProgram.data
                    - 'guides'> BaseProgram.guides
                    - 'settings'> BaseProgram.settings
                    - 'classes'> BaseProgram.classes
        """

        mode = mode.split("-")
        if mode == ["all"]:
            mode = ["database", "guides", "classes", "settings", "texts" , "streams"]

        if "database" in mode:
            with open('./Data/database.json', 'r', encoding='utf-8') as f:
                BaseProgram.data = json.load(f)
        if "guides" in mode:
            with open('./Data/guides.json', 'r', encoding='utf-8') as f:
                BaseProgram.guides = json.load(f)
        if "classes" in mode:   
            with open('./Data/classes.json', 'r', encoding='utf-8') as f:
                BaseProgram.classes = json.load(f)
            self.sort_classes_acronym()

        if "settings" in mode:
            with open('./Data/settings.json', 'r', encoding='utf-8') as f:
                BaseProgram.settings = json.load(f)

        if "texts" in mode:
            with open('./Data/texts.json', 'r', encoding='utf-8') as f:
                BaseProgram.texts = json.load(f)

        if "streams" in mode:
            with open('./Data/streams.json', 'r', encoding='utf-8') as f:
                BaseProgram.streams = json.load(f)


        self.sort_privileged_roles()
        self.sort_author_list_lowercase()

    def file_save(self, mode:str):
        """ Description: Saves data to local .json files
            Arguments:
                [mode] - checks to do. accepts: database, guides, settings, classes
                         or any of the their combination delimited by "-"
                    - 'database'> BaseProgram.data
                    - 'guides'> BaseProgram.guides
                    - 'settings'> BaseProgram.settings
                    - 'classes'> BaseProgram.classes
        """
        mode = mode.split("-")
        if mode == ["all"]:
            mode = ["database", "guides", "classes", "settings", "streams"]

        if "database" in mode:
            with open('./Data/database.json', 'w', encoding='utf-8') as f:
                json.dump(BaseProgram.data, f, ensure_ascii=False, indent=4)
        if "guides" in mode:
            with open('./Data/guides.json', 'w', encoding='utf-8') as f:
                json.dump(BaseProgram.guides, f, ensure_ascii=False, indent=4)
        if "classes" in mode:
            with open('./Data/classes.json', 'w', encoding='utf-8') as f:
                json.dump(BaseProgram.classes, f, ensure_ascii=False, indent=4)
            self.sort_classes_acronym()
        if "settings" in mode:
            with open('./Data/settings.json', 'w', encoding='utf-8') as f:
                json.dump(BaseProgram.settings, f, ensure_ascii=False, indent=4)
        if "texts" in mode:
            with open('./Data/texts.json', 'w', encoding='utf-8') as f:
                json.dump(BaseProgram.texts, f, ensure_ascii=False, indent=4)
        if "streams" in mode:
            with open('./Data/streams.json', 'w', encoding='utf-8') as f:
                json.dump(BaseProgram.streams, f, ensure_ascii=False, indent=4)



    def git_save(self, mode:str):
        """ Description: Saves data to github .json files
            Arguments:
                [mode] - checks to do. accepts: database, guides, settings, classes
                         or any of the their combination delimited by "-"
                    - 'database'> BaseProgram.data
                    - 'guides'> BaseProgram.guides
                    - 'settings'> BaseProgram.settings
                    - 'classes'> BaseProgram.classes
        """
        mode = mode.split("-")
        if mode == ["all"]:
            mode = ["database", "guides", "classes", "settings", "streams"]

        if "database" in mode:
            git_data = json.dumps(BaseProgram.data, indent=4).encode('utf-8')
            contents_object = BaseProgram.repository.file_contents("./Data/database.json")
            contents_object.update("update", git_data)
            self.file_save("database")

        if "guides" in mode:
            git_guides = json.dumps(BaseProgram.guides, indent=4).encode('utf-8')
            contents_object = BaseProgram.repository.file_contents("./Data/guides.json")
            contents_object.update("update", git_guides)
            self.file_save("guides")

        if "settings" in mode:
            git_settings = json.dumps(BaseProgram.settings, indent=4).encode('utf-8')
            contents_object = BaseProgram.repository.file_contents("./Data/settings.json")
            contents_object.update("update", git_settings)
            self.file_save("settings")

        if "classes" in mode:
            git_classes = json.dumps(BaseProgram.classes, indent=4).encode('utf-8')
            contents_object = BaseProgram.repository.file_contents("./Data/classes.json")
            contents_object.update("update", git_classes)
            self.file_save("classes")

        if "texts" in mode:
            git_texts = json.dumps(BaseProgram.texts, indent=4).encode('utf-8')
            contents_object = BaseProgram.repository.file_contents("./Data/texts.json")
            contents_object.update("update", git_texts)
            self.file_save("texts")

        if "streams" in mode:
            git_streams = json.dumps(BaseProgram.streams, indent=4).encode('utf-8')
            contents_object = BaseProgram.repository.file_contents("./Data/streams.json")
            contents_object.update("update", git_streams)
            self.file_save("streams")


        return

    def git_read(self, mode:str):
        """ Description: Reads data from github .json files
            Arguments:
                [mode] - checks to do. accepts: database, guides, settings, classes
                         or any of the their combination delimited by "-"
                    - 'database'> BaseProgram.data
                    - 'guides'> BaseProgram.guides
                    - 'settings'> BaseProgram.settings
                    - 'classes'> BaseProgram.classes
        """
        mode = mode.split("-")
        if mode == ["all"]:
            mode = ["database", "guides", "classes", "settings", "streams"]

        if "database" in mode:
            git_data = BaseProgram.repository.file_contents("./Data/database.json").decoded
            BaseProgram.data = json.loads(git_data.decode('utf-8'))

        if "guides" in mode:
            git_guides = BaseProgram.repository.file_contents("./Data/guides.json").decoded
            BaseProgram.guides = json.loads(git_guides.decode('utf-8'))

        if "classes" in mode:
            git_classes = BaseProgram.repository.file_contents("./Data/classes.json").decoded
            BaseProgram.classes = json.loads(git_classes.decode('utf-8'))
            self.sort_classes_acronym()

        if "settings" in mode:
            git_settings = BaseProgram.repository.file_contents("./Data/settings.json").decoded
            BaseProgram.settings = json.loads(git_settings.decode('utf-8'))

            self.sort_privileged_roles()
            self.sort_author_list_lowercase()

        if "texts" in mode:
            git_texts = BaseProgram.repository.file_contents("./Data/texts.json").decoded
            BaseProgram.texts = json.loads(git_texts.decode('utf-8'))

        if "streams" in mode:
            git_streams = BaseProgram.repository.file_contents("./Data/streams.json").decoded
            BaseProgram.streams = json.loads(git_streams.decode('utf-8'))


        # Saving
        self.file_save("all")
        return

    def sort_classes_acronym(self):
        """ Description: sort classes acronyms into one dictionary
                and assigns each acronym as a key and their class name as value.
                Method created for much more efficient class acronym search.
        """

        for class_name in BaseProgram.classes:
            if "acronym" in BaseProgram.classes[class_name]:
                list_of_acronyms = BaseProgram.classes[class_name]["acronym"].split(",")
                acronyms = [acr.replace(" ", "").lower() for acr in list_of_acronyms if acr != "(None)"]
                if acronyms != ['']:
                    for acr in acronyms:
                        BaseProgram.class_acronyms[acr] = class_name
        return

    def sort_author_list_lowercase(self):
        """ Description: sort author aliases into one dictionary
                and assigns each alias as a key and their author name as value.
                Method created for much more efficient class author alias search.
        """
        BaseProgram.author_list_lowercase = []
        for author in BaseProgram.settings["confirmed_authors"]:
            BaseProgram.author_list_lowercase.append(author.lower())
            for alias in BaseProgram.settings["confirmed_authors"][author]["alias"]:
                BaseProgram.author_list_lowercase.append(alias.lower())
        return

    def sort_privileged_roles(self):
        """ Description: Creates a list of privileged roles from BaseProgram.settings
        """
        BaseProgram.priveleged_roles = []
        for role in BaseProgram.settings["EvaluatorSettings"]["role_privilege"]:
            if BaseProgram.settings["EvaluatorSettings"]["role_privilege"][role] == 1:
                BaseProgram.priveleged_roles.append(role)
        return


    """ SEARCH METHODS SECTION """
    def find_bot_by_name(self, bot_name_value:str):
        """Description: Finds boats by name
           Arguments:
               [bot_name_value] - search word
        """
        if bot_name_value in BaseProgram.data["sort_by_bot_name"]:
            link = BaseProgram.data["sort_by_bot_name"][bot_name_value]["url"]
            author = BaseProgram.data["sort_by_bot_name"][bot_name_value]["author"]
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
        if author in BaseProgram.data["sort_by_bot_authors"]:
            list_of_bots = []
            for bot in BaseProgram.data["sort_by_bot_authors"][author]:
                link = BaseProgram.data["sort_by_bot_authors"][author][bot]["url"]
                list_of_bots.append([bot, author, link])
            return (True, list_of_bots)
        else:
            list_of_possible_authors = []
            for verified_author in BaseProgram.settings["confirmed_authors"]:
                alias = [alias.lower() for alias in BaseProgram.settings["confirmed_authors"][verified_author]["alias"]]
                for author_nickname in alias:
                    if author in author_nickname:
                        list_of_possible_authors.append(alias[0])
                        break
            return (False, list_of_possible_authors)

    def bot_searching_algorithm(self, bot_name_value):
        list_of_possible_bots = {}
        done_searching = []
        for author in BaseProgram.data["sort_by_bot_authors"]:
            for bot in BaseProgram.data["sort_by_bot_authors"][author]:
                search_name = bot_name_value.lower()
                bot_by_author = bot.lower()

                if search_name == bot_by_author:
                    link = BaseProgram.data["sort_by_bot_authors"][author][bot]["url"]
                    return {author:[(bot_name_value, link)]}

                if (search_name in bot_by_author) and ((bot_by_author, author) not in done_searching):
                    done_searching.append((bot_by_author, author))
                    link = BaseProgram.data["sort_by_bot_authors"][author][bot]["url"]
                    if author not in list_of_possible_bots:
                        list_of_possible_bots[author] = []
                    list_of_possible_bots[author].append([bot, link])
        return list_of_possible_bots

    def find_author_aliases(self, author):
        return [alias.lower() for alias in BaseProgram.settings["confirmed_authors"][author]["alias"]]


    def find_author_id(self, bot_author):
        test_id = re.sub("<|>|!|@","", bot_author)
        for author in BaseProgram.settings["confirmed_authors"]:
            if test_id == BaseProgram.settings["confirmed_authors"][author]["id"]:
                return author.lower()
        return None

    def find_class(self, class_name):
        possible_classes = []

        if len(class_name) <= 4:
            if class_name.lower() in BaseProgram.class_acronyms:
                class_name_ = BaseProgram.class_acronyms[class_name.lower()]
                return [
                    ("Authentic", ""), (class_name_, BaseProgram.classes[class_name_]["discord_url"], BaseProgram.classes[class_name_]["wiki"])
                    ]


        for class_name_ in BaseProgram.classes:
            # Search if exact name
            if class_name == class_name_.lower():
                if "discord_url" in BaseProgram.classes[class_name_]:
                    return [
                        ("Authentic", ""), (class_name_, BaseProgram.classes[class_name_]["discord_url"], BaseProgram.classes[class_name_]["wiki"])
                        ]
                else:
                    return [("Basic", ""), (class_name, BaseProgram.classes[class_name_])]

            duplicates = [dn.lower() for dn in BaseProgram.classes[class_name_]["duplicates"]]

            # Search duplicate classes
            if class_name in duplicates:
                ind = duplicates.index(class_name)
                if "discord_url" in BaseProgram.classes[class_name_]:
                    return [
                        ("Duplicate", BaseProgram.classes[class_name_]["duplicates"][ind]) ,
                        (class_name_, BaseProgram.classes[class_name_]["discord_url"], BaseProgram.classes[class_name_]["wiki"])
                        ]
                else:
                    return [("Basic", ""), (BaseProgram.classes[class_name_]["duplicates"][ind], BaseProgram.classes[class_name_])]

        if class_name.lower() in BaseProgram.class_acronyms:
            class_name_ = BaseProgram.class_acronyms[class_name.lower()]
            return [
                ("Authentic", ""), (class_name_, BaseProgram.classes[class_name_]["discord_url"], BaseProgram.classes[class_name_]["wiki"])
                ]

        for class_name_ in BaseProgram.classes:
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
                        possible_classes.append(BaseProgram.classes[class_name_]["duplicates"][ind])
        if possible_classes:
            return [(False, ""), (possible_classes)]
        else:
            return [(False, ""), ([])]


class BaseTools(BaseProgram):
    description = "Sets of tool functions to be used by other Cogs"

    def setup(self):
        self.block_color = 3066993 
        

    async def check_word_count(self, ctx, value:str, icon=""):
        """ Description: Checks word is allowed for searching
            Arguments:
                [ctx] - context
                [value] - word to be evaluated
            Return: Bool.
        """
        if value == "":
            await ctx.send(embed=self.embed_single("Warning", "Please input a value to search.", icon)) 
            return False

        test = value.split(" ")
        for word in test:
            for banned_words in BaseProgram.settings["banned_words"]:
                if banned_words in word.lower():
                    await ctx.send(embed=self.embed_single("Warning", f"The term `{banned_words}` is nerfed.\nIt does not give productive results.", icon)) 
                    return False

        word_value = value.split(" ")
        for word in word_value:
            if word.isdigit() and len(word) != 1:
                return True
            if word.isdigit() and len(word) == 1:
                desc = "Your search entries must have `at least 3 letters`. \n"\
                       "Or it must be a number of `length greater than 1`."
                await ctx.send(embed=self.embed_single("Warning", desc, icon)) 
                return False
        for word in word_value:
            if len(word) < 3:
                desc = "Your search entries must have `at least 3 letters`. \n"\
                       "Or it must be a number of `length greater than 1`."
                await ctx.send(embed=self.embed_single("Warning", desc, icon)) 
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
                    - 'update'> checks if BaseProgram.database_updating is set to True.
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
            if BaseProgram.database_updating:
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
        if int(guild_id) in BaseProgram.settings["EvaluatorSettings"]["guild_privilege"]:
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
                if role in BaseProgram.priveleged_roles:
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
        if str(ctx.author.id) not in BaseProgram.PERMISSIONS:
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
        if guild_id in BaseProgram.settings["server_settings"]:
            if BaseProgram.settings["server_settings"][guild_id]["server_privilage"] == "Homie":
                return True
        if guild_id not in BaseProgram.settings["server_settings"]:
            return False



    async def embed_multiple_links(self, ctx, bot_name: str, bot_results: str, icon=""):
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

        

        if icon:
            embedVar = discord.Embed(description=desc, color=self.block_color)
            embedVar.set_author(name=title, icon_url=icon)
        else:
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
                    bot_list += '➣ [{}]({})\n'.format(items[0], items[1])
                embedVar.add_field(name=author.capitalize(), value=bot_list, inline=inline)
        await ctx.send(embed=embedVar)
        return

    # Tools
    def embed_multi_link(self, title, block_title, embed_description, list_var, icon=""):
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

        if icon:
            embedVar = discord.Embed(description=embed_description, color=self.block_color)
            embedVar.set_author(name=title, icon_url=icon)
        else:
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
            print()
            if title == "Bot Author":
                bot_list += '➣ [{}]({})\n'.format(items[0], items[2])
            else:
                bot_list += '➣ [{}]({})\n'.format(items[0], items[1])
        if counts["field"] == 2:
            embedVar.add_field(name=st, value=st, inline=inline)
        if counts["field"] == 1:
            embedVar.add_field(name=st, value=st, inline=inline)
            embedVar.add_field(name=st, value=st, inline=inline)
        embedVar.add_field(name=block_title, value=bot_list, inline=inline)

        return embedVar

    def embed_multi_text(self, title, field_name:str, description:str,
            value_list, block_count:int, two_collumn:bool, icon=""):
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

        if icon:
            embedVar = discord.Embed(description=description, color=self.block_color)
            embedVar.set_author(name=title, icon_url=BaseProgram.icon_auqw)
        else:
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

    def embed_single(self, title, description, icon=""):
        """ Description: Single item embed
            Arguments:
                [title] - title
                [description] - embed description
            Return: Discord embed object
        """
        if icon:
            embedVar = discord.Embed(description=description, color=self.block_color)
            embedVar.set_author(name=title, icon_url=icon)
            return embedVar
        else:
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


    def try_till_succeed(self, function, name):
        while True:
            try:
                x = function()
                print(f"> Function {name} executed...Success!")
                return x
            except:
                print(f"> Failed Executing {name}... Trying again.")
                print("> Reloading...")
                continue

    def get_url_item(self, url):
        while True:
            try:
                content = BaseProgram.loop.run_until_complete(self.get_site_content(url))
                print(f"> Function get executed...Success!")
                return content
            except:
                print(f"> Failed Executing get... Trying again.")
                print("> Reloading...")
                continue
        
    def get_url_item_2(self, url):
        while True:
            try:
                content = BaseProgram.loop.run_until_complete(self.get_site_content_2(url))
                print(f"> Function get executed...Success!")
                return content
            except:
                print(f"> Failed Executing get... Trying again.")
                print("> Reloading...")
                continue

    # async def get_site_content(self, SELECTED_URL):
    #     async with aiohttp.ClientSession(trust_env=True) as session:
    #         async with session.get(SELECTED_URL) as response:
    #             text_ = await response.read()
    #             return Soup(text_.decode('utf-8'), 'html5lib')

    async def get_site_content(self, SELECTED_URL, header=""):
        client = aiosonic.HTTPClient()
        if header:
            response = await client.get(SELECTED_URL, headers=header)
        else:
            response = await client.get(SELECTED_URL)
        text_ = await response.content()
        return Soup(text_.decode('utf-8'), 'html5lib')

    async def get_site_content_2(self, SELECTED_URL, header=""):
        client = aiosonic.HTTPClient()
        if header:
            response = await client.get(SELECTED_URL, headers=header)
        else:
            response = await client.get(SELECTED_URL)
        text_ = await response.content()
        return Soup(text_.decode('utf-8'), 'html.parser')

    async def get_site_txt(self, SELECTED_URL):
        client = aiosonic.HTTPClient()
        response = await client.get(SELECTED_URL)
        text_ = await response.content()
        return text_

    async def get_site(self, SELECTED_URL, headers=""):
        client = aiosonic.HTTPClient()
        response = await client.get(SELECTED_URL, headers=headers)
        text_ = await response.content()
        return text_
    # async def get_site_txt(self, SELECTED_URL):
    #     async with aiohttp.ClientSession(trust_env=True) as session:
    #         async with session.get(SELECTED_URL) as response:
    #             text_ = await response.read()
    #             return text_

    # async def get_site(self, SELECTED_URL, headers=""):
    #     async with aiohttp.ClientSession(trust_env=True, headers=headers) as session:
    #         async with session.get(SELECTED_URL) as response:
    #             x = await response.read()
    #             return x
                 
        # async with aiohttp.ClientSession(trust_env=True) as session:
        #     async with session.get(SELECTED_URL) as response:
        #         text_ = await response.read()
        #         return Soup(text_.decode('utf-8'), 'html5lib')

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

        embedVar = discord.Embed(title="Bloom Help", color=self.block_color)
        desc = "`;bhelp` ➣ Shows all Bloom commands.\n"\
               "`;g` ➣ Summons a list of all guides commands.\n"\
               "`;g guide_name` ➣ Returns a specific guide.\n"\
               "`;c class_name` ➣ Shows Class data chart. Can use acronyms.\n"\
               "`;legends` ➣ Shows the legends for the class data charts.\n"\
               "`;char character_name` ➣ Shows player info from the Char page. \n"\
               "`;ioda character_name` ➣ IoDA date calculations.\n"\
               "`;w search` ➣ Search AQW Wikidot.\n"\
               "`;ws search` ➣ Gets list of AQW Wikidot searches.\n"\
               "`;go search` ➣ Search with google chrome.\n"\
               "`;server` ➣ Shows player count of Aqw servers.\n"\
               "`;credits` ➣ Reveals the credits.\n"
        embedVar.description = desc
        if guild_allowed:
            embedVar.add_field(name="Shadow Commands", inline=False, 
                value="`;b bot_name` ➣ Search a boat.\n"\
                      "`;a author` ➣ Search a boat author.\n"\
                      "`;a` ➣ Returns list of boat authors.\n"\
                      "`;a u` ➣ Returns list of boats with no authors.\n"\
                      "`;bverify u` ➣ Verifies an author name. Case sensitive.\n"\
                      "`;buverify u` ➣ Unverifies an author name. \n"\
                      "`;update database` ➣ Updates boat database.\n"\

                )
        embedVar.add_field(name="Privileged Commands", inline=False, 
            value="`;update all` ➣ Updates all .jsons.\n"\
                  "`;update settings` ➣ Updates the settings.\n"\
                  "`;update guides` ➣ Update the guides.\n"\
                  "`;update classes` ➣ Update the classes. Not the charts.\n"\
                  )

        embedVar.set_author(name="An AdventureQuest World General Discord Bot", icon_url=BaseProgram.icon_aqw)
        embedVar.set_thumbnail(url=BaseProgram.icon_bloom)
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
                    - 'database'> BaseProgram.data
                    - 'guides'> BaseProgram.guides
                    - 'settings'> BaseProgram.settings
                    - 'classes'> BaseProgram.classes
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
            BaseProgram.database_updating = True
            await ctx.send(r"\> Updating Bloom Bot")
            if value == "web" or value == "":
                result = self.database_update("web")
            elif value == "html":
                result = self.database_update("html")
            if result:
                await ctx.send(r"\> Bloom Bot updated!")
                await ctx.send(f"\> Update method: `{BaseProgram.mode}`")
            else:
                if BaseProgram.settings["latest_update"] == "web":
                    await ctx.send("\> Nope. Latest method is web. Not gonna use locally saved .html\n"\
                                  "`Error 14: Already up to date`")
                else:
                    await ctx.send("\> Something's wrong. Ping the Autistic Chungus.\n"\
                                  "`Error 69: Web method.`")
            BaseProgram.database_updating = False
            return

        if mode == "settings":
            BaseProgram.database_updating = True
            await ctx.send(r"\>Updating `setting.json`")
            self.git_read("settings-update")
            await ctx.send(r"\>Bloom Bot `setting.json` updated!")
            BaseProgram.database_updating = False
            return

        if mode == "classes":
            BaseProgram.database_updating = True
            await ctx.send(r"\>Updating `classes.json`")
            self.git_read("classes-update")
            await ctx.send(r"\>Bloom Bot `classes.json` updated!")
            BaseProgram.database_updating = False
            return

        if mode == "guides":
            BaseProgram.database_updating = True
            await ctx.send(r"\>Updating `guides.json`")
            self.git_read("guides-update")
            await ctx.send(r"\>Bloom Bot `guides.json` updated!")
            BaseProgram.database_updating = False
            return

        if mode == "texts":
            BaseProgram.database_updating = True
            await ctx.send(r"\>Updating `texts.json`")
            self.git_read("texts-update")
            await ctx.send(r"\>Bloom Bot `texts.json` updated!")
            BaseProgram.database_updating = False
            return

        if mode == "streams":
            BaseProgram.database_updating = True
            await ctx.send(r"\>Updating `streams.jsons`")
            self.git_read("streams-update")
            await ctx.send(r"\>Bloom Bot `streams.jsons` updated!")
            BaseProgram.database_updating = False
            return

        if mode == "all":
            BaseProgram.database_updating = True
            await ctx.send(r"\>Updating `all .jsons`")
            self.git_read("all-update")
            await ctx.send(r"\>Bloom Bot `all .jsons` updated!")
            BaseProgram.database_updating = False
            return