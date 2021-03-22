
import tweepy
import re
from .Base import *
from discord.ext import commands
import asyncio
from threading import Thread
from pprint import pprint
from discord.utils import get
from datetime import datetime, timedelta

class TweetTools(BaseTools):
    

    def tweet_tools(self):

        self.gift_checks = [
            "BONUS daily login gift",
            "New daily login gift",
            "daily login",
            "holi-daily",
            "login gift",
            "BONUS daily",
            "New daily drops",
            "daily gift",
            "daily gifts",
            "hour DOUBLE",
            "hour Drop",
            "DOUBLE Reputation"
        ]

        self.double_check = [
        "hour DOUBLE",
        "hour Drop",
        "DOUBLE Reputation",
        "DOUBLE Gold",
        "boost on all",
        "boost on all servers",
        "all servers",
        "for 48 hours",
        "for 72 hours",
        "Double Exp",
        "Double Void",
        "Double Class point",
        "Double Experience",
        ]
        self.black_list = [
            "Design Notes", "RT @"
            ]
        self.is_double = False

    def save_log(self, m, text, link, is_success=False):
        """
            1 = enemy
            2 = location
            3 = item
            4 = quest
            5 = hour
            6 = boost
        """


        if m == 1:
            error_name = "enemy"
        if m == 2:
            error_name = "location"
        if m == 3:
            error_name = "item"
        if m == 4:
            error_name = "quest"
        if m == 5:
            error_name = "hour"
        if m == 6:
            error_name = "boost"

        if is_success:
            item = f"[None at {error_name}] \nTweet: {text} Link: {link}"
        else:
            item = f"[Error at {error_name}] \nTweet: {text} Link: {link}"
        print(item)
        self.settings["TwitterListenerCogSettings"]["Logs"].append(item)
        self.file_save("settings")
        self.git_save("settings")

    def word_cleaner(self, word):
        return word.strip().capitalize()

    async def check_website_integrity(self, item):

        x = re.sub("[']", "-", item).replace(" ", "-")
        x = re.sub("[^A-Za-z0-9\-]+", "", x)
        straight = "http://aqwwiki.wikidot.com/" + x.lower()
        
        # wiki = "http://aqwwiki.wikidot.com/search:site/q/" + x.replace("-", "%20")
        wiki = self.convert_aqurl(item, "wikisearch")

        sites_soup = await self.get_site_content(straight)
        try:
            page_content = sites_soup.find("div", {"id":"page-content"})
            page_check = page_content.find("p").text.strip()
            if page_check == "This page doesn't exist yet!":
                result = wiki
            elif "usually refers to:" in page_check:
                result = straight
            else:
                result = straight
        except:
            result = wiki

        return result

    async def tweet_send(self, text, link, id_, time, double, send_ping="not_automatic"):
        tweet_link = "https://twitter.com/twitter/statuses/"+str(id_)

        if double:
            self.is_double = True

        text = text.replace("Log in", "")
        text = re.sub('(https://|http://)(.+?)(\s)', "", text).replace("\n", "")
        location = None
        quest = None
        item = None
        enemy = None
        hour = None
        hour = None
        npc = None

        if self.is_double:
            time_ = time.strftime("%d %B %Y")

            hour = re.search("(\d\d)", text)
            if hour:
                hour = hour.groups()[0]
            else:
                self.save_log(5, text, link)
                return 
            boost = re.search("(Happening now\:|DOUBLE|hour)(.+?)(on all servers|through|\!|\.)", text)
            if boost:
                boost = boost.groups()[1].strip().capitalize()
            else:
                self.save_log(6, text, link)

            hour = self.word_cleaner(hour)
            boost = self.word_cleaner(boost)

            end_date = time + timedelta(hours=int(hour))
            end_date = end_date.strftime('%d %B %Y')

            embedVar = discord.Embed(title="New Server Boost!", url=tweet_link, color=BaseProgram.block_color)
            embedVar.description = f"**Duration**: {hour} Hours\n"\
                                   f"**Boost**: {boost.title()}\n"\
                                   f"**Posted**: {time_}\n"\
                                   f"**Ends in**: {end_date}"
            embedVar.set_image(url=link)
            embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
            embedVar.set_footer(text="Check this chat's pinned message to get daily gift notifications.")
            
            if os.name == "nt":
                channel = await self.bot.fetch_channel(799238286539227136)
                if BaseProgram.tweet_call == "stuff":
                    await channel.send("<@&814054683651342366>")
            else:
                channel = await self.bot.fetch_channel(812318143322128384)
                if BaseProgram.tweet_call == "stuff":
                    await channel.send("<@&811305081063604290>")

            await channel.send(embed=embedVar)
            print("Done")
            self.is_double = False
            return
            

        if not self.is_double:
            time = time.strftime("%d %B %Y")
            lowered_text = text.lower()
            # Location
            if "battleontown" in lowered_text:
                location = "Battleontown"
            
            if not location:
                location = re.search("\s/(.+?)(\s)|map", text)
                if location:
                    location = "/%s"%(location[1])
                else:
                    location = re.search("(boss battle in the|\sin your\s|in\s|available now in the|battle in the\s|\sin the|Complete)(.+?)(to collect|to find|\.|\s\(|\!|for a chance|to get the|\smap|quest)", text)
                    if location:
                        location = location.groups()[1]
                    else:
                        self.save_log(2, text, link)
                        return 

            if "talk to" in lowered_text:
                npc  = re.search("(Talk to|talk to)(.+?)(\sin\s|\, in)", text).groups()[1]


            # Quest/Enemy
            if re.search("(\squest\s|quest\!)", lowered_text):
                quest = re.search("(Complete the|Complete|dropping from his)(.+?)(quest|quest\!)", text)
                if quest:
                    quest = quest.groups()[1]
                else:
                    self.save_log(4, text, link)
                    return 
            else:
                text = text.replace("Battleontown", "").replace("battleontown", "")
                if "Defeat the" in text:
                    enemy = re.search("(Defeat the)(.+?)(for reward gear|in the)", text)
                else:
                    enemy = re.search("(battle the|battle|Battle\sthe|Battle|Battle the|Defeat)(.+?)(for reward gear|in the\s/|in\s/|the\s|/|\sin\s)", text)
                if enemy:
                    enemy = enemy.groups()[1]
                    enemy_link = self.convert_aqurl(enemy, "wiki")
                    # enemy_link = await self.check_website_integrity(enemy)
                else:
                    self.save_log(1, text, link)
                    enemy = "<none>"
                    enemy_link = ""

            # Items
            item = re.search("(to find our|to find the|Find the|to find|for a chance to get the|for a chance to get our|for a chance to get|0 AC|this seasonal|to get the)(.+?)((!)|(\.)|(dropping from his|as we celebrate|as we head into|in the|in her|in his shop|in her shop|as we lead up|until))", text)
            if item:
                item = item.groups()[1]
                item = re.sub(r'((?<=^\s\b)this seasonal(?=\b\s))|(((?<=^\s\b)rare(?=\b\s)))','', item).strip()
            else:
                item = re.search("(pieces of the |to collect all |Find the full|\sfor\s|one of the new|to find)(.+?)(\.|\!|available|\,|in his shop)", text)
                if item:
                    item = item.groups()[1]
                else:
                    self.save_log(3, text, link)
                    return

            # Word processing
            item = self.word_cleaner(item)
            location = self.word_cleaner(location)
            if quest:
                quest = self.word_cleaner(quest)
                target = f"**Quest**: {quest.title()}\n" 
            else:
                enemy = self.word_cleaner(enemy)
                target = f"**Enemy**: [{enemy.title()}]({enemy_link})\n" 
            if npc:
                npc = self.word_cleaner(npc)

            # Adding /join to location
            location = location.replace("/", "").title()
            if "shop" not in location.lower():
                location = "/join " + location.lower()

            item = item.title()
            # Adding 0 AC to item
            if "0 ac" not in item.lower():
                item = "0 AC " + item
            else:
                item = item.replace("0 ac", "0 AC").replace("0 Ac", "0 AC").replace("0 aC", "0 AC")


            if npc:
                location += f" ({npc.title()})"

            embedVar = discord.Embed(title="New Daily Gift!", url=tweet_link, color=BaseProgram.block_color)
            embedVar.description = f"**Location**: {location}\n"\
                                   f"{target}"\
                                   f"**Item**: {item}\n"\
                                   f"**Posted**: {time}"

            embedVar.set_image(url=link)
            embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
            embedVar.set_footer(text="Check this chat's pinned message to get daily gift notifications.")
            
            if os.name == "nt":
                channel = await self.bot.fetch_channel(799238286539227136)
                if send_ping == "automatic":
                    await channel.send("<@&814054683651342366>")
                    print("happened!?!")
            else:
                channel = await self.bot.fetch_channel(812318143322128384)
                if send_ping == "automatic":
                    await channel.send("<@&811305081063604290>")
                    
            await channel.send(embed=embedVar)
            BaseProgram.tweet_call = ""
            print("Done")
            return


    # async def tweet_send(self, text, link, id_, time):
    #     tweet_link = "https://twitter.com/twitter/statuses/"+str(id_)

    #     # Enemy
    #     enemy = re.search("(battle the|battle|Battle\sthe|Battle)(.*)(in the|in|the)\s/", text)
    #     if enemy != None:
    #         enemy = enemy.groups()[1].strip()
    #         enemy_link = await self.check_website_integrity(enemy)
    #     else:
    #         self.save_log(1, text, link)
    #         return 

    #     # Location
    #     location = re.search("\s/(.+?)(map|\s)", text)
    #     if location !=  None:
    #         location = "/join %s"%(location[1])
    #     else:
    #         self.save_log(2, text, link)
    #         return 
    #     print("Or fucking here?")
    #     # Items
    #     item = re.search("(for a chance to get the|for a chance to get our|for a chance to get|0 AC|this seasonal)(.+?)((!)|(\.)|(as we celebrate))", text)
    #     if item !=  None:
    #         item = item.groups()[1]
    #     else:
    #         self.save_log(3, text, link)
    #         return 

    #     item = re.sub(r'((?<=^\s\b)this seasonal(?=\b\s))|(((?<=^\s\b)rare(?=\b\s)))','', item).strip()
    #     if "0 AC" not in item:
    #         item = "0 AC " + item


    #     embedVar = discord.Embed(title="New Daily Gift!", url=tweet_link, color=BaseProgram.block_color)
    #     embedVar.description = f"**Location**: {location}\n"\
    #                            f"**Enemy**: [{enemy}]({enemy_link})\n"\
    #                            f"**Item**: {item}\n"\
    #                            f"**Posted**: {time}"
    #     embedVar.set_image(url=link)
    #     embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
    #     embedVar.set_footer(text="Check this chat's pinned message to get daily gift notifications.")
        
    #     if os.name == "nt":
    #         channel = await self.bot.fetch_channel(799238286539227136)
    #         if BaseProgram.tweet_call == "updaily":
    #             await channel.send("<@&814054683651342366>")
    #     else:
    #         channel = await self.bot.fetch_channel(812318143322128384)
    #         if BaseProgram.tweet_call == "updaily":
    #             await channel.send("<@&811305081063604290>")

    #     await channel.send(embed=embedVar)
    #     print("Done")
    #     return

    async def tweet_simple(self, link):
        link = str(link)
        if os.name == "nt":
            channel = await self.bot.fetch_channel(799238286539227136)
        else:
            channel = await self.bot.fetch_channel(811309992727937034)

        await channel.send(f"@Alina_AE: https://twitter.com/twitter/statuses/{link}")
        return

