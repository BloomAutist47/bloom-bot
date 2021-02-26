
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
        self.char_exists = []
        self.basic_data = {
                "change": {},
                "add": {},
                "remove": {}
            }
        self.set_item_cmd = ["all", "set", "remove"]
    @commands.command()
    async def streamset(self, ctx, *, value=""):
        if not value:
            await ctx.send("Please Input value.")
            return

        id_ = str(ctx.author.id)

        if id_ not in BaseProgram.streams["users"]:
            BaseProgram.streams["users"][id_] = {}
            BaseProgram.streams["users"][id_]["stream_list"] = {}
            BaseProgram.streams["users"][id_]["time"] = 60
            BaseProgram.streams["users"][id_]["target_items"] = {}

        await ctx.send(f"➣ Setting Stream for {ctx.author}...")
        await ctx.send(f"➣ Please wait...")
        values = value.lower().split(",")

        for name in values:
            if name.strip() in BaseProgram.streams["users"][id_]["stream_list"]:
                self.char_exists.append(name)
                continue
            name = name.strip()
            name_data = await self.check_name(ctx, name)
            if not name_data:
                continue
            ccid = name_data[1]
            if not ccid:
                continue

            await self.get_inv_changes(name, ccid, id_)

        
        # await ctx.send("\u200b\n\n\n\u200b")
        # if self.char_accepted:
        #     for acc in self.char_accepted:
        #         if acc not in BaseProgram.streams["users"][id_]["stream_list"]:
        #             BaseProgram.streams["users"][id_]["stream_list"][acc]
            # self.char_accepted = []
        if self.char_rejected:
            embedVar = self.char_rejected_embed()
            await ctx.send(embed=embedVar)

        if self.char_exists:
            embedVar = self.char_existed_embed()
            await ctx.send(embed=embedVar)

        await ctx.send("➣ Done Setting Stream.")
        self.file_save("streams-settings")
        self.git_save("streams-settings")
        return

    @commands.command()
    async def streamsetitems(self, ctx, mode, *, value):
        mode = mode.strip()
        print(mode)
        if mode not in self.set_item_cmd:
            await ctx.send("➣ Please enter either `all` or `set` in <mode>.")
            return
        if not value:
            await ctx.send("➣ Please enter either a value.")
            return

        id_ = str(ctx.author.id)
        value = value.split(",")
        not_accepted = []
        done = False
        # Modes
        if mode == "all":
            for name in BaseProgram.streams["users"][id_]["stream_list"]:
                for items in value:
                    items = items.strip()
                    print(items)
                    if items in BaseProgram.streams["users"][id_]["stream_list"][name]["inventory"]:
                        if items not in BaseProgram.streams["users"][id_]["stream_list"][name]["target_items"]:
                            print("yesd")
                            BaseProgram.streams["users"][id_]["stream_list"][name]["target_items"].append(items)
                            if not done:
                                done = True
                        else:
                            continue
                    else:
                        not_accepted.append(f"{name}: {items}")
            if done:
                await ctx.send("➣ Item all Completed.")

        # [chaosripjaw, acrolous]=void essence, [item, ripjaw]=dragon shit
        print("valu: ", value)
        if mode == "set":
            for raw in value:
                items = raw.split("=")[-1].strip()
                players = raw.split("=")[0].lower().replace("[", "").replace("]", "").split(",")
                print(items)
                for name in players:
                    name = name.strip()
                    if items in BaseProgram.streams["users"][id_]["stream_list"][name]["inventory"]:
                        if items not in BaseProgram.streams["users"][id_]["stream_list"][name]["target_items"]:
                            BaseProgram.streams["users"][id_]["stream_list"][name]["target_items"].append(items)
                            if not done:
                                done = True
                        else:
                            continue
                    else:
                        not_accepted.append(f"{name}: {items}")
            if done:
                await ctx.send("➣ Item Set Completed.")

        if not_accepted:
            embedVar = self.item_not_accepted_embed(not_accepted)
            await ctx.send(embed=embedVar)

        self.file_save("streams-settings")
        self.git_save("streams-settings")
            
        #     pass

    @commands.command()
    async def stream(self, ctx, *, value=""):

        
        id_ = str(ctx.author.id)
        if id_ not in BaseProgram.streams["users"]:
            await ctx.send("➣ Please register yourself with atleast one aqw account using `;streamset player_name, player_namer, player, etc...`")
            return
        # await ctx.send("\u200b\n\n\n\u200b")

        if value == "":
            await ctx.send(f"➣ Getting Stream list for {ctx.author}")
            for name in BaseProgram.streams["users"][id_]["stream_list"]:
                await self.stream_method(ctx, name, id_)
        else:
            await ctx.send(f"➣ Getting Stream Character stream")
            values = value.lower().split(",")
            for name in values:
                await self.stream_method(ctx, name, id_)


        if self.char_rejected:
            embedVar = self.char_rejected_embed()
            await ctx.send(embed=embedVar)


        await ctx.send("➣ Done Scanning.")
        
        self.file_save("streams-settings")
        self.git_save("streams-settings")

    async def stream_method(self, ctx, name, id_):
        
        name = name.lower().lstrip().rstrip()

        name_data = await self.check_name(ctx, name)
        ccid = name_data[1]
        char_full_name = name_data[0]
        char_link = name_data[2]
        if not ccid:
            self.self.char_rejected.append(name)
            return

        data = await self.get_inv_changes(name, ccid, id_)

        if data != self.basic_data:
            
            embedVar = await self.send_to_discord(char_full_name, char_link, data)
            await ctx.send(embed=embedVar)
            pass
        else:
            embedVar = discord.Embed(color=self.block_color, description="No change")
            embedVar.set_author(name=name, url=char_link, icon_url=BaseProgram.icon_auqw)
            await ctx.send(embed=embedVar)

        



    async def check_name(self, ctx, name):
        char_link = 'https://account.aq.com/CharPage?id=' + name.replace(" ", "+")
        try:
            sites_soup = await self.get_site_content(char_link)
            char_full_name = sites_soup.find("div", {"class":"card-header"}).find("h1").text
        except:
            self.char_rejected.append(name)
            return None
        try:
            ccid = re.search("var ccid = [\d]+;", sites_soup.find_all("script")[-2].text)[0][11:-1]
            self.char_accepted.append(char_full_name)
            return (char_full_name, ccid, char_link)
        except:
            try:
                result = sites_soup.find("div", {"class": "card-body"}).find("p").text
                result = result.replace("Disabled", "**Disabled**").replace("wandering in the Void", "**wandering in The Void**").replace("frozen solid", "**Frozen solid**").replace("Deleted", "**Deleted**").replace("our","AQW's")
                result += f" [Click Here]({url}) to go to their Character Page."
                self.char_rejected.append(name)
                return None
            except:
                self.char_rejected.append(name)
                return None


    async def get_inv_changes(self, name, ccid, id_):

        # Get inventory data
        char_inv_url = "https://account.aq.com/CharPage/Inventory?ccid="+ccid
        char_inv = await self.get_site_content(char_inv_url)
        char_inv = char_inv.find("body").text[1:-1].replace("false", "False").replace("true", "True")
        char_inv = literal_eval(char_inv)
        char_inv = self.convert_form(char_inv)

        # Get time
        est_dt = datetime.now(timezone('est'))
        current_time = est_dt.strftime("%d %B %Y, %I:%M %p")

        if name not in BaseProgram.streams["users"][id_]["stream_list"]:
            BaseProgram.streams["users"][id_]["stream_list"][name] = {}
            BaseProgram.streams["users"][id_]["stream_list"][name]["time_scanned"] = current_time
            BaseProgram.streams["users"][id_]["stream_list"][name]["inventory"] = char_inv
            BaseProgram.streams["users"][id_]["stream_list"][name]["target_items"] = []
            return

        if name in BaseProgram.streams["users"][id_]["stream_list"]:
            compare = BaseProgram.streams["users"][id_]["stream_list"][name]["inventory"]

            data = {
                "change": {},
                "add": {},
                "remove": {}
            }
            for diff in list(dictdiffer.diff(compare, char_inv)):
                type_ = diff[0]

                if type_ == "change":
                    item = diff[1].split(".")[0]
                    check_ = self.is_target_item(name, item, id_)
                    if check_:
                        data["change"][item] = {"prev": diff[2][0], "next": diff[2][1]}
                    continue
                if type_ == "add":
                    for added in diff[2]:
                        item = added[0]
                        check_ = self.is_target_item(name, item, id_)
                        if check_:
                            data["add"][item] = added[1]
                    continue
                if type_ == "remove":
                    for removed in diff[2]:
                        item = removed[0]
                        check_ = self.is_target_item(name, item, id_)
                        if check_:
                            data["remove"][item] = removed[1]
                    continue

            BaseProgram.streams["users"][id_]["stream_list"][name]["time_scanned"] = current_time
            BaseProgram.streams["users"][id_]["stream_list"][name]["inventory"] = char_inv

            return data

            

            
        

        
    async def send_to_discord(self, name, url, data):
        some = False
        embedVar = discord.Embed(color=self.block_color)
        embedVar.set_author(name=name, url=url, icon_url=BaseProgram.icon_auqw)
        if data['change']:
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
            some = True
            dat_ = data["add"]
            add_desc = ""
            for add in data["add"]:
                if len(add_desc) >= 900:
                    embedVar.add_field(name="Added", value=add_desc, inline=True)
                    add_desc = ""
                add_desc+= f"📌 {add}\n"
            if add_desc == "":
                add_desc = "\u200b"
            embedVar.add_field(name="Added", value=add_desc, inline=True)

        if data['remove']:
            some = True
            dat_ = data["remove"]
            remove_desc = ""
            for rem in data["remove"]:
                if len(remove_desc) >= 900:
                    embedVar.add_field(name="Removed", value=remove_desc, inline=True)
                    remove_desc = ""
                remove_desc+= f"📌 {rem}\n"
            if remove_desc == "":
                remove_desc = "\u200b"
            embedVar.add_field(name="Removed", value=remove_desc, inline=True)
        if not some:
            embedVar.add_field(name="No change.", value="I observed it, there was no change from the previous scan", inline=True)
        return embedVar



    def convert_form(self, dict_):
        data = {}
        for i in dict_:
            data[i["strName"]] = i
        return data

    def is_target_item(self, name, item, id_):
        targets = BaseProgram.streams["users"][id_]["stream_list"][name]["target_items"]
        if not targets:
            return True
        if item in targets:
            return True
        return False

    def char_rejected_embed(self):
        embedVar = self.embed_multi_text(title="AutoQuest Worlds", field_name="Character Not found",
            description="The Following characters were not found.", 
            value_list=self.char_rejected, block_count=10,
            two_collumn=True, icon=BaseProgram.icon_auqw)
        self.char_rejected = []
        return embedVar

    def char_existed_embed(self):
        embedVar = self.embed_multi_text(title="AutoQuest Worlds", field_name="Character Already exists",
            description="The Following characters already exists.", 
            value_list=self.char_exists, block_count=10,
            two_collumn=True, icon=BaseProgram.icon_auqw)
        self.char_exists = []
        return embedVar

    def item_not_accepted_embed(self, not_accepted):
        embedVar = self.embed_multi_text(title="AutoQuest Worlds", field_name="These items are not accepted.",
            description="Make sure to check the player character page. `;streamsetitems mode item, item, item, etc...` will only work if the item is currently on the player inventory and appears on the Character Page. Copy the EXACT NAME on the char page.", 
            value_list=not_accepted, block_count=10,
            two_collumn=True, icon=BaseProgram.icon_auqw)
        return embedVar