
from .Base import *
from discord.ext import commands

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
        
        self.loop = bot.loop
        self.bot = bot

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

        print("yes")
        BaseProgram.reddit_network = {
            "4chan":{
                "key": 822037903790047233,
                "obj": "",
            },
            "maids": {
                "key": 824636610481881157,
                "obj": "",
            }
        }
        print("nope")
        self.reddit = asyncpraw.Reddit(client_id = client_id,  
                             client_secret = client_secret,  
                             username = username,  
                             password = password, 
                             user_agent = user_agent) 
        # send_fut = asyncio.run_coroutine_threadsafe(self.get_channel(), BaseProgram.loop)
        # send_fut.result()

        self.loop.create_task(self.listener())

    async def listener(self):
        await self.bot.wait_until_ready()
        if os.name == "nt":
            self.channel = await self.bot.fetch_channel(799238286539227136)
        else:
            self.channel = await self.bot.fetch_channel(811305082758758434)

            for subred in BaseProgram.reddit_network:
                print(BaseProgram.reddit_network[subred]["key"])
                try:
                    BaseProgram.reddit_network[subred]["obj"] = await self.bot.fetch_channel(BaseProgram.reddit_network[subred]["key"])
                except Exception as e:
                    print(e)
        # await asyncio.sleep(10)
        print("> Start Watching")
        subreddit = await self.reddit.subreddit("AQW+FashionQuestWorlds+AutoQuestWorlds+133sAppreciationClub")
        while True:
            try:
                async for sub in subreddit.stream.submissions():
                    sub_name = str(sub.subreddit)
                    if sub_name not in BaseProgram.reddit_logs:
                        BaseProgram.reddit_logs[sub_name] = {}

                    if str(sub.id) in BaseProgram.reddit_logs[sub_name]:
                        print("NOPE")
                        continue
                    author_ = str(sub.author)
                    title_ = str(sub.title)
                    link_ = f"https://www.reddit.com{sub.permalink}"
                    image_ = None
                    footer_ = None
                    is_video_= sub.is_video

                    if not sub.is_self:  # We only want to work with link posts
                        image_ = str(sub.url)
                    print(title_)
                    try:
                        image_ = sub.media_metadata[list(sub.media_metadata)[0]]["s"]["u"]
                        footer_ = "This is a gallery post."
                    except:
                        pass
                    if sub.is_video == True:
                        image_ = sub.preview["images"][0]["source"]["url"]
                        footer_ = "This is a video post."
                    text_ = str(sub.selftext) + "\n"
                    time_ = self.get_date(sub)

                    BaseProgram.reddit_logs[sub_name][sub.id] = {
                        "author": author_,
                        "title": title_,
                        "link": link_,
                        "image": image_,
                        "text": text_,
                        "time": time_,
                        "is_video": is_video_
                    }
                    if not BaseProgram.lock_read:
                        self.git_save("reddit_logs")

                    embedVar = discord.Embed(title=title_, url=link_, color=BaseProgram.block_color)
                    embedVar.set_author(name="r/" + sub_name, url=f"https://www.reddit.com/r/{sub_name}/", icon_url=BaseProgram.icon_dict[sub_name])
                    
                    text_ = re.sub(r"[^(](https://preview.redd.it/.+?\n)", "", text_)
                    text_ = re.sub(r"(&#x200B;)", "", text_)
                    text_ = re.sub(r"(\n\n\n)", "\n", text_).strip()
                    chunks = textwrap.wrap(text_, 1024, break_long_words=False, replace_whitespace=False)
                    pprint(text_)
                    if chunks:
                        embedVar.description = chunks[0]
                    if len(chunks) > 0:
                        for chunk in chunks[1:]:
                            embedVar.add_field(name="\u200b", value=chunk, inline=False)

                    embedVar.add_field(name='Author:', value=f"[u/{author_}](https://www.reddit.com/user/{author_}/)", inline=True)
                    embedVar.add_field(name='Date Posted:', value=time_, inline=True)
                    if image_:
                        embedVar.set_image(url=image_.strip())
                    if footer_:
                        embedVar.set_footer(text=footer_)

                    if os.name == "nt":
                        await self.channel.send(embed=embedVar)
                    else:
                        if sub_name.lower() in BaseProgram.reddit_network:
                            await BaseProgram.reddit_network[sub_name.lower()]["obj"].send(embed=embedVar)
                        else:
                            await self.channel.send(embed=embedVar)
                    await asyncio.sleep(1)
            except Exception as e:
                print("Dead: ", e)
                continue
            # await self.send_webhook(sub_name, author_, title_, link_, image_, time_, text_, footer_)
            

            # print(f"Title: {sub.title}\nAuthor: u/{sub.author}\nAuthor Link: https://www.reddit.com/user/{sub.author}/\nScore: {sub.score}\nID: {sub.id}\nURL: https://www.reddit.com{sub.permalink}\nImage URL: {sub.url}\n\n")
            # print("\n"*5)
    async def send_webhook(self, sub_name_, author_, title_, link_, image_, time_, text_, footer_):
        webhook = DiscordWebhook(url=self.channel_urls)

        # create embed object for webhook
        embed = DiscordEmbed(title=title_, color=BaseProgram.block_color, url=link_)
        embed.set_author(name="r/" + sub_name_, url="https://www.reddit.com/r/AQW/", icon_url=BaseProgram.icon_dict[sub_name_])
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
        if footer_:
            embed.set_footer(text=footer_)
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