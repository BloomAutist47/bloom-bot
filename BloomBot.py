"""
Notes:
    prefix:
        "file_fucntion": file refers to functions that deals
                         with locally saved data.
bloom tempalte: https://discord.new/D79FPrWaZh2V
Paradise template: https://discord.new/rntDVgbpUSzW

heroku config
$ heroku login
$ heroku ps:scale worker=1 -a bloom-2
# ➣➣
#EACD8A skin color

heroku logs --tail --app bloom-1
https://raw.githubusercontent.com/BloomAutist47/bloom-bot/master/Data/reddit_logs.json
"""

# Imports
import discord
import os
import tweepy

from discord.ext import tasks
from discord import Intents
from discord.ext.commands import CommandNotFound
from pprint import pprint   
from time import sleep  
from datetime import datetime
from pytz import timezone
from pypresence import Presence

from Cogs.Base import *
from Cogs.BoatSearchCog import BoatSearchCog
from Cogs.CharacterCog import CharacterCog
from Cogs.ClassSearchCog import ClassSearchCog
from Cogs.GoogleSearchCog import GoogleSearchCog
from Cogs.GuideCog import GuideCog
from Cogs.WikiCog import WikiCog
from Cogs.TwitterListener import TwitterCog
from Cogs.TextUploaderCog import TextUploaders
from Cogs.UtilsCog import UtilsCog
from Cogs.RedditCog import RedditCog
# from Cogs.SWFProcessorCog import SWFProcessorCog

# from Cogs.StreamCog import StreamCog
# from Cogs.TestCog import TestCog

class BreakProgram(Exception):
    pass

os.chdir(os.path.dirname(os.path.abspath(__file__)))


if os.name == "nt":
    load_dotenv()
    BaseProgram.tweet_user = "1349290524901998592"
    DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN2') # test bot token
    CLIEND_ID = os.getenv("DISCORD_CLIENT_ID2")
    DEPLOY_NAME = os.getenv("DEPLOY_NAME")
    cmd = "'"
else:
    BaseProgram.tweet_user = "16480141"
    DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
    CLIEND_ID = os.environ.get("DISCORD_CLIENT_ID")
    DEPLOY_NAME = os.environ.get("DEPLOY_NAME")
    cmd = ";"


intents = Intents.all()
intents.presences = True
Bot = commands.Bot(command_prefix=[cmd], description='Bloom Bot Revamped', intents=intents)
Bot.remove_command('help')

BaseStuff = BaseProgram()
BaseStuff.git_prepare()
while True:
    try:
        BaseProgram.auth = tweepy.OAuthHandler(BaseProgram.CONSUMER_KEY, BaseProgram.CONSUMER_SECRET)
        BaseProgram.auth.set_access_token(BaseProgram.ACCESS_TOKEN, BaseProgram.ACCESS_TOKEN_SECRET)

        BaseProgram.api = tweepy.API(BaseProgram.auth)
        BaseProgram.api.verify_credentials()
        print("> Twitter Succeed.")
        break
    except:
        print("> Twitter Failed... Trying again")
        continue


@Bot.event
async def on_ready():
    print('> Starting Bloom bot 2')
    if os.name == "nt":
        channel = Bot.get_channel(799238286539227136)
        await channel.send("HOLA")

    await Bot.wait_until_ready()
    deploy_notif = await Bot.fetch_channel(830702959679373352)

    manila = timezone('Asia/Manila')
    now = datetime.now(manila)
    current_time = now.strftime("%d %B %Y, %a | %I:%M:%S %p")

    await deploy_notif.send(f"**Deployed**: {DEPLOY_NAME} at {current_time}")

    # game = discord.Activity(
    #             application_id=123,
    #             assets={
    #                 "large_image": "nigmoirehd_x1024",
    #                 "large_text":"Trtyyyyy",
    #                 "small_image":"nigmoirehd_x512",
    #                 "small_text":"Asdasd"},
    #             details="Competitive",
    #             name="Initializing Bloom Bot Autism",
    #             game="AdventureQuest Worlds", 
    #             state="Playing Solo",
    #             url="https://www.youtube.com/watch?v=ivXw9VO89jw",
    #             timestamps={
    #                 "start": 1507665886,
    #                 "end": 1621191372000
    #             },
    #             type=discord.ActivityType.playing
    #                 )

    # await Bot.change_presence(status=discord.Status.online, activity=game)
    await Bot.change_presence(activity=discord.Game(name="Playing AutoQuest Worlds! An AQW bot developed for the community. Smyess."))
    RPC = Presence(CLIEND_ID, pipe=0    )
    RPC.connect()
    RPC.update(
        state="Studying the Art of War",
        details="Bot Developer",
        start=1507665886,
        end=1621191372000,
        large_image="bloom_logo",
        large_text ="An AdventureQuest Worlds Bot - Search Class Stats, Look up Chars, Use Wiki, and more!",
        small_image="aqw_logo",
        small_text="Play AQW with us!",
        buttons=[{"label": "Join Discord", "url": "https://discord.gg/ZPURWDSGGQ"},
            {"label": "Portal Site", "url": "https://adventurequest.life/"},
        ],
        instance=True
    )

@Bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        print("System: lmao a nigger used", error)
        return
    BaseProgram.database_updating = False
    raise error


# Essential Cog
Bot.add_cog(BaseCog(Bot))
# Bot.add_cog(TestCog(Bot))
# Bot.add_cog(Help(Bot))

# Feature Cogs
Bot.add_cog(BoatSearchCog(Bot))
Bot.add_cog(CharacterCog(Bot))
Bot.add_cog(ClassSearchCog(Bot))
Bot.add_cog(GoogleSearchCog(Bot))   
Bot.add_cog(GuideCog(Bot)) 
Bot.add_cog(WikiCog(Bot))

if os.name != "nt":
    Bot.add_cog(RedditCog(Bot)) 
    Bot.add_cog(TwitterCog(Bot, BaseProgram.api))

Bot.add_cog(UtilsCog(Bot))
# Bot.add_cog(StreamCog(Bot))
Bot.add_cog(TextUploaders(Bot))
# Bot.add_cog(SWFProcessorCog(Bot)) 


print("> Starting Bot...")
Bot.run(DISCORD_TOKEN)
