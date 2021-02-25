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


"""



# from discord.utils import get as dis_get
# from discord_webhook import DiscordWebhook
# from PIL import Image

# import asyncio
# import aiohttp
# import urllib.parse
# import unicodedata


# Imports
import discord
import os
import tweepy

from discord.ext import tasks
from discord import Intents
from discord.ext.commands import CommandNotFound
from pprint import pprint
from time import sleep

from Cogs.Base import *
from Cogs.BoatSearchCog import BoatSearchCog
from Cogs.CharacterCog import CharacterCog
from Cogs.ClassSearchCog import ClassSearchCog
from Cogs.GuideCog import GuideCog
from Cogs.WikiCog import WikiCog
from Cogs.TwitterListener import TwitterListener
from Cogs.GoogleSearchCog import GoogleSearchCog
# from Cogs.StreamCog import StreamCog
from Cogs.TestCog import TestCog

class BreakProgram(Exception):
    pass

os.chdir(os.path.dirname(os.path.abspath(__file__)))


intents = Intents.all()
if os.name == "nt":
    Bot = commands.Bot(command_prefix=["'"], description='Bloom Bot Revamped', intents=intents)
else:
    Bot = commands.Bot(command_prefix=[";"], description='Bloom Bot Revamped', intents=intents)
Bot.remove_command("help")


@Bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        print("System: lmao a nigger used", error)
        return
    BaseProgram.database_updating = False
    raise error

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



@Bot.event
async def on_ready():
    print('> Starting Bloom bot 2')
    if os.name == "nt":
        channel = Bot.get_channel(799238286539227136)
        await channel.send("HOLA")
    name = "A bot Created by Bloom Autist. Currently Beta V.2.0.0.00"
    await Bot.change_presence(status=discord.Status.idle,
        activity=discord.Game(name=name, type=3))

    auth = tweepy.OAuthHandler(BaseProgram.CONSUMER_KEY, BaseProgram.CONSUMER_SECRET)
    auth.set_access_token(BaseProgram.ACCESS_TOKEN, BaseProgram.ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)
    # api.verify_credentials()

    tweets_listener = TwitterListener(Bot, api)
    stream = tweepy.Stream(auth, tweets_listener, tweet_mode='extended', is_async=True)
    print("> Twitter Listener Success")
    stream.filter(follow=["16480141"], is_async=True)

    # Bloom Autist ID: 1349290524901998592
    # Alina ID: 16480141
    # Use this to get IDS: https://tweeterid.com/

if os.name == "nt": # PC Mode
    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN2') # test bot token
else:              # Heroku
    DISCORD_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

BaseStuff = BaseProgram()
BaseStuff.git_prepare()

# Essential Cog
Bot.add_cog(BaseCog(Bot))
# Bot.add_cog(TestCog(Bot))

# Feature Cogs
Bot.add_cog(BoatSearchCog(Bot))
Bot.add_cog(ClassSearchCog(Bot))
Bot.add_cog(GuideCog(Bot)) 
Bot.add_cog(CharacterCog(Bot))
Bot.add_cog(WikiCog(Bot))
Bot.add_cog(GoogleSearchCog(Bot))
# Bot.add_cog(StreamCog(Bot))

# Bot.add_cog(TextUploaders(Bot))

print("> Starting Bot...")
while True:
    try:
        BaseProgram.loop.run_until_complete(Bot.run(DISCORD_TOKEN))
        print("> Discord Connection...Success!")
        break
    except:
        BaseProgram.loop.close()
        print("> Failed Connecting to Discord... Trying again.")
        print("> Reconnecting...")
        sleep(5)
        continue

# ➣➣