import re
import os
import requests
import threading

from pprintpp import pprint
from datetime import datetime

from io import BytesIO, StringIO
from zipfile import ZipFile
from pathlib import Path

from .Base import *
from discord.ext import commands
import xml.etree.ElementTree as ET

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class SWFProcessor():

    def __init__(self):
        
        self.file = ""
        self.target = {}
        self.target_type = ""
        self.added_count = 0
        self.already_exist = 0
        self.got_it=False
        self.swf_adding = False
        self.semiList = ["Description", "Cost", "Shop item ID", "ID"]
        self.changingShops = ["Featured Gear Shop", "Nulgath's Birthday Shop"]
        self.threads = []
        self.validMode = ["all", "semi", "link"]
        self.mode = ""
        self.swf = self.openJson("./swf.json")
        self.shop_list = self.openJson("./shop_list.json")

    def openJson(self, file):
        with open(file, 'r', encoding='utf-8') as f:
           return json.load(f)

    def openFile(self, fileName):
        text = open(fileName, "r")
        return text.read()

    def saveJson(self, data, file):
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def swfadd(self, fileName):
        warn = r"> Please upload a valid .xml file"

        print("> Analysing .xml file. Please wait....")


        self.got_it = False
        self.swf_adding = True
        # file_ = await self.get_site_content(URL=target_url, is_soup=False, encoding="utf8")
        # file_ = ET.fromstring(str(file_))
        # file_ = ET.tostring(file_, encoding='unicode')

        file_ = self.openFile(fileName)
        while True:
            if '<n t="Location:' in file_:
                try:
                    self.file = file_
                    self.shopProcess()
                    self.got_it = True
                    break
                except: pass
            else:
                try:
                    self.file = file_
                    self.questProcess()
                    self.got_it = True
                    break
                except: pass

            try:
                self.file = file_
                self.itemProcess()
                self.got_it = True
                break
            except: pass
        
        if not self.got_it:
            print(warn)
            return
        print(r"> Saving to database. Please wait....")
        self.addToDatabase()

        if self.added_count:

            print(f"> Added {self.added_count} items to the Database!")
        if self.already_exist:
            print(f"> These {self.already_exist} items already exists in the Database.")

        if not self.added_count and not self.already_exist:
            print(f"> No items were added. :sadge:.")

        self.already_exist = 0
        self.added_count = 0
        self.got_it=False
        self.swf_adding = False

        print(f"> Done Analysing.")
        self.saveJson(self.swf, './swf.json')
        self.saveJson(self.shop_list, './shop_list.json')
        print("\n"*2)
        return

    def itemProcess(self):
        self.file = re.sub('(<n t=)|(/>)|(<TreeView>)|(</TreeView>)|\"', "", self.file)
        self.file = re.sub("(  )", " ", self.file)
        self.file = self.file.replace('<?xml version=1.0 encoding=us-ascii?>', "")
        self.file = self.file.split(" </n>")
        self.item_data = {}

        for i in self.file:
            item = i.strip()
            if not item:
                continue
            category_holder = ""
            linkHolder = ""
            itemDataHolder = {}

            itemName = re.search(r"(.+>?)", item)[0].replace(">", "").strip()
            if self.swf_adding:
                if itemName in self.swf:
                    self.already_exist +=1
                    continue

            itemData = item.split(">")[1].split("\n")[1:]

            for data in itemData:
                # print(f"{itemName}: {data}")
                x = data.split(":")[:]
                if x == ['']:
                    continue
                key = x[0].strip()
                value = x[1].strip().replace("&quot;", "\"")
                if "category" in key.lower():
                    category_holder = value
                if "sfile" in key.lower():
                    linkHolder = self.URLMaker(category_holder, value)
                itemDataHolder[key] = value

            if isinstance(linkHolder, tuple):
                itemDataHolder["UrlMale"] = linkHolder[0]
                itemDataHolder["UrlFemale"] = linkHolder[1]
            elif linkHolder == "":
                pass
            else:
                itemDataHolder["Url"] = linkHolder
            self.item_data[itemName] = itemDataHolder
        # pprint(self.item_data)
        self.target_type = "Item"
        self.target = self.item_data

    def shopCheck(self, fileName):
        self.file = self.openFile(fileName)
        if '<n t="Location:' not in self.file:
            return
        self.file = re.sub('(<n t=)|(/>)|(<TreeView>)|(</TreeView>)|\"', "", self.file)
        self.file = re.sub("(  )", " ", self.file)
        self.file = self.file.replace('<?xml version=1.0 encoding=us-ascii?>', "").strip()
        self.file = self.file.split("   </n>\n  </n>\n </n>")

        for shop in self.file:
            shop = shop.strip()
            if not shop:
                continue
            try:
                shopName = re.match(r"(.+>?)", shop)[0].replace(">", "")
                shopID = int(re.search(r"(ID:)(.+?)(\n)", shop)[0].replace("ID:", "").strip())
            except: continue

            if shopID not in self.shop_list:
                self.shop_list[shopID] = shopName

    def shopOrganize(self):
        print(self.shop_list)
        new_shop = {}
        for key in sorted(self.shop_list):
            print(key)
            new_shop[key] = self.shop_list[key]
        self.shop_list = new_shop
        self.saveJson(self.shop_list, './shop_list.json')
        print("> Done sorting shop ids")


    def shopProcess(self):
        self.file = re.sub('(<n t=)|(/>)|(<TreeView>)|(</TreeView>)|\"', "", self.file)
        self.file = re.sub("(  )", " ", self.file)
        self.file = self.file.replace('<?xml version=1.0 encoding=us-ascii?>', "").strip()
        self.file = self.file.split("   </n>\n  </n>\n </n>")
        self.shop_data = {}
        for shop in self.file:
            shop = shop.strip()
            if not shop:
                continue
            shopName = re.match(r"(.+>?)", shop)[0].replace(">", "")
            shopID = re.search(r"(ID:)(.+?)(\n)", shop)[0].replace("ID:", "").strip()
            shopLocation = re.search(r"(Location:)(.+?)(\n)", shop)[0].replace("Location:", "").strip()
            shopItems = shop.split("Items>")[-1].split("   </n>")

            self.shop_data[shopName] = {
                "ID": shopID,
                "Location": shopLocation,
                "Items": {},
                "Type": "Shop"
            }
            if shopID not in self.shop_list:
                self.shop_list[shopID] = shopName
            for item in shopItems:
                category_holder = ""
                linkHolder = ""
                itemDataHolder = {}

                itemName = re.search(r"(.+>?)", item)[0].replace(">", "").strip()
                if self.swf_adding:
                    if itemName in self.swf and ("Shop ID" in self.swf[itemName] or "Quest ID" in self.swf[itemName]):
                        self.already_exist +=1
                        continue

                itemData = item.split(">")[1].split("\n")[1:-1]
                for data in itemData:
                    x = data.split(":")[:]
                    if x == ['']:
                        continue
                    key = x[0].strip()
                    value = x[1].strip().replace("&quot;", "\"")
                    if "category" in key.lower():
                        category_holder = value
                    if "sfile" in key.lower():
                        linkHolder = self.URLMaker(category_holder, value)
                    itemDataHolder[key] = value

                if isinstance(linkHolder, tuple):
                    itemDataHolder["UrlMale"] = linkHolder[0]
                    itemDataHolder["UrlFemale"] = linkHolder[1]
                elif linkHolder == "":
                    pass
                else:
                    itemDataHolder["Url"] = linkHolder

                self.shop_data[shopName]["Items"][itemName] = itemDataHolder

        self.target_type = "Shop"
        print("> Entered shop")
        self.target = self.shop_data

        
        # pprint(self.shop_data)
    def questProcess(self):
        # self.file = BaseProgram.file_quest
        self.file = re.sub('(<n t=)|(/>)|(<TreeView>)|(</TreeView>)|\"', "", self.file)
        self.file = re.sub("(  )", " ", self.file)
        self.file = self.file.replace('<?xml version=1.0 encoding=us-ascii?>', "")
        self.file = self.file.split("   </n>\n  </n>\n </n>")
        self.quest_data = {}
        for quest in self.file:
            quest = quest.strip().split("   </n>\n  </n>")
            quest_header = quest[0].split("Required items>")

            if quest_header[0].strip() == "":
                continue
            quest_name = quest_header[0].split(">")[0].split("-", 1)[1].strip().replace(">", "")
            quest_id = quest_header[0].split("\n")[1].split(":")[-1].strip()
            # print(quest_name)
            # print(quest_id)

            self.quest_data[quest_name] = {
                "ID": quest_id,
                "Items": {},
                "Type": "Quest"
            }
            # Requirement items
            '''
            for quest_reward in quest_header[1:]:
                quest_reward = quest_reward.split("</n>")
                for i in quest_reward:
                    print(i)'''
            try:
                x = quest[1]
            except:
                continue

            reward_item = quest[1].replace("Rewards>", "").split("</n>")
            category_holder = ""
            linkHolder = ""
            itemDataHolder = {}

            for reward in reward_item:
                reward_dat = reward.strip().split("\n")
                itemName = reward_dat[0]
                if self.swf_adding:
                     if itemName in self.swf and ("Shop ID" in self.swf[itemName] or "Quest ID" in self.swf[itemName]):
                        self.already_exist +=1
                        continue

                details = reward_dat[1:]
                for data in details:
                    x = data.split(":")[:]
                    if x == ['']:
                        continue
                    key = x[0].strip()
                    value = x[1].strip().replace("&quot;", "\"")
                    if "category" in key.lower():
                        category_holder = value
                    if "sfile" in key.lower():
                        linkHolder = self.URLMaker(category_holder, value)
                    itemDataHolder[key] = value.replace("&#xD;&#xA", "")

                if isinstance(linkHolder, tuple):
                    itemDataHolder["UrlMale"] = linkHolder[0]
                    itemDataHolder["UrlFemale"] = linkHolder[1]
                elif linkHolder == "":
                    pass
                else:
                    itemDataHolder["Url"] = linkHolder

                self.quest_data[quest_name]["Items"][itemName] = itemDataHolder

        self.target_type = "Quest"
        self.target = self.quest_data

    def addToDatabase(self):
        type_ = self.target
        if self.target_type == "Item":
            self.swf = self.swf | self.target
            # for item in self.target:
            #     self.swf[item] = self.target
            #     self.added_count +=1
            return
        if self.target_type == "Shop":
            print("here")
            for shop in self.target:
                for item in self.target[shop]["Items"]:
                    # print(f"{shop}:  {item}")
                    # if item in self.swf:
                    #     self.already_exist +=1
                    #     continue
                    item_data = self.target[shop]["Items"][item]
                    item_data["Shop Name"] = shop
                    item_data["Shop ID"] = self.target[shop]["ID"]
                    item_data["Location"] = self.target[shop]["Location"]
                    item_data["Type"] = "Shop"
                    self.swf[item] = item_data
                    self.added_count +=1
            return
        if self.target_type == "Quest":
            for quest in self.target:
                for item in self.target[quest]["Items"]:
                    # if item in self.swf:
                    #     self.already_exist +=1
                    #     continue
                    item_data = self.target[quest]["Items"][item]
                    item_data["Quest Name"] = quest
                    item_data["Quest ID"] = self.target[quest]["ID"]
                    item_data["Type"] = "Quest"
                    self.swf[item] = item_data
                    self.added_count += 1
            return
        # new_swf = {}
        # for key in sorted(self.swf):
        #    new_swf[key] = self.swf[key]
        # self.swf = new_swf
        # pprint(self.swf)

    def reorganize(self):
        print("> Sorting")
        new_swf = {}
        for key in sorted(self.swf):
           new_swf[key] = self.swf[key]
        self.swf = new_swf
        self.saveJson(self.swf, './swf.json')
        print(">Done sorting")

    def combineSaisha(self):
        saisha = self.openJson("swf_saisha.json")
        cnt_add = 0
        cnt_exist = 0
        for item in saisha:
            if item not in self.swf:
                self.swf[item] = saisha[item]
                cnt_exist += 1
            else:
                print(f"{item}: is already here!")
                cnt_add += 1
        print(f"Added: {cnt_add}\tExists: {cnt_exist}")
        self.saveJson(self.swf, './swf.json')

    def URLMaker(self, category, file):
        category = category.lower()
        if "class" in category or "armor" in category:
            x = "https://www.aq.com/game/gamefiles/classes/M/" + file
            y = "https://www.aq.com/game/gamefiles/classes/F/" + file
            return (x, y)
        else:
            x = "https://www.aq.com/game/gamefiles/" + file
            return x

    def stats(self):
        print(f"> No. of items: {len(self.swf)}")

    def clean(self):
        for item in self.swf:
            if "Quantity" in self.swf[item]:
                del self.swf[item]["Quantity"]
            if "Char item id" in self.swf[item]:
                del self.swf[item]["Char item id"]
        self.saveJson(self.swf, './swf.json')


