import re
import copy
import asyncio
import tweepy

from .Base import *
from discord.ext import commands, tasks

from threading import Thread
from pprintpp import pprint
from discord.utils import get
from datetime import datetime, timedelta

from urllib.request import urlopen, Request, urlretrieve
from urllib.parse import urlencode
from base64 import standard_b64encode

class TwitterCog(commands.Cog, BaseTools):
    
    def __init__(self, bot, api):
        self.setup()
        self.bot = bot
        self.api = api

        self.twitter_user_list = [
            "Alina_AE",
            # "BloomAutist47",
            "Kotaro_AE",
            "notdarkon",
            "asukaae",
            "yo_lae",
            "arletteaqw",
            
            "aqwclass",
            "CaptRhubarb",
                       
            "ArtixKrieger",
            "AQW_News_Reddit",
            
            "Aelious_AE",
                        
            
             # "ae_root",
             # "Cemaros_AE",
             # "Psi_AE",
        ]

        self.gift_checks = [
            "celebrating",
            "birthday",
            "Now available",
            "BONUS gift!",
            "bonus gift",
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
            "DOUBLE Reputation",
            "BONUS gift",
            "birthday gifts",

        ]
        if BaseProgram.lock_read == True:
            self.twitter_user_list = ["BloomAutist47"]
            
        self.double_check = [
            "Double quest rewards",
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
            "Void Auras",
            "5/10/20",
            "Spirit Orbs",
            "Void Aura",
            
        ]
        self.black_list = [
            "Design Notes", "RT @"
            ]
        self.is_double = False
        self.first = False
        # self.tweet_looker.start(
        
        self.tweet_looper.start()



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

        self.settings["TwitterListenerCogSettings"]["Logs"].append(item)
        self.file_save("settings")
        self.git_save("settings")

    def word_cleaner(self, word):
        return word.strip().capitalize()

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
            time_ = time.strftime("%B %d, %Y")

            hour = re.search("(\d\d)", text)
            if hour:
                hour = hour.groups()[0]
            else:
                self.save_log(5, text, link)
                return 
            boost = re.search("(Happening now\:|DOUBLE|hour)(.+?)(on all servers|until|through|\!|\.)", text)
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

            BaseProgram.auqw["boost"] = {
                "item": boost.title(),
                "startsin": time_,
                "endsin": end_date
            }

            self.git_save("auqw")

            if os.name == "nt":
                channel = await self.bot.fetch_channel(799238286539227136)
                if send_ping == "automatic":
                    await channel.send("<@&814054683651342366>")
            else:
                channel = await self.bot.fetch_channel(812318143322128384)
                if send_ping == "automatic":
                    await channel.send("<@&811305081063604290>")
                    

            await channel.send(embed=embedVar)
            self.is_double = False
            return
            

        if not self.is_double:
            
            time = time.strftime("%B %d, %Y")
            lowered_text = text.lower()
            # Location
            if "battleontown" in lowered_text:
                location = "Battleontown"
            
            if not location:
                location = re.search("\s/(.+?)(\s|map)", text)
                if location:
                    location = "/%s"%(location[1])
                else:
                    location = re.search("(boss battle in the|\sin your\s|\sin the\s|\sin\s|available now in the|battle in the\s|\sin the|Complete)(.+?)(to collect|to find|\.|\s\(|\!|for a chance|to get the|\smap|map|quest)", text)
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
                    enemy = re.search("(Defeat the)(.+?)(for reward gear|in the|\sin\s)", text)
                else:
                    enemy = re.search("(battle the|battle|Battle\sthe|Battle|Battle the|Defeat|fight)(.+?)(for reward gear|in the\s/|in\s/|the\s|/|\sin\s)", text)
                if enemy:
                    enemy = enemy.groups()[1]
                    enemy_link = self.convert_aqurl(enemy, "wiki")
                    # enemy_link = await self.check_website_integrity(enemy)
                else:
                    self.save_log(1, "[Its got a shop]"+text, link)
                    enemy = "<none>"
                    enemy_link = ""

            # Items
            item = re.search("(to find our|to find the|Find the|to find|Find her|find her|for a chance to get the|for a chance to get our|for a chance to get|0 AC|this seasonal|to get the)(.+?)((!)|(\.)|(dropping from his|dropping in|as we celebrate|as we head into|in the|in her|in his shop|in her shop|as we lead up|until))", text)
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

            image_link = await self.get_image(link)
            
            BaseProgram.auqw["daily"] = {
                "location": location,
                "item": item,
                "date": time,
                "image": link,
                "link": tweet_link
            }
            if quest:
                BaseProgram.auqw["daily"]["quest"] = quest.title()
                BaseProgram.auqw["daily"]["enemy"] = ""
            else:
                BaseProgram.auqw["daily"]["quest"] = ""
                BaseProgram.auqw["daily"]["enemy"] = [enemy.title(), enemy_link]

            self.git_save("auqw")

            if os.name == "nt":
                channel = await self.bot.fetch_channel(799238286539227136)
                if send_ping == "automatic":
                    await channel.send("<@&814054683651342366>")
            else:
                channel = await self.bot.fetch_channel(812318143322128384)
                if send_ping == "automatic":
                    await channel.send("<@&811305081063604290>")
                    
            await channel.send(embed=embedVar)
            BaseProgram.tweet_call = ""
            return

    async def tweet_simple(self, id_, user_screen):
        link = str(id_)
        if os.name == "nt":
            channel = await self.bot.fetch_channel(799238286539227136)
        else:
            channel = await self.bot.fetch_channel(811309992727937034)

        await channel.send(f"@{user_screen}: https://twitter.com/twitter/statuses/{id_}")
        return


    # Bloom Autist ID: 1349290524901998592
    # Alina ID: 16480141
    # Use this to get IDS: https://tweeterid.com/


    @commands.command()
    async def updaily(self, ctx):
        allow_ = await self.allow_evaluator(ctx, mode="role_privilege", command_name="updaily")
        if not allow_:
            return

        BaseProgram.tweet_call == "updaily"


        got = False
        time_line = tweepy.Cursor(self.api.user_timeline, screen_name="Alina_AE", count=100, tweet_mode='extended').items()
        tweet_list = []
        print("> appending")
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

        BaseProgram.tweet_call == "updaily"

        got = False
        time_line = tweepy.Cursor(self.api.user_timeline, screen_name="Alina_AE", tweet_mode='extended').items(100)
        tweet_list = []

        for tweet in (time_line):
            print(tweet.id)
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
        print("> starting")
        if tweet_list:
            tweet = tweet_list[0]
            await self.tweet_send(tweet["tweet"], tweet["image_url"], tweet["id"], tweet["time"], double=tweet['double'], send_ping="automatic")
        else:
            print("> No Daily Gift Found")
        return


    @tasks.loop(minutes=30)
    async def tweet_looper(self):
        if not self.first:
            await asyncio.sleep(10)
            self.first = True
        await self.bot.wait_until_ready()
        BaseProgram.tweet_call == "updaily"

        for user_name in self.twitter_user_list:
            print(f"\n\n> Targeting @{user_name}")
            got = False
            tweet_list = []
            daily_list = []
            while True:
                try:
                    time_line = tweepy.Cursor(self.api.user_timeline, screen_name=user_name, tweet_mode='extended').items(30)

                    print("> Tweets appending")  
                    for tweet in time_line:
                        # check if the tweet alread exists
                        if tweet.user.id_str not in BaseProgram.twitter_logs:
                            BaseProgram.twitter_logs[tweet.user.id_str] = []
                        if tweet.id in BaseProgram.twitter_logs[tweet.user.id_str]:
                            print("> nope tweet", end=" ")
                            continue
                        else:
                            BaseProgram.twitter_logs[tweet.user.id_str].append(tweet.id)

                        if BaseProgram.lock_read == False:
                            # Checks if it isn't alina then don't do any daily gift analysis
                            if user_name != "Alina_AE" or user_name != "BloomAutist47":
                                tweet_list.append([tweet.id, tweet.user.id_str, user_name])
                                print("> simple tweet", end=" ")
                                continue
                            else:
                                print(">>>>>>>>>>> Passed")
                                pass

                        tweet_text = tweet.full_text.lower()
                        self.is_double = False
                        got = False
                        got_2 = True
                        tweet_line = tweet.full_text
                        # Checks if wrong tweet
                        for i in self.black_list:
                            if i.lower() in tweet_text:
                                tweet_list.append([tweet.id, tweet.user.id_str, user_name])
                                got_2 = False
                                print(">nottttt got")
                                break

                        if not got_2:
                            print("> Not got")
                            continue

                        # Checks if double boost
                        for i in  self.double_check:
                            if i.lower() in tweet_text:
                                self.is_double = True
                                got = True
                                print("DOUBLE YESS")
                                break
                        print(">NOT DOUBLE?!!")
                        if not self.is_double:
                            # Check if Daily Gift
                            for i in self.gift_checks:
                                if i.lower() in tweet_text:
                                    got = True
                                    for i in self.gift_checks:
                                        tweet_line = tweet.full_text.replace(i, "")
                                    break

                        if not got:
                            tweet_list.append([tweet.id, tweet.user.id_str, user_name])
                            print(" not again?@@@")
                            continue


                        if "media" in tweet.entities:
                            med = tweet.entities['media']
                            for i in med:
                                if "media_url" in i:
                                    # time_ = tweet.created_at.strftime("%d %B %Y")
                                    daily_list.append({
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
                
                    break
                except Exception as e:
                    print("\n> Failed, retry again. Error: ", e)
                    continue

            
            print("> Starting tweet sending.\n")
            if tweet_list:
                tweet_list = reversed(tweet_list)
                for tweet in tweet_list:
                    await self.tweet_simple(tweet[0], tweet[2])
                    print("> This tweet alright.", end =" ")
                    await asyncio.sleep(0.5)

            if daily_list:
                daily_list = reversed(daily_list)
                for tweet in daily_list:
                    await self.tweet_send(tweet["tweet"], tweet["image_url"], tweet["id"], tweet["time"], double=tweet['double'], send_ping="automatic")

            if user_name.lower() != "alina_ae":
                if not tweet_list:
                    print("> No Tweets")

            if not BaseProgram.lock_read:
                self.git_save("twitter_logs")

        print("> Done Tweeter hunting")
        # return

    def check_twitter_id(self, tweet_id_, user_id_):

        if user_id_ not in BaseProgram.twitter_logs:
            BaseProgram.twitter_logs[user_id_] = []

        if tweet_id_ not in BaseProgram.twitter_logs[user_id_]:
            BaseProgram.twitter_logs[user_id_].append(tweet_id_)
        
        return



    async def send_to_discord(self, id_, user_id, user_screen):
        if user_id not in BaseProgram.twitter_logs:
            BaseProgram.twitter_logs[user_id] = []

        if id_ in BaseProgram.twitter_logs[user_id]:
            print("> not this tweet" , end =" ")
            return
        else:
            BaseProgram.twitter_logs[user_id].append(id_)
        # self.check_twitter_id(id_, user_id)
        await self.tweet_simple(id_, user_screen)
        print("> This tweet alright.", end =" ")
        await asyncio.sleep(0.5)
        return



    async def get_image(self, url) -> str:

        urlretrieve(url, "daily.jpg")

        b64_image = standard_b64encode(open("./daily.jpg", "rb") .read())

        headers = {'Authorization': 'Client-ID ' + "4d8b88de7160b18"}
        data = {'image': b64_image, 'title': 'test'} 

        request = Request(url="https://api.imgur.com/3/upload.json", data=urlencode(data).encode("utf-8"),headers=headers)
        response = loads(urlopen(request).read())

        print(response)
        return response['data']['link']

"""
    @tasks.loop(seconds=60)
    async def tweet_looker(self):
        if BaseProgram.status_list == []:
            print("not this")
            return
        lenx = len(BaseProgram.status_list)

        prev_set = copy.deepcopy(BaseProgram.status_list)
        
        while True:
            for status in BaseProgram.status_list:
                await self.process_data(status[0])
                print("whut")
            if lenx != len(BaseProgram.status_list):
                print("it changed?!!")
                new_set = self.DiffList(BaseProgram.status_list, prev_set)
                BaseProgram.status_list = new_set
                continue
            else:
                BaseProgram.status_list = []
                break
        BaseProgram.status_list = []

    def DiffList(self, li1, li2):
        new_list = []
        for item in li2:
            if item not in li1:
                new_list.append(item)
        return new_list


    async def process_data(self, status=""):
        print("came")
        while True:
            if BaseProgram.twitter_updating == True:
                print(BaseProgram.twitter_updating)
                continue
            else:
                break
        if status.user.id_str not in BaseProgram.twitter_logs:
            BaseProgram.twitter_logs[status.user.id_str] = []
        if status.id in BaseProgram.twitter_logs[status.user.id_str]:
            print("> Already got this")
            return

        self.is_double = False
        got = False
        user_screen = status._json["user"]["screen_name"]
        if status == "":
            return
        if hasattr(status, 'extended_tweet'):
            tweet = status.extended_tweet['full_text']
            tweet_text = tweet.lower()

            # Checks if wrong tweet
            for i in self.black_list:
                if i.lower() in tweet_text:
                    await self.send_to_discord(status.id, status.user.id_str, user_screen)
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
                
                await self.send_to_discord(status.id, status.user.id_str, user_screen)
                return
            self.check_twitter_id(status.id, status.user.id_str)
            link = status.extended_tweet['entities']['media'][0]["media_url_https"]

            await self.tweet_send(tweet, link, status.id, status.created_at, None, send_ping="automatic")
            self.git_save("twitter_logs")
            return
        else:
            print('text: ' + status.text)
            user_screen = status._json["user"]["screen_name"]
            await self.send_to_discord(status.id, status.user.id_str, user_screen)
            self.git_save("twitter_logs")
            return




"""



# class TwitterListener(tweepy.StreamListener):
#     def __init__(self, bot, api,  *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         self.bot = bot
#         self.setup()


#     def on_status(self, status=""):
#         if status == "":
#             return
#         BaseProgram.twitter_updating = True
#         BaseProgram.status_list.append([status])
#         BaseProgram.twitter_updating = False
#         return

#     def on_error(self, status):
#         print(status)


# async def stream_tweet():
#     BaseProgram.tweets_listener = TwitterListener(Bot, BaseProgram.api)
#     BaseProgram.stream = tweepy.Stream(BaseProgram.auth, BaseProgram.tweets_listener, is_async=True,  tweet_mode='extended')
#     print("> Twitter Listener Success")

#     BaseProgram.stream.filter(follow=BaseProgram.tweet_user_list, is_async=True, stall_warnings=True)

    # Bloom Autist ID: 1349290524901998592
    # Alina ID: 16480141
    # Use this to get IDS: https://tweeterid.com/