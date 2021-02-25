
from .Base import *
from discord.ext import commands
from ast import literal_eval
from datetime import datetime
from pprint import pprint
from pytz import timezone
import dictdiffer  
# from bs4 import BeautifulSoup as Soup


class StreamCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot
        self.list_links = {}
        self.compare = {}

        self.char_rejected = []
        self.char_accepted = []

    @commands.command()
    async def setstreams(self, ctx, *, value=""):
        if not value:
            await ctx.send("Please Input value.")

        id_ = str(ctx.author.id)

        if id_ not in BaseProgram.settings["StreamCogSettings"]["users"]:
            BaseProgram.settings["StreamCogSettings"]["users"][id_] = {}
            BaseProgram.settings["StreamCogSettings"]["users"][id_]["stream_list"] = []
            BaseProgram.settings["StreamCogSettings"]["users"][id_]["time"] = 30
            BaseProgram.settings["StreamCogSettings"]["users"][id_]["target_items"] = {}

        await ctx.send(f"➣ Setting Stream for {ctx.author}")

        values = value.lower().split(",")

        for name in values:
            name = name.lower().lstrip().rstrip()

            ccid = self.check_name(ctx, name)
            if not ccid:
                continue

            await self.get_inv_changes(ctx, ccid)

        await ctx.send("➣ Done Setting Stream.")
        await ctx.send("\u200b\n\n\n\u200b")

        for acc in self.char_accepted:
            if acc not in BaseProgram.settings["StreamCogSettings"]["users"][id_]["stream_list"]:
                BaseProgram.settings["StreamCogSettings"]["users"][id_]["stream_list"].append(acc)
        if self.char_rejected:
            embedVar = self.embed_multi_text(title="AutoQuest Worlds", field_name="Character Not found",
                description="The Following characters were not found. Please recheck them.", block_count=10,
                two_collumn=True, icon=BaseProgram.icon_auqw)


        self.file_save("streams-settings")
        self.git_save("streams-settings")


    @commands.command()
    async def stream(self, ctx, *, value=""):

        if not value:
            await ctx.send("Please Input value.")

        id_ = str(ctx.author.id)

        await ctx.send("\u200b\n\n\n\u200b")
        await ctx.send(f"➣ Setting Stream for {ctx.author}")

        values = value.lower().split(",")

        for name in values:
            name = name.lstrip().rstrip()

            ccid = self.check_name(ctx, name)
            if not ccid:
                continue

            await self.get_inv_changes(ctx, ccid)


            if data != {
                "change": {},
                "add": {},
                "remove": {}
            }:
                
                embedVar = await self.send_to_discord(char_full_name, char_link, data)
                await ctx.send(embed=embedVar)
                pass
            else:
                embedVar = discord.Embed(color=self.block_color)
                embedVar.set_author(name=name, url=char_link, icon_url=BaseProgram.icon_auqw)
                embedVar.add_field(name="No change.", value="I observed it, there was no change from the previous scan", inline=True)
                await ctx.send(embed=embedVar)

        await ctx.send("➣ Done Scanning.")
        self.file_save("streams-settings")
        self.git_save("streams-settings")

    def check_name(self, ctx, name):
        char_link = 'https://account.aq.com/CharPage?id=' + name.replace(" ", "+")
        sites_soup = await self.get_site_content(char_link)
        char_full_name = sites_soup.find("div", {"class":"card-header"}).find("h1").text



        try:
            ccid = re.search("var ccid = [\d]+;", sites_soup.find_all("script")[-2].text)[0][11:-1]
            self.char_accepted.append(char_full_name)
            return ccid
        except:
            try:
                result = sites_soup.find("div", {"class": "card-body"}).find("p").text
                result = result.replace("Disabled", "**Disabled**").replace("wandering in the Void", "**wandering in The Void**").replace("frozen solid", "**Frozen solid**").replace("Deleted", "**Deleted**").replace("our","AQW's")
                result += f" [Click Here]({url}) to go to their Character Page."
                self.char_rejected.append((name, "Problematic"))
                return None
            except:
                self.char_rejected.append((name, "Char does not exists."))
                return None


    async def get_inv_changes(self, ctx, ccid):

        # Get inventory data
        char_inv_url = "https://account.aq.com/CharPage/Inventory?ccid="+ccid
        char_inv = await self.get_site_content(char_inv_url)
        char_inv = char_inv.find("body").text[1:-1].replace("false", "False").replace("true", "True")
        char_inv = literal_eval(char_inv)
        char_inv = self.convert_form(char_inv)

        # Get time
        est_dt = datetime.now(timezone('est'))
        current_time = est_dt.strftime("%d %B %Y, %I:%M %p")

        if name not in BaseProgram.streams:
            BaseProgram.streams[name] = {}
            BaseProgram.streams[name]["time"] = current_time
            BaseProgram.streams[name]["inventory"] = char_inv
            
            print("pre saved")
            print("Character saved to stream list")
            self.file_save("streams-settings")
            self.git_save("streams-settings")
            return

        if name in BaseProgram.streams:
            compare = BaseProgram.streams[name]["inventory"]

            data = {
                "change": {},
                "add": {},
                "remove": {}
            }
            for diff in list(dictdiffer.diff(compare, char_inv)):
                type_ = diff[0]

                if type_ == "change":
                    item = diff[1].split(".")[0]
                    data["change"][item] = {"prev": diff[2][0], "next": diff[2][1]}
                    continue
                if type_ == "add":
                    for added in diff[2]:
                        item = added[0]
                        data["add"][item] = added[1]
                    continue
                if type_ == "remove":
                    for added in diff[2]:
                        item = added[0]
                        data["remove"][item] = added[1]
                    continue

            BaseProgram.streams[name]["time"] = current_time
            BaseProgram.streams[name]["inventory"] = char_inv

            print("Character saved to stream list")
            return data

            

            
        

        
    async def send_to_discord(self, name, url, data):
        some = False
        embedVar = discord.Embed(color=self.block_color)
        embedVar.set_author(name=name, url=url, icon_url=BaseProgram.icon_auqw)
        if data['change']:
            print("change")
            some = True
            dat_ = data["change"]
            change_desc = ""
            for change in data["change"]:
                if len(change_desc) >= 900:
                    embedVar.add_field(name="Changed", value=change_desc, inline=True)
                    change_desc = ""
                change_desc+= f"📌 {change}**:** {dat_[change]['prev']} ➣ {dat_[change]['next']}\n"
            if change_desc == "":
                change_desc = "\u200b"
            embedVar.add_field(name="Changed", value=change_desc, inline=True)

        if data['add']:
            print("change", data['add'])
            some = True
            dat_ = data["add"]
            add_desc = ""
            for add in data["add"]:
                if len(add_desc) >= 900:
                    embedVar.add_field(name="Added", value=add_desc, inline=True)
                    add_desc = ""
                add_desc+= f"📌 {add}**:** {dat_[add]['strType']}\n"
            if add_desc == "":
                add_desc = "\u200b"
            embedVar.add_field(name="Added", value=add_desc, inline=True)

        if data['remove']:
            print("rem", data['remove'])
            some = True
            dat_ = data["remove"]
            remove_desc = ""
            for rem in data["remove"]:
                if len(remove_desc) >= 900:
                    embedVar.add_field(name="Removed", value=remove_desc, inline=True)
                    remove_desc = ""
                remove_desc+= f"📌 {rem}**:** {dat_[rem]['strType']}\n"
            if remove_desc == "":
                remove_desc = "\u200b"
            embedVar.add_field(name="Removed", value=remove_desc, inline=True)
        if not some:
            print("not")
            embedVar.add_field(name="No change.", value="I observed it, there was no change from the previous scan", inline=True)
        print("what?")
        return embedVar



    def convert_form(self, dict_):
        data = {}
        for i in dict_:
            data[i["strName"]] = i
        return data