class TwitterCog(commands.Cog, TweetTools):

    def __init__(self, bot, api):
        self.setup()
        self.tweet_tools()
        self.bot = bot
        self.api = api
        # self.auth = tweepy.OAuthHandler(BaseProgram.CONSUMER_KEY, BaseProgram.CONSUMER_SECRET)
        # self.auth.set_access_token(BaseProgram.ACCESS_TOKEN, BaseProgram.ACCESS_TOKEN_SECRET)

        # self.api = tweepy.API(self.auth)

        # self.tweets_listener = TwitterListener(bot, self.api)
        # self.stream = tweepy.Stream(self.auth, self.tweets_listener, tweet_mode='extended', is_async=True)
        # print("> Twitter Listener Success")
        # self.stream.filter(follow=["1349290524901998592"], is_async=True)

    # Bloom Autist ID: 1349290524901998592
    # Alina ID: 16480141
    # Use this to get IDS: https://tweeterid.com/


    @commands.command()
    async def updaily(self, ctx):
        allow_ = await self.allow_evaluator(ctx, mode="role_privilege", command_name="updaily")
        if not allow_:
            return

        BaseProgram.tweet_call == "updaily"

        # this code block is another way of doing the thing below

        # user = self.api.get_user("Alina_AE")

        got = False
        time_line = tweepy.Cursor(self.api.user_timeline, screen_name="Alina_AE", count=100, tweet_mode='extended').items()
        tweet_list = []
        print("appending")
        for tweet in (time_line):
            tweet_text = tweet.full_text.lower()
            # print("did")
            self.is_double = False
            got = False
            tweet_line = tweet.full_text

            # Checks if wrong tweet
            for i in self.black_list:
                if i.lower() in tweet_text:
                    continue

            # Checks if double boost
            for i in  self.double_check:
                if i.lower() in tweet_text:
                    self.is_double = True
                    got = True
                    break

            if not self.is_double:
                # Check if Daily Gift
                for i in self.gift_checks:
                    if i.lower() in tweet_text:
                        got = True
                        for i in self.gift_checks:
                            tweet_line = tweet.full_text.replace(i, "")
                        break

            if not got:
                continue

            if "media" in tweet.entities:
                med = tweet.entities['media']
                for i in med:
                    if "media_url" in i:
                        # time_ = tweet.created_at.strftime("%d %B %Y")
                        tweet_list.append({
                            "tweet": tweet_line,
                            "image_url": i["media_url"],
                            "id": tweet.id,
                            "time": tweet.created_at,
                            "double": self.is_double
                            })
                        print("done tweet")
                        got = False
                        self.is_double = False
                        break
        print("starting")
        reversed_list = reversed(tweet_list)
        for tweet in reversed_list:
            await self.tweet_send(tweet["tweet"], tweet["image_url"], tweet["id"], tweet["time"], double=tweet['double'])

    @commands.command()
    async def uponce(self, ctx):
        allow_ = await self.allow_evaluator(ctx, mode="role_privilege", command_name="updaily")
        if not allow_:
            return

        BaseProgram.tweet_call == "uponce"

        # this code block is another way of doing the thing below

        user = self.api.get_user("Alina_AE")

        got = False
        time_line = tweepy.Cursor(self.api.user_timeline, screen_name="Alina_AE", count=10, tweet_mode='extended').items(40)

        tweet_list = []
        count = 0

        for tweet in time_line:
            print("new")
            tweet_text = tweet.full_text.lower()
            for i in self.key_check:
                if i in tweet_text:
                    got = True
                    break
            if not got:
                continue
            if "media" not in tweet.entities:
                continue

            med = tweet.entities['media']
            for i in med:
                if "media_url" in i:
                    time_ = tweet.created_at.strftime("%d %B %Y")
                    tweet_list.append({
                        "tweet": tweet.full_text,
                        "image_url": i["media_url"],
                        "id": tweet.id,
                        "time": time_,
                        })
                    count += 1
                    print(count)
                    got = False
                    break

        print("starting")
        tweet_ = tweet_list[-1]
        pprint(tweet_)
        await self.tweet_send(tweet_["tweet"], tweet_["image_url"], tweet_["id"], tweet_["time"])




