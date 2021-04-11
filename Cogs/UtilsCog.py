
import os
from .Base import *
from discord.ext import commands, tasks

# from layeris.layer_image import LayerImage
# from PIL import Image, ImageDraw

# from random import randint

# from .Base import *
# from discord.ext import commands
# from time import sleep
# from io import BytesIO

from datetime import datetime
from pytz import timezone

class UtilsCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.bot = bot
        self.done = False

        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        os.chdir('..')
        
        
        self.serverTime.start()

    # @tasks.loop(minutes=60.0)
    # async def update_profile(self):
    #     await asyncio.sleep(20)
    #     await self.change_profile()

    # @commands.command()
    # async def change(self, ctx):
    #     await self.change_profile()

    @tasks.loop(minutes=5)
    async def serverTime(self):
        eastern = timezone('US/Eastern')
        
        est_dt = datetime.now(eastern)

        current_time = est_dt.strftime("%I:%M %p")
        # print(current_time)
        if os.name == "nt":
            channel = await self.bot.fetch_channel(830706429765746718)
        else:
            channel = await self.bot.fetch_channel(811305082758758437)

        await channel.edit(name=f"Server Time: {current_time.upper()}")
        return


    # async def change_profile(self):
    #     sb = "./Data/Resources/icon/bloom_icon_symbol.png"
    #     bg = "./Data/Resources/icon/bloom_icon_bg.png"
    #     save_loc = "./Data/Resources/icon/avatar.png"

    #     symbol = LayerImage.from_file(sb)
    #     symbol.grayscale()
    #     color = "#%06x" % randint(0, 0xFFFFFF)
        
    #     BaseProgram.block_color = int(hex(int(color.replace("#", ""), 16)), 0)
    #     print(BaseProgram.block_color)
    #     symbol.overlay(color)
    #     symbol.save(save_loc)

        
    #     base_image = Image.open(save_loc)
    #     img = ImageDraw.Draw(base_image)

    #     bg_overlay = Image.open(bg)
    #     base_image.paste(bg_overlay, (0, 0), mask=bg_overlay)

    #     new_image = self.image_to_byte_array(base_image)

    #     # await self.bot.user.edit(avatar=new_image)
    #     self.done = True


    # def image_to_byte_array(self, image):
    #   imgByteArr = BytesIO()
    #   image.save(imgByteArr, format='PNG')
    #   imgByteArr = imgByteArr.getvalue()
    #   return imgByteArr