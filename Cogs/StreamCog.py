
from .Base import *
from discord.ext import commands
from ast import literal_eval
from datetime import datetime
from pprint import pprint
from pytz import timezone
import dictdiffer  
from bs4 import BeautifulSoup as Soup
from requests import get as requests_get
from urllib.request import urlopen, Request
import cloudscraper
from time import sleep
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
        self.set_item_cmd = ["all", "set", "del"]

        self.usr_agent = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/61.0.3163.100 Safari/537.36'}
        self.user_agent = {
                'User-Agent': "DiscordBot"
            }


    @commands.command()
    async def sadd(self, ctx, *, value=""):
        if not value:
            await ctx.author.send("➣ Please Input value.")
            return

        id_ = str(ctx.author.id)
        allow = await self.user_check(ctx, id_)
        if not allow:
            return

        if id_ not in BaseProgram.streams["users"]:
            BaseProgram.streams["users"][id_] = {}
            BaseProgram.streams["users"][id_]["stream_list"] = {}
            BaseProgram.streams["users"][id_]["time"] = 60
            BaseProgram.streams["users"][id_]["target_items"] = {}

        await ctx.author.send(f"➣ Setting Stream for {ctx.author}...")
        await ctx.author.send(f"➣ Please wait...")
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

        
        if self.char_rejected:
            embedVar = self.char_rejected_embed()
            await ctx.author.send(embed=embedVar)

        if self.char_exists:
            embedVar = self.char_existed_embed()
            await ctx.author.send(embed=embedVar)

        await ctx.author.send("➣ Done Setting Stream.")
        self.file_save("streams-settings")
        self.git_save("streams-settings")
        return

    @commands.command()
    async def sdel(self, ctx, *, value=""):
        if not value:
            await ctx.author.send("➣ Please Input a character to untarget.")
            return

        id_ = str(ctx.author.id)
        allow = await self.user_check(ctx, id_)
        if not allow:
            return

        delete_once = False
        await ctx.author.send(f"➣ Deleting characters from {ctx.author}'s steam list...")
        await ctx.author.send(f"➣ Please wait...")
        values = value.lower().split(",")

        if BaseProgram.streams["users"][id_]["stream_list"]:
            for name in values:
                if name.strip() in BaseProgram.streams["users"][id_]["stream_list"]:
                    result = BaseProgram.streams["users"][id_]["stream_list"].pop(name, None)
                    if not delete_once:
                        delete_once = True
                else:
                    self.char_rejected.append(name)


            if self.char_rejected:
                embedVar = self.char_rejected_embed()
                await ctx.author.send(embed=embedVar)

            if delete_once:
                await ctx.author.send("➣ Done deleting players.")
                self.file_save("streams-settings")
                self.git_save("streams-settings")

            if not delete_once:
                await ctx.author.send(f"➣ Done. No accounts were deleted.")
        else:
            await ctx.author.send(f"➣ User {ctx.author} does not have any character in stream list.")
        return

    @commands.command()
    async def serase(self, ctx):

        id_ = str(ctx.author.id)
        allow = await self.user_check(ctx, id_)
        if not allow:
            return

        delete_once = False
        await ctx.author.send(f"➣ Deleting all character from {ctx.author}'s steam list...")
        await ctx.author.send(f"➣ Please wait...")

        if BaseProgram.streams["users"][id_]["stream_list"]:
            BaseProgram.streams["users"][id_]["stream_list"] = {}

            await ctx.author.send("➣ Done deleting players.")
            self.file_save("streams-settings")
            self.git_save("streams-settings")
            return

        else:
            await ctx.author.send(f"➣ User {ctx.author} does not have any character in stream list.")
        return


    @commands.command()
    async def slist(self, ctx, mode=""):

        id_ = str(ctx.author.id)
        allow = await self.user_check(ctx, id_)
        if not allow:
            return

        if not BaseProgram.streams["users"][id_]["stream_list"]:
            await ctx.author.send("➣ You have no registered player.")
            return

        if mode == "" or mode == "char":
            name_list = []
            for name in BaseProgram.streams["users"][id_]["stream_list"]:
                name_list.append(name)

            embedVar = self.char_all(name_list)

            await ctx.author.send(embed=embedVar)
            return

        if mode == "items":
            item_dict = {}
            for player in BaseProgram.streams["users"][id_]["stream_list"]:
                item_dict[player] = []
                for item in BaseProgram.streams["users"][id_]["stream_list"][player]["target_items"]:
                    item_dict[player].append(f"> {item}")
                if item_dict[player] == []:
                    item_dict[player].append("<None>")

            embedVar = self.embed_multi_text_indiv(title="AutoQuest Worlds",
                description="Characters and their targeted items.", 
                value_list=item_dict, block_count=10,
                icon=BaseProgram.icon_bloom)
            await ctx.author.send(embed=embedVar)


    @commands.command()
    async def sitems(self, ctx, mode="", *, value=""):
        if not mode:
            await ctx.author.send("➣ Please enter either `all` or `set` in <mode>.")
            return

        if not value:
            await ctx.author.send("➣ Please enter either a value.")
            return

        mode = mode.strip()
        if mode not in self.set_item_cmd:
            await ctx.author.send("➣ Please enter either `all` or `set` in <mode>.")
            return



        id_ = str(ctx.author.id)
        allow = await self.user_check(ctx, id_)
        if not allow:
            return

        value = value.split(",")
        not_accepted = []
        done = False
        # Modes
        if mode == "all":
            for name in BaseProgram.streams["users"][id_]["stream_list"]:
                for items in value:
                    items = items.strip()
                    if items in BaseProgram.streams["users"][id_]["stream_list"][name]["inventory"]:
                        if items not in BaseProgram.streams["users"][id_]["stream_list"][name]["target_items"]:

                            BaseProgram.streams["users"][id_]["stream_list"][name]["target_items"].append(items)
                            if not done:
                                done = True
                        else:
                            continue
                    else:
                        not_accepted.append(f"{name}: {items}")

        # [chaosripjaw, acrolous]=void essence, [item, ripjaw]=dragon shit
        if mode == "set":
            await ctx.author.send("➣ Highlight item set started.")
            for raw in value:
                items = raw.split("=")[-1].strip().replace("[", "").replace("]", "").split("/")
                players = raw.split("=")[0].lower().replace("[", "").replace("]", "").split("/")
                print("items: ", items )

                print("players: ", players)
                for name in players:
                    name = name.strip()
                    if name not in BaseProgram.streams["users"][id_]["stream_list"]:
                        if name:
                            not_accepted.append(f"> Does not exists: {name}")
                        continue


                    for item in items:
                        if item in BaseProgram.streams["users"][id_]["stream_list"][name]["inventory"]:
                            if item not in BaseProgram.streams["users"][id_]["stream_list"][name]["target_items"]:
                                BaseProgram.streams["users"][id_]["stream_list"][name]["target_items"].append(item)
                                if not done:
                                    done = True
                            else:
                                continue
                        else:
                            not_accepted.append(f"> {name}: {item}")
            if done:
                await ctx.author.send("➣ Item set Completed.")

        if mode == "del":
            await ctx.author.send("➣ Highlight item delete started.")
            for raw in value:
                items = raw.split("=")[-1].strip().replace("[", "").replace("]", "").split("/")
                players = raw.split("=")[0].lower().replace("[", "").replace("]", "").split("/")
                print("items: ", items )
                print("players: ", players)

                for name in players:
                    name = name.strip()
                    if name not in BaseProgram.streams["users"][id_]["stream_list"]:
                        if name:
                            not_accepted.append(f"> Does not exists: {name}")
                        continue

                    for item in items:
                        if item in BaseProgram.streams["users"][id_]["stream_list"][name]["inventory"]:
                            if item in BaseProgram.streams["users"][id_]["stream_list"][name]["target_items"]:
                                BaseProgram.streams["users"][id_]["stream_list"][name]["target_items"].remove(item)
                                if not done:
                                    done = True
                            else:
                                continue
                        else:
                            not_accepted.append(f"> {name}: {item}")
            if done:
                await ctx.author.send("➣ Item delete Completed.")

        if not_accepted:
            embedVar = self.item_not_accepted_embed(not_accepted)
            await ctx.author.send(embed=embedVar)

        self.file_save("streams-settings")
        self.git_save("streams-settings")
            
        #     pass

    @commands.command()
    async def sget(self, ctx, *, value=""):

        id_ = str(ctx.author.id)
        allow = await self.user_check(ctx, id_)
        if not allow:
            return

        if value == "":
            await ctx.author.send(f"➣ Getting Stream list for {ctx.author}")
            if not BaseProgram.streams["users"][id_]["stream_list"]:
                await ctx.author.send("➣ User stream list is empty")
                return

            for name in BaseProgram.streams["users"][id_]["stream_list"]:
                await self.stream_method(ctx, name, id_)
        else:
            await ctx.author.send(f"➣ Getting Stream Character stream")
            values = value.lower().split(",")
            for name in values:
                await self.stream_method(ctx, name, id_)


        if self.char_rejected:
            embedVar = self.char_rejected_embed()
            await ctx.author.send(embed=embedVar)


        await ctx.author.send("➣ Done Scanning.")
        
        self.file_save("streams-settings")
        self.git_save("streams-settings")



    @commands.command()
    async def shelp(self, ctx):
        embedVar = discord.Embed(title="Stream Help", color=BaseProgram.block_color,
            description="What is Streaming? It keeps track of character inventories and compares them to previous content each scans. "\
                "It essentially shows how much progress you've had while farming. it currently cannot do any automatic scanning because my mind is about to break."
            )

        embedVar.add_field(name="Stream Commands", inline=False, 
            value="`;shelp` ➣ Shows Stream commands.\n"\
                "`;sadd char, char,..` ➣ Adds a target character.\n"\

                "`;slist` ➣ Shows list of targeted characters.\n"\
                "`;slist items` ➣ Shows characters with highlighted items.\n"\

                "`;sget` ➣ Manually get ALL character inventory comparison.\n"
                "`;sdel char, char,..` ➣ Deletes a target character.\n"\
                "`;serase char, char,...` ➣ Removes a character.\n"\

                "`;sitems all item, item,...` ➣ Set Highlighted item to all chars. \n"\
                "`;sget char, char...` ➣ Manually get specific character inventory comparison.\n\n"
                "`;sitems set [char\\char...]=[item\\item...], [char, char...]=[item, item...],` ➣ Sets specific Highlighted items to specific characters.\n\n"\
                "`;sitems del [char\\char...]=[item\\item...], [char, char...]=[item, item...],` ➣ Delete specific Highlighted items to specific characters."\

                "\n\n")

        embedVar.add_field(name="**How to use Streams**", inline=False, 
            value="Read the following caredully.\n"
            )


        embedVar.add_field(name="📌 **Starting**", inline=False, 
            value="**1.**) Register a character you want to keep track with `;sadd char`."\
                    "```Swift\n;sadd Artix```"\
                    "If you have multiple accounts, you want to register: ```Swift\n;sadd Artix, Alina, Cysero```"\
                    "**Note**: I recommend only use 5 to 6 accounts at a time, else the rate limit of connecting to AQW server will make scanning, slow.\n"\
                    "**2.**) Use `;sget` to see your progress.\n"\
               )
        embedVar.add_field(name="📌 **Highlighting Specific Items**", inline=False, 
            value="**3.**) If you want only specific items to get tracked, e.g. **Void Aura**, use `;sitem`.\n"\
               "**4.**) `;sitem all item, item...` will keep keep track of the specific item you set for all registered characters."\
               " **Example**: ```Swift\n;sitems all Void Aura, Dai Tengu Essence```"\
               "**5.**) If you want specific characters to track certain items,\ndo `;sitem set [Artix]=[Void Aura]`"\
               " **Example**: ```Swift\n;sitems set [Artix\\Alina]=[Legion Token], [Cysero\\Memet]=[Legion Token\\Void Aura\\Magenta Dye]```"\
               "\n**Note**: Remember, the `;sitems` commands WILL ONLY track items that the player has in their character page and is currently in the inventory. AE has a retarded programming that not all misc items will appear. So I set this rule to prevent confusion."\
               "\n"
                )
        embedVar.add_field(name="📌 **Removing Stuffs**", inline=False, 
            value="**6.**) If you want to Delete highlighted items, use `;sitems del` command. It works the same way as `;sitem set` command.\n"\
                "**7.**) Unregister a character? Use `;sdel char, char....` Example:"\
                "```Swift\n;sdel Artix, Alina```"\
                "**8.**) Remove all registered character? Use `;serase`\n"\
                )



        embedVar.set_author(name="An AdventureQuest World Farming Tracker", icon_url=BaseProgram.icon_auqw)
        # embedVar.set_thumbnail(url=BaseProgram.icon_auqw)
        await ctx.send(embed=embedVar)
        return


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
        print("Da: ", data)
        if data != self.basic_data:
            
            embedVar = await self.send_to_discord(char_full_name, char_link, data)
            await ctx.author.send(embed=embedVar)
            pass
        else:
            embedVar = discord.Embed(color=BaseProgram.block_color, description="No change")
            embedVar.set_author(name=name, url=char_link, icon_url=BaseProgram.icon_aqw)
            await ctx.author.send(embed=embedVar)

    async def user_check(self, ctx, id_):
        if id_ not in BaseProgram.streams["users"]:
            await ctx.author.send("➣ Please register yourself with atleast one aqw account using `;streamset player_name, player_namer, player, etc...`")
            return False
        return True



    async def get_content(self, URL):



        while True:
            try:
                usr_agent = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/61.0.3163.100 Safari/537.36'}
                usr_agent2 = {'User-agent': 'your bot 0.1'}
                req = Request(URL,headers=usr_agent2)
                self.response = urlopen(req)
                soup = Soup(self.response.read(), 'html5lib')
                print("> Success")
                return soup
                
            except:
                print("> Retry")
                sleep(12)
                continue

    async def check_name(self, ctx, name):

        try:
            char_link = 'https://account.aq.com/CharPage?id=' + name.replace(" ", "+")

            sites_soup = await self.get_content(char_link)
            char_full_name = sites_soup.find("div", {"class":"card-header"}).find("h1").text

            ccid = re.search("var ccid = [\d]+;", sites_soup.find_all("script")[-2].text)[0][11:-1]
            self.char_accepted.append(char_full_name)
            return (char_full_name, ccid, char_link)
        except:
            try:
                result = sites_soup.find("div", {"class": "card-body"}).find("p").text
                result = result.replace("Disabled", "**Disabled**").replace("wandering in the Void", "**wandering in The Void**").replace("frozen solid", "**Frozen solid**").replace("Deleted", "**Deleted**").replace("our","AQW's")
                result += f" [Click Here]({url}) to go to their Character Page."
                self.char_rejected.append(name)
                print("nope this")
                return None
            except:
                print("this part")
                self.char_rejected.append(name)
                return None


    async def get_inv_changes(self, name, ccid, id_):

        # Get inventory data
        char_inv_url = "https://account.aq.com/CharPage/Inventory?ccid="+ccid
        char_soup = await self.get_content(char_inv_url)
        char_inv = char_soup.find("body").text[1:-1].replace("false", "False").replace("true", "True")
        try:
            char_inv = literal_eval(char_inv.strip())
        except:
            raise error
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
        embedVar = discord.Embed(color=BaseProgram.block_color)
        embedVar.set_author(name=name, url=url, icon_url=BaseProgram.icon_aqw)
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
            two_collumn=True, icon=BaseProgram.icon_bloom)
        self.char_rejected = []
        return embedVar

    def char_existed_embed(self):
        embedVar = self.embed_multi_text(title="AutoQuest Worlds", field_name="Character Already exists",
            description="The Following characters already exists.", 
            value_list=self.char_exists, block_count=10,
            two_collumn=True, icon=BaseProgram.icon_bloom)
        self.char_exists = []
        return embedVar

    def char_all(self, list):
        embedVar = self.embed_multi_text(title="AutoQuest Worlds", field_name="Characters",
            description="List of registered characters.", 
            value_list=list, block_count=10,
            two_collumn=True, icon=BaseProgram.icon_bloom)
        self.char_exists = []
        return embedVar

    def item_not_accepted_embed(self, not_accepted):
        embedVar = self.embed_multi_text(title="AutoQuest Worlds", field_name="These items are not accepted.",
            description="Make sure to check the player character page. `;streamitems mode item, item, item, etc...` will only work if the item is currently on the player inventory and appears on the Character Page. Copy the EXACT NAME on the char page.", 
            value_list=not_accepted, block_count=10,
            two_collumn=True, icon=BaseProgram.icon_bloom)
        return embedVar