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
        print("> Addinfff")
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

    def openFile(self):
        text = open(self.fileName, "r")
        self.file = text.read()

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
            # try:
            itemName = re.search(r"(.+\>?)", item)[0].replace(">", "").strip()
            if self.swf_adding:
                if itemName in BaseProgram.swf:
                    self.already_exist +=1
                    continue
            print(f"> {itemName}", end=" ")
            itemData = item.split(">")[1].split("\n")[1:-1]
            # print(itemData)
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
            self.item_data[itemName] = itemDataHolder
        # pprint(self.item_data)
        self.target_type = "Item"
        self.target = self.item_data

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
            shopName = re.match(r"(.+\>?)", shop)[0].replace(">", "")
            shopID = re.search(r"(ID:)(.+?)(\n)", shop)[0].replace("ID:", "").strip()
            shopLocation = re.search(r"(Location:)(.+?)(\n)", shop)[0].replace("Location:", "").strip()
            shopItems = shop.split("Items>")[-1].split("   </n>")

            self.shop_data[shopName] = {
                "ID": shopID,
                "Location": shopLocation,
                "Items": {},
                "Type": "Shop"
            }

            for item in shopItems:
                category_holder = ""
                linkHolder = ""
                itemDataHolder = {}

                itemName = re.search(r"(.+\>?)", item)[0].replace(">", "").strip()
                if self.swf_adding:
                    if itemName in BaseProgram.swf and ("Shop ID" in BaseProgram.swf[itemName] or "Quest ID" in BaseProgram.swf[itemName]):
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
                     if itemName in BaseProgram.swf and ("Shop ID" in BaseProgram.swf[itemName] or "Quest ID" in BaseProgram.swf[itemName]):
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

    def swfGetter(self, shop, items, start, end):
        # print("Target Shop>>>: ", shop)
        for link in items[start:end]:
            link_arr = link.split("/")
            # print(link_arr)
            try:

                path = f'./Downloaded/{shop}/' + link_arr[-2] + '/'
            except:
                
                raise BREAKSHIT
            file_name = link_arr[-1] + ''

            Path(path).mkdir(parents=True, exist_ok=True)
            completeName = os.path.join(path, file_name)
            
            file = requests.get(link)

            try:
                assert os.path.isfile(completeName)
            except:
                print(">>>>>>>>>>>>>>>>>>>>> ", completeName)
            # with open(completeName, "r") as f:
            #     pass

            f = open(completeName, "wb")
            f.write(file.content)
            f.close()
            # print("Downloading", link)

    def downloadFile(self, result_list, num_splits=100):
        for shop in result_list:
            items = result_list[shop]["Items"].split("\n")
            if items == [""]:
                continue

            split_size = len(items)  # num splits
            self.threads = []
            for i in range(num_splits):
                # determine the indices of the list this thread will handle
                start = i * split_size
                # special case on the last chunk to account for uneven splits
                end = None if i+1 == num_splits else (i+1) * split_size
                # create the thread
                self.threads.append(
                    threading.Thread(target=self.swfGetter, args=(shop, items, start, end)))
                self.threads[-1].start()  # start the thread we just created

            # wait for all threads to finish
            for t in self.threads:
                t.join()

    def addToDatabase(self):
        type_ = self.target
        if self.target_type == "Item":
                for item in self.target:
                    BaseProgram.swf[item] = self.target
                    self.added_count +=1
                    print(f"> ADDED: {item}", end=" ")

        if self.target_type == "Shop":
            for shop in self.target:
                for item in self.target[shop]["Items"]:
                    # if item in BaseProgram.swf:
                    #     self.already_exist +=1
                    #     continue
                    item_data = self.target[shop]["Items"][item]
                    item_data["Shop Name"] = shop
                    item_data["Shop ID"] = self.target[shop]["ID"]
                    item_data["Location"] = self.target[shop]["Location"]
                    item_data["Type"] = "Shop"
                    BaseProgram.swf[item] = item_data
                    self.added_count +=1

        if self.target_type == "Quest":
            for quest in self.target:
                for item in self.target[quest]["Items"]:
                    # if item in BaseProgram.swf:
                    #     self.already_exist +=1
                    #     continue
                    item_data = self.target[quest]["Items"][item]
                    item_data["Quest Name"] = quest
                    item_data["Quest ID"] = self.target[quest]["ID"]
                    item_data["Type"] = "Quest"
                    BaseProgram.swf[item] = item_data
                    self.added_count += 1

        # new_swf = {}
        # for key in sorted(BaseProgram.swf):
        #    new_swf[key] = BaseProgram.swf[key]
        print("\n\n\ngonna save")
        # BaseProgram.swf = new_swf
        while True:
            try:
                self.loop.create_task(self.git_save("swf"))
                break
            except:
                print("> Github `swf` save failed. Trying again...")
                continue
        # for items in self.target:
        #     result += f"Shop Name: {items}\n"
        #     result += f"ID: {self.target[items]['ID']}\n"
        #     result += f"Location: {self.target[items]['Location']}\n\n\n"

        #     for item in self.target[items]["Items"]:
        #         result += f"Name: {item}\n"
        #         ref = self.target[items]["Items"][item]
        #         for part in ref:
        #             result += f"{part}: {ref[part]}\n"
        #         result += "\n"
        #     result_list[items] = {}
        #     result_list[items]["ID"] = self.target[items]['ID']
        #     result_list[items]["Items"] = result.strip()
        #     result = ""


    def printFile(self, mode):
        result = ""
        result_list = {}
        if mode == "link":
            for items in self.target:
                for item in self.target[items]["Items"]:
                    ref = self.target[items]["Items"][item]
                    if "Url" in ref:
                        result += ref["Url"] + "\n"
                    if "UrlMale" in ref:
                        result += ref["UrlMale"] + "\n"
                    if "UrlFemale" in ref:
                        result += ref["UrlFemale"] + "\n"
                    continue
                result_list[items] = {}
                result_list[items]["ID"] = self.target[items]['ID']
                result_list[items]["Items"] = result.strip()
                result = ""

        if mode == "downloaded":
            for items in self.target:
                for item in self.target[items]["Items"]:
                    ref = self.target[items]["Items"][item]
                    if "Url" in ref:
                        result += ref["Url"] + "\n"
                    if "UrlMale" in ref:
                        result += ref["UrlMale"] + "\n"
                    if "UrlFemale" in ref:
                        result += ref["UrlFemale"] + "\n"
                    continue
                result_list[items] = {}
                result_list[items]["ID"] = self.target[items]['ID']
                result_list[items]["Items"] = result.strip()
                result = ""
            self.downloadFile(result_list)

        if mode == "semi":
            for items in self.target:
                result += f"Shop Name: {items}\n"
                result += f"ID: {self.target[items]['ID']}\n"
                result += f"Location: {self.target[items]['Location']}\n\n\n"

                for item in self.target[items]["Items"]:

                    ID = self.target[items]["Items"][item]["ID"]
                    shopID = self.target[items]["Items"][item]["Shop item ID"]
                    result += f"Name: {item}\nID: {ID} | Shop Item ID: {shopID} | "

                    ref = self.target[items]["Items"][item]
                    for part in ref:
                        if part in self.semiList:
                            continue
                        result += f"{part}: {ref[part]}\n"
                    result += "\n"
                result_list[items] = {}
                result_list[items]["ID"] = self.target[items]['ID']
                result_list[items]["Items"] = result.strip()
                result = ""

        if mode == "all":
            for items in self.target:
                result += f"Shop Name: {items}\n"
                result += f"ID: {self.target[items]['ID']}\n"
                result += f"Location: {self.target[items]['Location']}\n\n\n"

                for item in self.target[items]["Items"]:
                    result += f"Name: {item}\n"
                    ref = self.target[items]["Items"][item]
                    for part in ref:
                        result += f"{part}: {ref[part]}\n"
                    result += "\n"
                result_list[items] = {}
                result_list[items]["ID"] = self.target[items]['ID']
                result_list[items]["Items"] = result.strip()
                result = ""
        # pprint(result_list)
        if len(result_list) == 1:
            res = self.createTxt(result_list)

        else:
            res = self.createZip(result_list)
        return res

    def createTxt(self, result_list):
        string = StringIO()
        ID = ""
        items = ""
        for item in result_list:
            items = item.replace("\r", "")
            ID = result_list[item]["ID"]
            string.write(result_list[item]["Items"])

        string.seek(0)
        # if items in self.changingShops:
        #     
        #     textProccessed = open(f"SWF [{ID}] {items} {time}.txt",'w')
        # else:
        #     textProccessed = open(f"SWF [{ID}] {items}.txt",'w')
        if items in self.changingShops:
            time = self.getTime()
            name = f"SWF [{ID}] {items} {time}.txt"
        else:
            name = f"SWF [{ID}] {items}.txt"
        
        # data = archive.read()

        # textProccessed.write(string.getvalue())

        return (name, string)

    def createZip(self, res):
        # pprint(res)
        archive = BytesIO()
        zipArchive = ZipFile(archive, mode="w")
        for items in res:
            if items in self.changingShops:
                today = datetime.today()
                datem = datetime(today.year, today.month, 1)
                time = datem.strftime("%B %Y")
                zipArchive.writestr(f"SWF [{res[items]['ID']}] {items} {time}.txt", res[items]["Items"])
            else:
                zipArchive.writestr(f"SWF [{res[items]['ID']}] {items}.txt", res[items]["Items"])

        zipArchive.close()

        archive.seek(0)
        # data = archive.read()

        # zipProccessed = open('./SWF txts.zip','wb')
        # zipProccessed.write(data)
        return ("SWF Result.zip", archive)

    def getTime(self):
        today = datetime.today()
        datem = datetime(today.year, today.month, 1)
        time = datem.strftime("%B %Y")
        return time

    def URLMaker(self, category, file):
        category = category.lower()
        if "class" in category or "armor" in category:
            x = "https://www.aq.com/game/gamefiles/classes/M/" + file
            y = "https://www.aq.com/game/gamefiles/classes/F/" + file
            return (x, y)
        else:
            x = "https://www.aq.com/game/gamefiles/" + file
            return x


# x = SWFProcessor("./Test Files/single_shop.xml")


