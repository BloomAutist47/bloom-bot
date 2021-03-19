
from .Base import *
from discord.ext import commands
from threading import Thread
from pprintpp import pprint
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
import os
import textwrap
import json
import asyncpraw
import asyncio

class RedditCog(commands.Cog, BaseTools):

    def __init__(self, bot):
        self.setup()
        self.bot = bot
        self.git_read("reddit_logs")

        if os.name == "nt":
            from dotenv import load_dotenv
            load_dotenv()

            client_id = os.getenv('REDDIT_ID')
            client_secret = os.getenv('REDDIT_SECRET')
            username = os.getenv('REDDIT_USERNAME')
            password = os.getenv('REDDIT_PASSWORD')
            user_agent = os.getenv('REDDIT_USER_AGENT')
        else:              # Heroku
            client_id = os.environ.get('REDDIT_ID')
            client_secret = os.environ.get('REDDIT_SECRET')
            username = os.environ.get('REDDIT_USERNAME')
            password = os.environ.get('REDDIT_PASSWORD')
            user_agent = os.environ.get('REDDIT_USER_AGENT')

        self.channel_urls = [BaseProgram.settings["RedditCogSettings"]["channels"][channel] for channel in BaseProgram.settings["RedditCogSettings"]["channels"]]
        print(self.channel_urls)

        self.reddit = asyncpraw.Reddit(client_id = client_id,  
                             client_secret = client_secret,  
                             username = username,  
                             password = password, 
                             user_agent = user_agent) 

        
        send_fut = asyncio.run_coroutine_threadsafe(self.listener(), BaseProgram.loop)
        # send_fut.result()

    # def load_reddit_log(self):
    #     with open('./Data/reddit_logs.json', 'r', encoding='utf-8') as f:
    #         BaseProgram.reddit_logs = json.load(f)


    # def save_reddit_log(self):
    #     with open('./Data/reddit_logs.json', 'w', encoding='utf-8') as f:
    #         json.dump(BaseProgram.reddit_logs, f, ensure_ascii=False, indent=4)

    async def listener(self):
        await asyncio.sleep(20)
        print("Start Watching")
        subreddit = await self.reddit.subreddit("AQW+FashionQuestWorlds")
        async for sub in subreddit.stream.submissions():
            print("submissions")
            sub_name = str(sub.subreddit)
            if sub_name not in BaseProgram.reddit_logs:
                BaseProgram.reddit_logs[sub_name] = {}

            if str(sub.id) in BaseProgram.reddit_logs[sub_name]:
                print("Nope")
                continue

            author_ = str(sub.author)
            title_ = str(sub.title)
            link_ = f"https://www.reddit.com{sub.permalink}"
            image_ = None
            if not sub.is_self:  # We only want to work with link posts
                image_ = str(sub.url)
            print(title_)
            try:
                image_ = sub.media_metadata[list(sub.media_metadata)[0]]["s"]["u"]
            except:
                pass
            
            text_ = str(sub.selftext)
            time_ = self.get_date(sub)

            BaseProgram.reddit_logs[sub_name][sub.id] = {
                "author": author_,
                "title": title_,
                "link": link_,
                "image": image_,
                "text": text_,
                "time": time_
            }

            self.git_save("reddit_logs")


            await self.send_webhook(sub_name, author_, title_, link_, image_, time_, text_)
            await asyncio.sleep(1)

            print(f"Title: {sub.title}\nAuthor: u/{sub.author}\nAuthor Link: https://www.reddit.com/user/{sub.author}/\nScore: {sub.score}\nID: {sub.id}\nURL: https://www.reddit.com{sub.permalink}\nImage URL: {sub.url}\n\n")

    async def send_webhook(self, sub_name_, author_, title_, link_, image_, time_, text_):
        webhook = DiscordWebhook(url=self.channel_urls)

        # create embed object for webhook
        embed = DiscordEmbed(title=title_, color=BaseProgram.block_color, url=link_)
        embed.set_author(name="r/" + sub_name_, url="https://www.reddit.com/r/AQW/", icon_url=BaseProgram.icon_aqw)
        chunks = textwrap.wrap(text_, 1024, break_long_words=False)
        if chunks:
            embed.description = chunks[0]
        if len(chunks) > 0:
            for chunk in chunks[1:]:
                embed.add_embed_field(name="\u200b", value=chunk, inline=False)
        embed.add_embed_field(name='Author:', value=f"[u/{author_}](https://www.reddit.com/user/{author_}/)", inline=True)
        embed.add_embed_field(name='Date Posted:', value=time_, inline=True)
        if image_:
            embed.set_image(url=image_.strip())
        webhook.add_embed(embed)
        response = webhook.execute()

    def get_date(self, submission):
        date = datetime.fromtimestamp(submission.created).strftime('%d %B %Y | %I:%M %p %Z')
        print(date)
        return date


    @commands.command()
    async def reddithook(self, ctx, mode, *, webhook_name:str=""):
        allow_ = await self.allow_evaluator(ctx, mode="role_privilege", command_name="listlock")
        if not allow_:
            return

        mode = mode.lower()
        channel_id = f"{ctx.channel.id}"

        if mode == "set":
            if not webhook_name:
                await ctx.send("\> Please type a webhook name.")
                return
            
            if channel_id in BaseProgram.settings["RedditCogSettings"]["channels"]:
                await ctx.send(f"\> A Webhook  is **already registered** for this channel.\n\> `{webhook_name}`")
                return
            got = False
            webhook = await ctx.channel.webhooks()
            for hook in webhook:
                if webhook_name == hook.name:
                    hook_url = hook.url
                    got = True
                    break
            if not got:
                await ctx.send("\> No Webhook of that name in this channel.")
                return
            
            BaseProgram.settings["RedditCogSettings"]["channels"][channel_id] = str(hook_url)
            self.channel_urls = [BaseProgram.settings["RedditCogSettings"]["channels"][channel] for channel in BaseProgram.settings["RedditCogSettings"]["channels"]]
            self.git_save("settings")
            await ctx.send(f"\> Webhook `{webhook_name}` Successfully set for this channel.")
            return
        elif mode == "rem":
            if channel_id not in BaseProgram.settings["RedditCogSettings"]["channels"]:
                await ctx.send(f"\> This channel has no registered `;uptext` webhook")
                return

            BaseProgram.settings["RedditCogSettings"]["channels"].pop(channel_id, None)
            self.channel_urls = [BaseProgram.settings["RedditCogSettings"]["channels"][channel] for channel in BaseProgram.settings["RedditCogSettings"]["channels"]]
            self.git_save("settings")
            await ctx.send(f"\> Webhook for this Channel is Successfully unregistered ")
            return
        await ctx.send("\> Please type a `;reddithook set webhook_name` or  `;reddithook rem webhook_name`.")