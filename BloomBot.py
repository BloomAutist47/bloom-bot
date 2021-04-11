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

"""

# Imports
import discord
import os
import tweepy

from discord.ext import tasks
from discord import Intents
from discord.ext.commands import CommandNotFound
# import pypresence
from pprint import pprint   
from time import sleep  
from datetime import datetime
from pytz import timezone

from Cogs.Base import *
from Cogs.BoatSearchCog import BoatSearchCog
from Cogs.CharacterCog import CharacterCog
from Cogs.ClassSearchCog import ClassSearchCog
from Cogs.GoogleSearchCog import GoogleSearchCog
from Cogs.GuideCog import GuideCog
from Cogs.WikiCog import WikiCog
# from Cogs.TwitterListener import TwitterListener
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
Bot = commands.Bot(command_prefix=[cmd], description='Bloom Bot Revamped', intents=intents, help_command=None)



BaseStuff = BaseProgram()
BaseStuff.git_prepare()

BaseProgram.auth = tweepy.OAuthHandler(BaseProgram.CONSUMER_KEY, BaseProgram.CONSUMER_SECRET)
BaseProgram.auth.set_access_token(BaseProgram.ACCESS_TOKEN, BaseProgram.ACCESS_TOKEN_SECRET)

BaseProgram.api = tweepy.API(BaseProgram.auth)
BaseProgram.api.verify_credentials()



# async def stream_tweet():
#     BaseProgram.tweets_listener = TwitterListener(Bot, BaseProgram.api)
#     BaseProgram.stream = tweepy.Stream(BaseProgram.auth, BaseProgram.tweets_listener, is_async=True,  tweet_mode='extended')
#     print("> Twitter Listener Success")

#     BaseProgram.stream.filter(follow=BaseProgram.tweet_user_list, is_async=True, stall_warnings=True)

    # Bloom Autist ID: 1349290524901998592
    # Alina ID: 16480141
    # Use this to get IDS: https://tweeterid.com/


def rich_presence():
    RPC = pypresence.Presence(client_id=CLIEND_ID, pipe=0, loop=BaseProgram.loop) 
    y = RPC.connect()
    x = RPC.update(state="Rich Presence using pypresence!", details="A test of qwertyquerty's Python Discord RPC wrapper, pypresence!")

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

    # name = "A bot Created by Bloom Autist. Currently v.4.0.0.00"

    # game = discord.Activity(state="with the API",name="AdventureQuest Worlds", details="suck madasdasd", type=discord.ActivityType.playing,
    #      url="https://www.youtube.com/channel/UCfiSbTjgVesx8wllBz4aIxw",
    #             assets={"large_image": "nigmoirehd_x1024", "small_image":"nigmoirehd_x512", "large_text":"test", "small_text":"Asdasd"},
    # await Bot.change_presence(status=discord.Status.online, activity=game)

    # await Bot.change_presence(status=discord.Status.idle,
    #     activity=discord.Game(name=name, type=3))
    
    # Bot.loop.create_task(stream_tweet())
    # Bot.loop.create_task(stre())
        
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

# Feature Cogs
Bot.add_cog(BoatSearchCog(Bot))
Bot.add_cog(CharacterCog(Bot))
Bot.add_cog(ClassSearchCog(Bot))
Bot.add_cog(GoogleSearchCog(Bot))   
Bot.add_cog(GuideCog(Bot)) 
Bot.add_cog(WikiCog(Bot))

Bot.add_cog(RedditCog(Bot)) 
# Bot.add_cog(TwitterCog(Bot, BaseProgram.api))

Bot.add_cog(UtilsCog(Bot))
# Bot.add_cog(StreamCog(Bot))
Bot.add_cog(TextUploaders(Bot))
# Bot.add_cog(SWFProcessorCog(Bot)) 


print("> Starting Bot...")
Bot.run(DISCORD_TOKEN)


# @Bot.event
# async def on_member_update(before, after):
#     satanId = 212913871466266624
#     if os.name == "nt":
#         satanRoleId = 808657429784035338
#         guild_id = 761956630606250005
#     else:
#         satanRoleId = 775824347222245426
#         guild_id = 766627412179550228
    
#     guild = Bot.get_guild(guild_id)
#     role = dis_get(guild.roles, name='satan', id=satanRoleId)
#     role_ids = [x.id for x in after.roles]
#     if after.id != satanId and satanRoleId in role_ids:
#         await after.remove_roles(role)