class SWFProcessorCog(commands.Cog, BaseTools):

    def __init__(self, bot):
        self.setup()
        self.bot = bot
        
        self.file = ""
        self.target = {}
        self.target_type = ""
        self.added_count = 0
        self.already_exist = 0
        self.got_it=False
        self.swf_adding = False
        self.semiList = ["Description", "Cost", "Shop item ID", "ID"]
        self.changingShops = ["Featured Gear Shop", "Nulgath's Birthday Shop"]
        self.threads = []
        self.validMode = ["all", "semi", "link"]
        self.mode = ""




    @commands.command()
    async def swf(self, ctx, mode=""):
        warn = r"\> Please upload a valid .xml file"
        mode = mode.lower()
        if mode not in self.validMode:
            await ctx.send(r"\> Please enter a valid mode; `all, semi, link`.")
            return

        try:
            attach = ctx.message.attachments[0]
        except:
            await ctx.send(warn)
            return

        file_n = attach.filename
        if file_n.split(".")[-1] != "xml":
            await ctx.send(warn)
            return  

        target_url = attach.url

        self.file = await self.get_site_content(URL=target_url, is_soup=False, encoding="utf8")
        test = ET.fromstring(str(self.file))
        self.file = ET.tostring(test, encoding='unicode')

        BaseProgram.database_updating = False
        try:
            # self.openFile()
            self.shopProcess()
            fp = self.printFile(mode)
        except:
            await ctx.send(r"\> Please enter only .xml files from the Shop Items.")
            return

        # await ctx.message.attachments[0].save(fp)
        await ctx.send(file=discord.File(fp[1], filename=mode + " " + fp[0]))
        return

    @commands.command()
    async def swfadd(self, ctx):
        warn = r"\> Please upload a valid .xml file"
        try:
            attach = ctx.message.attachments[0]
        except:
            await ctx.send(warn)
            return

        file_n = attach.filename
        if file_n.split(".")[-1] != "xml":
            await ctx.send(warn)
            return  

        await ctx.send(r"\> Analysing .xml file. Please wait....")

        target_url = attach.url

        self.got_it = False
        self.swf_adding = True
        file_ = await self.get_site_content(URL=target_url, is_soup=False, encoding="utf8")
        file_ = ET.fromstring(str(file_))
        file_ = ET.tostring(file_, encoding='unicode')

        if '<n t="Location:' in file_:
            try:
                self.file =file_
                self.shopProcess()
                self.got_it = True
            except: pass
        else:
            try:
                self.file = file_
                self.questProcess()
                self.got_it = True
            except: pass

        try:
            self.file = file_
            self.itemProcess()
            self.got_it = True
        except: pass
        
        print("> ==================== Here")
        if not self.got_it:
            await ctx.send(warn)
            return
        await ctx.send(r"\> Saving to database. Please wait....")
        self.addToDatabase()
        print("> kek")
        if self.added_count:
            await ctx.send(f"\> Added {self.added_count} items to the Database!")
        if self.already_exist:
            await ctx.send(f"\> These {self.already_exist} items already exists in the Database.")

        if not self.added_count and not self.already_exist:
            await ctx.send(f"\> No items were added. :sadge:.")

        self.already_exist = 0
        self.added_count = 0
        self.got_it=False
        self.swf_adding = False

        await ctx.send(f"\> Done Analysing.")

        return

    @commands.command()
    async def swfhelp(self, ctx):

        embedVar = discord.Embed(title="Bloom SWF Help", color=BaseProgram.block_color)
        desc = "`;swf mode` ➣ Converts .xml files obtained from the Loader/Grabber into a readable .txt file.\n"\
               " __NOTE:__ This currently only supports .xml files from Shop Items.\n"
        embedVar.add_field(name="Modes:", inline=False,
            value= "`link` ➣ Returns a only the links.\n"\
                   "`semi` ➣ Removes the desc/cost. Returns only important stuffs.\n"\
                   "`all` ➣ Returns text file with all details.\n")

        embedVar.description = desc

        embedVar.set_author(name="An AdventureQuest World General Discord Bot", icon_url=BaseProgram.icon_aqw)
        embedVar.set_thumbnail(url=BaseProgram.icon_bloom)
        await ctx.send(embed=embedVar)
        return
