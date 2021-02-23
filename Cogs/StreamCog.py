
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

        BaseProgram.loop.run_until_complete(self.stream_player())


    @commands.command()
    async def stream(self, ctx, *, value=""):
        print(ctx.author)

        if not value:
            await ctx.send("Please Input value.")

        value = value.split(" ")
        for name in value:
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
                    print(result)
                    # await ctx.send(embed=self.embed_single("Character Profile Result", result))
                    return
                except:
                    print("No Character")
                    # await ctx.send(embed=self.embed_single("Character Profile Result", "No Character of that name"))
                    return


            char_inv_url = "https://account.aq.com/CharPage/Inventory?ccid="+ccid
            char_inv = await self.get_site_content(char_inv_url)
            char_inv = char_inv.find("body").text[1:-1].replace("false", "False").replace("true", "True")
            char_inv = literal_eval(char_inv)
            char_inv = self.convert_form(char_inv)

            weapon_type = ["Axe", "Bow", "Dagger", "Gun", "Mace", "Polearm", "Staff", "Sword", "Wand"]

            item_count = {"Weapon": 0}
            for item in char_inv:
                item_type = char_inv[item]["strType"]
                if item_type in weapon_type:
                    item_count["Weapon"] += 1
                    continue
                if item_type not in item_count:
                    item_count[item_type] = 0
                item_count[item_type] += 1


            # pprint(char_inv)
            est_dt = datetime.now(timezone('est'))
            current_time = est_dt.strftime("%d %B %Y, %I:%M %p")

            if name not in BaseProgram.stream_list:
                BaseProgram.stream_list[name] = {}
                BaseProgram.stream_list[name]["time"] = current_time
                BaseProgram.stream_list[name]["inventory"] = char_inv
                

                print("Character saved to stream list")
                self.file_save()
                return

            if name in BaseProgram.stream_list:
                compare = BaseProgram.stream_list[name]["inventory"]

                diff_ = []
                for item in compare:
                    if item in char_inv:
                        for diff in list(dictdiffer.diff(compare[item], char_inv[item])):       
                            print(f"{item}: ", diff)
                            if diff:
                                diff_.append(item)
                    else:
                        print(f"{item} is gone!")

                BaseProgram.stream_list[name]["time"] = current_time
                BaseProgram.stream_list[name]["inventory"] = char_inv
                
                if diff_:
                    print(diff_)
                else:
                    print("No difference")
                print("Character saved to stream list")
                self.file_save()

        self.git_save("streams")
        


    def convert_form(self, dict_):
        data = {}
        for i in dict_:
            data[i["strName"]] = i
        return data
