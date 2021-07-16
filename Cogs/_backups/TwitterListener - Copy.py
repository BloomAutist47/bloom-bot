
import tweepy
import re
from .Base import *
from discord.ext import commands
import asyncio
from threading import Thread
from pprint import pprint
from discord.utils import get


class TweetTools(BaseTools):
    def tweet_tools(self):
        self.key_check = [
            "BONUS daily login gift",
            "New daily login gift",
            "daily login",
            "holi-daily",
            "login gift",
            "BONUS daily",
            "daily drops",
            "daily gifts"
            ]
        self.mode = ""

    def save_log(self, m, text, link):
        if m == 1:
            item = f"[Error at enemy] \nTweet: {text} Link: {link}"
        
        if m == 2:
            item = f"[Error at location] \nTweet: {text} Link: {link}"
        
        if m == 3:
            item = f"[Error at item] \nTweet: {text} Link: {link}"
        self.settings["TwitterListenerCogSettings"]["Logs"].append(item)
        self.file_save("settings")
        self.git_save("settings")


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

    async def tweet_send(self, text, link, id_, time):
        tweet_link = "https://twitter.com/twitter/statuses/"+str(id_)

        # Enemy
        enemy = re.search("(battle the|battle|Battle\sthe|Battle)(.*)(in the|in|the)\s/", text)
        if enemy != None:
            enemy = enemy.groups()[1].strip()
            enemy_link = await self.check_website_integrity(enemy)
        else:
            self.save_log(1, text, link)
            return 

        # Location
        location = re.search("\s/(.+?)(map|\s)", text)
        if location !=  None:
            location = "/join %s"%(location[1])
        else:
            self.save_log(2, text, link)
            return 
        print("Or fucking here?")
        # Items
        item = re.search("(for a chance to get the|for a chance to get our|for a chance to get|0 AC|this seasonal)(.+?)((!)|(\.)|(as we celebrate))", text)
        if item !=  None:
            item = item.groups()[1]
        else:
            self.save_log(3, text, link)
            return 

        item = re.sub(r'((?<=^\s\b)this seasonal(?=\b\s))|(((?<=^\s\b)rare(?=\b\s)))','', item).strip()
        if "0 AC" not in item:
            item = "0 AC " + item


        embedVar = discord.Embed(title="New Daily Gift!", url=tweet_link, color=BaseProgram.block_color)
        embedVar.description = f"**Location**: {location}\n"\
                               f"**Enemy**: [{enemy}]({enemy_link})\n"\
                               f"**Item**: {item}\n"\
                               f"**Posted**: {time}"
        embedVar.set_image(url=link)
        embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
        embedVar.set_footer(text="Check this chat's pinned message to get daily gift notifications.")
        
        if os.name == "nt":
            channel = await self.bot.fetch_channel(799238286539227136)
            if self.mode == "updaily":
                await channel.send("<@&814054683651342366>")
        else:
            channel = await self.bot.fetch_channel(812318143322128384)
            if self.mode == "updaily":
                await channel.send("<@&811305081063604290>")

        await channel.send(embed=embedVar)
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
    #         if self.mode == "updaily":
    #             await channel.send("<@&814054683651342366>")
    #     else:
    #         channel = await self.bot.fetch_channel(812318143322128384)
    #         if self.mode == "updaily":
    #             await channel.send("<@&811305081063604290>")

    #     await channel.send(embed=embedVar)
    #     print("Done")
    #     return



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

        self.mode == "updaily"

        # this code block is another way of doing the thing below

        # user = self.api.get_user("Alina_AE")

        got = False
        time_line = tweepy.Cursor(self.api.user_timeline, screen_name="Alina_AE", count=100, tweet_mode='extended').items()
        tweet_list = []
        print("appending")
        for tweet in (time_line):
            # print(tweet.full_text)
            tweet_text = tweet.full_text.lower()
            for i in self.key_check:
                if i in tweet_text:
                    got = True
                    break
            if not got:
                continue

            if "media" in tweet.entities:
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
                        print("done tweet")
                        got = False
        print("starting")
        reversed_list = reversed(tweet_list)
        for tweet in reversed_list:
            await self.tweet_send(tweet["tweet"], tweet["image_url"], tweet["id"], tweet["time"])

    @commands.command()
    async def uponce(self, ctx):
        allow_ = await self.allow_evaluator(ctx, mode="role_privilege", command_name="updaily")
        if not allow_:
            return

        self.mode == "uponce"

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
                    a
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



    def on_status(self, status=""):
        if status == "":
            return
        if hasattr(status, 'extended_tweet'):
            tweet = status.extended_tweet['full_text']
            got = False
            tweet_text = tweet.lower()
            for i in self.key_check:
                if i in tweet_text:
                    got = True
                    print("GOT")
                    break

            if not got: return
            self.mode == "stuff"
            link = status.extended_tweet['entities']['media'][0]["media_url_https"]
            time_ = status.created_at.strftime("%d %B %Y")
            send_fut = asyncio.run_coroutine_threadsafe(self.tweet_send(tweet, link, status.id, time_), BaseProgram.loop)
            send_fut.result()
            return

        else:
            print('text: ' + status.text)
            return

    def on_error(self, status):
        print(status)
