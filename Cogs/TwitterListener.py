
import tweepy
import re
from .Base import *
from discord.ext import commands
import asyncio
from threading import Thread
from pprint import pprint
from discord.utils import get



class TwitterListener(tweepy.StreamListener, BaseTools, commands.Cog):
    def __init__(self, bot, api,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.discord = discord # this is just a function which sends a message to a channel
        # self.loop = loop # this is the loop of discord client
        self.bot = bot
        # self.api = api
        # self.me = api.me()
        self.tweet_text = ""
        self.image_url = ""

        self.key_check = [
            "BONUS daily login gift",
            "New daily login gift",
            "daily login",
            "holi-daily",
            "login gift",
            "BONUS daily",
            "daily drops"
            ]

    def on_status(self, status=""):
        if status == "":
            return
        if hasattr(status, 'extended_tweet'):
            tweet = status.extended_tweet['full_text']
            got = False
            for i in self.key_check:
                if i in tweet:
                    got = True
                    print("GOT")
                    break

            if not got: return

            link = status.extended_tweet['entities']['media'][0]["media_url_https"]
            send_fut = asyncio.run_coroutine_threadsafe(self.tweet_send(tweet, link, status.id), BaseProgram.loop)

            send_fut.result()
            return

        else:
            print('text: ' + status.text)
            return

    async def tweet_send(self, text, link, id_):
        tweet_link = "https://twitter.com/twitter/statuses/"+str(id_)

        # Enemy
        enemy = re.search("(battle the|battle|Battle\sthe|Battle)(.*)(in the|in)\s/", text)
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
                               f"**Item**: {item}\n"
        embedVar.set_image(url=link)
        embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
        embedVar.set_footer(text="Check this chat's pinned message to get daily gift notifications.")
        
        if os.name == "nt":
            channel = await self.bot.fetch_channel(799238286539227136)
        else:
            channel = await self.bot.fetch_channel(812318143322128384)

        await channel.send(embed=embedVar)
        searched_role = get(ctx.guild.roles, name='Daily Gifts')
        print(searched_role)
        # await channel.send("<@!>")
        return

    def on_error(self, status):
        print(status)

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
        
        wiki = "http://aqwwiki.wikidot.com/search:site/q/" + x.replace("-", "%20")

        sites_soup = self.get_url_item(straight)
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