class TwitterListener(tweepy.StreamListener, TweetTools):
    def __init__(self, bot, api,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.discord = discord # this is just a function which sends a message to a channel
        # self.loop = loop # this is the loop of discord client
        self.bot = bot
        # self.api = api
        # self.me = api.me()
        self.tweet_text = ""
        self.image_url = ""
        self.tweet_tools()
        self.setup()



    def on_status(self, status=""):

        self.is_double = False
        got = False

        if status == "":
            return
        if hasattr(status, 'extended_tweet'):
            tweet = status.extended_tweet['full_text']
            tweet_text = tweet.lower()

            # Checks if wrong tweet
            for i in self.black_list:
                if i.lower() in tweet_text:
                    self.send_to_discord(status.id, status.user.id_str)
                    return

            # Checks if double boost
            for i in  self.double_check:
                if i.lower() in tweet_text:
                    self.is_double = True
                    got = True
                    break

            if not self.is_double:
                # Check if Daily Gift
                for i in self.gift_checks:
                    if i.lower() in tweet_text:
                        got = True
                        for i in self.gift_checks:
                            tweet = tweet.replace(i, "")
                        break

            if not got:
                self.send_to_discord(status.id, status.user.id_str)
                return

            link = status.extended_tweet['entities']['media'][0]["media_url_https"]
            send_fut = asyncio.run_coroutine_threadsafe(self.tweet_send(tweet, link, status.id, status.created_at, None, send_ping="automatic"), BaseProgram.loop)
            send_fut.result()
            return
        else:
            # print(status)
            print('text: ' + status.text)
            self.send_to_discord(status.id, status.user.id_str)
            return



    def on_error(self, status):
        print(status)

    def send_to_discord(self, id_, tweet_id):
        if os.name == "nt":
            tweet_user = "1349290524901998592"
        else:
            tweet_user = "16480141"
        

        if tweet_id != tweet_user:
            return
        send_fut = asyncio.run_coroutine_threadsafe(self.tweet_simple(id_), BaseProgram.loop)
        send_fut.result()
        return