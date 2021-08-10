
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


    @commands.command()
    async def board(self, ctx, mode="", *, work=""):
        true_save = False
        second_save = False
        author = str(ctx.author.id)
        author_name = str(ctx.author.name)
        allowed = await self.check_verified_botter(ctx, "WIP")

        if author in self.boaters["works"] and author_name != self.boaters["works"][author]["name"]:
            self.boaters["works"][author]["name"] = author_name
            true_save = True
        mode = mode.lower()
        if mode not in ["", "add", "rem"]:
            await ctx.send("\> `;board cmd value` Please use the follwing for `<cmd>` -> `add` | `rem`| or blank to show the list of boards.")
            return
        if mode=="add":
            
            if not allowed:
                await ctx.send("\> Apologies. But only verified Boat Makers can add to the Boatyard board..")
                return
            if not work:
                await ctx.send("\> Please add proper value. Use the commad `;board add boat_name, boat_name, etc...`. Ex. `;board add LR Revamp, Bloom Questline`")
                return
            if author not in self.boaters["works"]:
                self.boaters["works"][author] = {"name":author_name, "items":[]}



            for i in work.split(","):
                if i not in self.boaters["works"][author]["items"]:
                    self.boaters["works"][author]["items"].append(i.strip())

            second_save = True
            await ctx.send(f"\> WIP `{work}` successfully added.")
            self.git_save("boaters")
            print("> Saved")

        if mode == "rem":
            if not allowed:
                await ctx.send("\> Apologies. But only verified Boat Makers can use this command.")
                return

            if not work:
                await ctx.send("\> Please use `;board rem index` and input proper index value. Ex. `;board rem 3`")
                return

            if not work.isnumeric():
                await ctx.send("\> Please use `;board rem index` and input proper index value. Ex. `;board rem 3`")
                return

            author = str(ctx.author.id)
            ind = int(work)

            if author not in self.boaters["works"]:
                await ctx.send("\> You have no registered Work-in-progress boat.")
                return

            try:
                del self.boaters["works"][author]["items"][ind]
                if self.boaters["works"][author]["items"] == []:
                    del self.boaters["works"][author]

            except:
                await ctx.send(f"\> Item index [{ind}] does not exists for you.")
                return

            self.git_save("boaters")
            await ctx.send(f"\> Item index [{ind}] successfully removed.")
            return

        if mode == "":
            if not self.boaters["works"]:
                await ctx.send("\> There are currently no work in progress at the Bulletin board.")
                return
            st = "\u200b"
            inline = 0
            there_is_work = False
            embedVar = discord.Embed(title="Pearl Harbor's Bulletin Board",description="This is the Work-in-progress list. Made to ensure no duplicate boats are made and to increase cooperation between boat makers. \n➣ To add your currently WIP boat, use `;board add botname, botname, etcc..`.\n➣ To remove a WIP boat, use `board rem index`.\n➣ For details, use `;bhelp`.", color=BaseProgram.block_color)
            embedVar.set_author(name="AutoQuest Worlds", icon_url=BaseProgram.icon_auqw)
            for author in self.boaters["works"]:
                if not self.boaters["works"]:
                    continue

                item_list = self.boaters["works"][author]["items"]
                value = '\n'.join([f"[{item_list.index(i)}] " + i for i in item_list])
                embedVar.add_field(name=self.boaters["works"][author]["name"], value="```" + value + "```", inline=False)

                there_is_work = True
            embedVar.set_footer(text="Add/Rem commands are <@811305081097814073> privilege.")
            if not there_is_work:
                await ctx.send("\> There are currently no work in progress at the Bulletin board.")
                return

            if true_save and not second_save:
                self.git_save("boaters")
            await ctx.send(embed=embedVar)





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