
from .Base import *
from discord.ext import commands
from ast import literal_eval
from datetime import datetime

class StreamCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot
        self.list_links = {}
        self.compare = {}


    @commands.command()
    async def setstream(self, ctx, *, value=""):
        

        if not value:
            await ctx.send("Please Input value.")

        id_ = str(ctx.author.id)
        confirmed_name = []

        empty_char = []
        await ctx.send(f"➣ Setting Stream for {ctx.author}")
        # print(BaseProgram.steams)
        values = value.split(" ")
        print(values)
        for name in values:
            name = name.lower()
            char_link = 'https://account.aq.com/CharPage?id=' + name

           
            sites_soup = await self.get_site_content(char_link)

            try:
                ccid = re.search("var ccid = [\d]+;", sites_soup.find_all("script")[-2].text)[0][11:-1]
                print(ccid)
            except:
                try:
                    result = sites_soup.find("div", {"class": "card-body"}).find("p").text
                    result = result.replace("Disabled", "**Disabled**").replace("wandering in the Void", "**wandering in The Void**").replace("frozen solid", "**Frozen solid**").replace("Deleted", "**Deleted**").replace("our","AQW's")
                    result += f" [Click Here]({url}) to go to their Character Page."
                    # print(result)
                    await ctx.send(embed=self.embed_single("Stream Result", result))
                    continue
                except:
                    print("No Character")
                    await ctx.send(embed=self.embed_single("Stream Result", "No Character of that name"))
                    continue

            confirmed_name.append(name)
            print("broke")
            char_inv_url = "https://account.aq.com/CharPage/Inventory?ccid="+ccid
            char_inv = await self.get_site_content(char_inv_url)
            print("Here")
            char_inv = char_inv.find("body").text[1:-1].replace("false", "False").replace("true", "True")
            char_inv = ast.literal_eval(char_inv)
            print(char_inv)
            char_inv = self.convert_form(char_inv)
            pprint(char_inv)
            # weapon_type = ["Axe", "Bow", "Dagger", "Gun", "Mace", "Polearm", "Staff", "Sword", "Wand"]

            # item_count = {"Weapon": 0}
            # for item in char_inv:
            #     item_type = char_inv[item]["strType"]
            #     if item_type in weapon_type:
            #         item_count["Weapon"] += 1
            #         continue
            #     if item_type not in item_count:
            #         item_count[item_type] = 0
            #     item_count[item_type] += 1

            # pprint(char_inv)
            est_dt = datetime.now(timezone('est'))
            current_time = est_dt.strftime("%d %B %Y, %I:%M %p")

            if name not in BaseProgram.streams:
                BaseProgram.streams[name] = {}
                BaseProgram.streams[name]["time"] = current_time
                BaseProgram.streams[name]["inventory"] = char_inv
                

                print("Character saved to stream list")
                self.file_save()
                return

            if name in BaseProgram.streams:
                compare = BaseProgram.streams[name]["inventory"]

                data = {
                    "change": {},
                    "add": {},
                    "remove": {}
                }

                # for item in compare:
                #     if item in char_inv:
                for diff in list(dictdiffer.diff(compare, char_inv)):
                    # print(diff)
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
                        # print(diff)
                        # print(f"{item}: ", diff)
                    # else:
                    #     # diff_["remove"][item] = "True"
                    #     print(f"{diff} is gone!")

                BaseProgram.streams[name]["time"] = current_time
                BaseProgram.streams[name]["inventory"] = char_inv
                pprint(data)
                if data != {
                    "change": {},
                    "add": {},
                    "remove": {}
                }:
                    # type_ = self.change_data(data)
                    
                    print("Data")
                    pprint(data)
                    print("\n"*3)
                    pass
                else:
                    print("No difference")
                print("Character saved to stream list")

        if id_ not in BaseProgram.settings["StreamCogSettings"]["users"]:
            BaseProgram.settings["StreamCogSettings"]["users"][id_] = {}
        for acc in confirmed_name:
            if acc not in BaseProgram.settings["StreamCogSettings"]["users"][id_]["stream_list"]:
                BaseProgram.settings["StreamCogSettings"]["users"][id_]["stream_list"].append(acc)
        
        self.git_save("streams-settings")
        


    def convert_form(self, dict_):
        data = {}
        for i in dict_:
            data[i["strName"]] = i
        return data
