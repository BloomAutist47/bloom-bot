
import re

from .Base import *
from discord.ext import commands
from ast import literal_eval

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from pytz import timezone

class CharacterCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot

        self.weapon_type = ["Axe", "Bow", "Dagger", "Gun", "Mace", "Polearm", "Staff", "Sword", "Wand"]
        self.house_items = ["Wall Item", "Floor Item"]
        self.miscs = ["Quest Item", "Item"]
        
        self.getting_the_good_shit = False
        
        self.faction_link = {
            "Good": "http://aqwwiki.wikidot.com/good-faction",
            "Evil": "http://aqwwiki.wikidot.com/evil-faction",
            "Chaos": "http://aqwwiki.wikidot.com/chaos-faction",
        }
        

    async def multiple_reactions(self, embed_object):
        await embed_object.add_reaction(emoji = "\U0001F9D8") # Classes
        await embed_object.add_reaction(emoji = "\U00002694") # Swords
        await embed_object.add_reaction(emoji = "\U0001F6E1") # Armors
        await embed_object.add_reaction(emoji = "\U0001FA96") # Helm
        await embed_object.add_reaction(emoji = "\U0001F3F4") # Cape
        await embed_object.add_reaction(emoji = "\U0001F415") # Pet
        await embed_object.add_reaction(emoji = "\U0001F392") # Misc Items
        await embed_object.add_reaction(emoji = "\U0001F3C6") # Misc Items
        return

    def search_ccid(self, sites_soup):
        return re.search("var ccid = [\d]+;", sites_soup.find_all("script")[-2].text)[0][11:-1]

    @commands.command()
    async def ioda(self, ctx, *, char_name=""):
        
        url = self.convert_aqurl(char_name)
        sites_soup = await self.get_site_content(URL=url)

        try:
            ccid = self.search_ccid(sites_soup)
        except:
            try:
                result = sites_soup.find("div", {"class": "card-body"}).find("p").text
                result = result.replace("Disabled", "**Disabled**").replace("wandering", "**wandering**")
                result += f" [Click Here]({url}) to go to their Character Page."
                embedVar = self.embed_single("Ioda Calculations", result)
                embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
                await ctx.send(embed=embedVar)
                return
            except:
                embedVar = self.embed_single("Ioda Calculations", "No Character of that name")
                embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
                await ctx.send(embed=embedVar)
                return

        char_full_name = sites_soup.find("div", {"class":"text-dark"}).find("div", {"class":"card-header"}).find("h1").text

        # Inventory stuffs
        char_inv_url = "https://account.aq.com/CharPage/Inventory?ccid="+ccid
        char_inv = await self.get_site_content(char_inv_url)
        print("here")
        char_inv = char_inv.find("body").text[1:-1].replace("false", "False").replace("true", "True")
        char_inv = literal_eval(char_inv)


        for i in char_inv:
            if i["strName"] == "Treasure Potion":
                count = i["intCount"]
                break
            else:
                count = 0
        potion_count = count
# 🔷
        embedVar = discord.Embed(title="Ioda Calculations", color=BaseProgram.block_color,
                        description=f"Name: [**{char_full_name}**]({url})\nTreasure Potions: **{potion_count}**")
        embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)

        if potion_count >= 1000:
            embedVar.set_footer(text="Note:\n"\
                "> Without 50% bonus, 40,000 ACs are\nequal to $100.")
            embedVar.description += "\n*Account ready to __**Get an Ioda**__*."
            await ctx.send(embed=embedVar)
            return

        # Two treasure potions
        tp_two_spins = round(((1000-potion_count)/2))
        tp_two_spins_ac = round(tp_two_spins*200)

        tp_mem_two_days = round((1000 - potion_count) / (8*2) * 7)
        tp_mem_two_weeks = round(tp_mem_two_days/7, 1)
        tp_mem_two_months = round(tp_mem_two_days/30) 
        tp_mem_two_date = (date.today() + timedelta(days=tp_mem_two_days)).strftime("%a, %d %B %Y")

        tp_non_two_days = round((1000 - potion_count) / (1*2) * 7)
        tp_non_two_weeks = round(tp_non_two_days/7, 1)
        tp_non_two_months = round(tp_non_two_days/30) 
        tp_non_two_date = (date.today() + timedelta(days=tp_non_two_days)).strftime("%a, %d %B %Y")

        # print(f"Treasure Potion: {potion_count}\nUsing Acs Spins: {tp_two_spins} ({tp_two_spins_ac} ACs)\t\n"\
        #       f"2TP/Spin Mem days: {tp_mem_two_days}\t\tDate: {tp_mem_two_date}\n"\
        #       f"2TP/Spin Non-Mem days: {tp_non_two_days}\t\tDate: {tp_non_two_date}\n"\
        #        )


        # six treasure potions
        tp_six_spins = round(((1000-potion_count)/6))
        tp_six_spins_ac = round(tp_six_spins*200)

        tp_mem_six_days = round((1000 - potion_count) / (8*6) * 7)
        tp_mem_six_weeks = round(tp_mem_six_days/7, 1)
        tp_mem_six_months = round(tp_mem_six_days/30) 
        tp_mem_six_date = (date.today() + timedelta(days=tp_mem_six_days)).strftime("%a, %d %B %Y")

        tp_non_six_days = round((1000 - potion_count) / (1*6) * 7)
        tp_non_six_weeks = round(tp_non_six_days/7, 1)
        tp_non_six_months = round(tp_non_six_days/30) 
        tp_non_six_date = (date.today() + timedelta(days=tp_non_six_days)).strftime("%a, %d %B %Y")

        # <:ACtagged:622978586160136202>
        inline = True
        embedVar.add_field(name="\n`2 Treasure Potions per Spin`", inline=inline, 
            value=""\
                  f"**With ACs 💰**\n"\
                  f"➣ **Spins**: {tp_two_spins} ({tp_two_spins_ac:,} ACs)\n\n"
                   "**With Member Daily Spin 📅**\n"\
                  f"➣ **Days**: {tp_mem_two_days} ({tp_mem_two_weeks} W/ {tp_mem_two_months} M)\n➣ **Due**: {tp_mem_two_date}\n\n"\
                   "**With Non-Mem Weekly Spin 📅**\n"\
                  f"➣ **Days**: {tp_non_two_days} ({tp_non_two_weeks} W/ {tp_non_two_months} M)\n➣ **Due**: {tp_non_two_date}"\
            )

        embedVar.add_field(name="\u200b", inline=inline, value="\u200b")

        embedVar.add_field(name="\n`6 Treasure Potions per Spin`", inline=inline,
            value=""\
                  f"**With ACs 💰**\n"\
                  f"➣ **Spins**: {tp_six_spins} ({tp_six_spins_ac:,} ACs)\n\n"\
                   "**With Member Daily Spin 📅**\n"\
                  f"➣ **Days**: {tp_mem_six_days} ({tp_mem_six_weeks} W/ {tp_mem_six_months} M)\n➣ **Due**: {tp_mem_six_date}\n\n"\
                   "**With Non-Mem Weekly Spin 📅**\n"\
                  f"➣ **Days**: {tp_non_six_days} ({tp_non_six_weeks} W/  {tp_non_six_months} M)\n➣ **Due**: {tp_non_six_date}\n\n"
            )

        embedVar.set_footer(text="Note:\n"\
            "> 6 Treasure Potion math is made assuming the Player does NOT receive any drop.\n"\
            "> Without 50% bonus, 40,000 ACs are equal to $100. ")


        await ctx.send(embed=embedVar)
        return

    @commands.command()
    async def char(self, ctx, *, char_name=""):
        url = self.convert_aqurl(char_name)
        sites_soup = await self.get_site_content(url)
        try:
            ccid = self.search_ccid(sites_soup)
        except:
            try:
                result = sites_soup.find("div", {"class": "card-body"}).find("p").text
                result = result.replace("Disabled", "**Disabled**").replace("wandering in the Void", "**wandering in The Void**").replace("frozen solid", "**Frozen solid**").replace("Deleted", "**Deleted**").replace("our","AQW's")
                result += f" [Click Here]({url}) to go to their Character Page."
                await ctx.send(embed=self.embed_single("Character Profile Result", result))
                return
            except:
                await ctx.send(embed=self.embed_single("Character Profile Result", "No Character of that name"))

        body = sites_soup.find("div", {"class":"text-dark"})
        char_full_name = body.find("div", {"class":"card-header"}).find("h1").text

        # Character Details
        body_details = body.find("div", {"class": "card-body"}).find("div", {"class":"row"})
        defaults = {
            "Level": "", "Class": "", "Weapon": "", "Armor": "", "Helm": "", "Cape": "",
            "Pet": "", "Faction": "", "Guild": ""
        }

        char_details_raw = [x.text for x in body_details.select("div.col-12.col-md-6")]
        char_details = {}
        for i in char_details_raw:
            item = [x.lstrip() for x in i.split("\n")[1:-1]]
            for cat in item:
                x = cat.split(":")
                char_details[x[0]] = x[1]


        for i in defaults:
            if i not in char_details:
                char_details[i] = ""

        # Inventory stuffs
        char_inv_url = "https://account.aq.com/CharPage/Inventory?ccid="+ccid
        char_inv = await self.get_site_content(char_inv_url)
        char_inv = char_inv.find("body").text[1:-1].replace("false", "False").replace("true", "True")
        char_inv = literal_eval(char_inv)

        item_count = {"Weapon": 0, "House Item": 0, "Misc": 0}
        for item in char_inv:
            item_type = item["strType"]
            if item_type in self.weapon_type:
                item_count["Weapon"] += 1
                continue
            if item_type in self.miscs:
                item_count["Misc"] += 1
                continue
            if item_type not in item_count and item_type:
                item_count[item_type] = 0
            item_count[item_type] += 1

        item_default = ['Armor', 'Cape', 'Class', 'Floor Item', 'Helm',
            'House', 'House Item', 'Misc', 'Necklace', 'Pet',
            'Wall Item', 'Weapon']

        for item in item_default:
            if item not in item_count:
                item_count[item] = 0

        fac = char_details['Faction'].strip()
        if fac not in self.faction_link:
            faction_link = "http://aqwwiki.wikidot.com/"
        else:
            faction_link = self.faction_link[fac]

        # Inserts stuffs
        link_name = self.convert_aqurl(char_full_name)
        embedVar = discord.Embed(title="Character Profile", color=BaseProgram.block_color)
        embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
        char_full_text = f"Name: [{char_full_name}]({link_name})"

        guild_dat = f"Guild: {char_details['Guild']}"
        guild_length = f"{guild_dat}".ljust(30, "")
        guild_length = guild_length.replace(f"{guild_dat}", "")
        print(guild_length)

        link_class = self.convert_aqurl(char_details['Class'], mode="wiki")
        panel_1_raw = [char_full_text + "\n",
                f"Level: [{char_details['Level']}](http://aqwwiki.wikidot.com/exp-class-points-rep)" + "\n",
                f"Class: [{char_details['Class']}]({link_class})" + "\n",
                f"Faction: [{char_details['Faction']}]({faction_link})" + "\n",
                f"Guild: [{char_details['Guild']}](https://www.aq.com/lore/guilds)" + guild_length,
                ]

        link_weapon = self.convert_aqurl(char_details['Armor'], mode="wiki")
        link_armor = self.convert_aqurl(char_details['Armor'], mode="wiki")
        link_helm = self.convert_aqurl(char_details['Helm'], mode="wiki")
        link_cape = self.convert_aqurl(char_details['Cape'], mode="wiki")
        link_pet = self.convert_aqurl(char_details['Pet'], mode="wiki")

        panel_2 = f"Weapon: [{char_details['Weapon']}]({link_weapon})\n"\
                f"Armor: [{char_details['Armor']}]({link_armor})\n"\
                f"Helm: [{char_details['Helm']}]({link_helm})\n"\
                f"Cape: [{char_details['Cape']}]({link_cape})\n"\
                f"Pet: [{char_details['Pet']}]({link_pet})"

        vl = 25
        inventories_ =["```css\n",
                      f"Classes: {item_count['Class']}".ljust(vl) + f"Miscs: {item_count['Misc']}\n",
                      f"Weapons: {item_count['Weapon']}".ljust(vl) + f"Pets: {item_count['Pet']}\n",
                      f"Armors: {item_count['Armor']}".ljust(vl) + f"Houses: {item_count['House']}\n",
                      f"Helms: {item_count['Helm']}".ljust(vl) + f"Wall Items: {item_count['Wall Item']}\n",
                      f"Capes: {item_count['Cape']}".ljust(vl) + f"Floor Items: {item_count['Floor Item']}```\n",
                      ]
        panel_1 = ""
        for i in panel_1_raw:
            panel_1 += i

        inventories_2 = ""
        for i in inventories_:
            inventories_2 += i

        embedVar.add_field(name="Data", value=panel_1, inline=True)
        embedVar.add_field(name="Equips", value=panel_2, inline=True)
        embedVar.add_field(name="Inventory", value=inventories_2, inline=False)

        embed_object = await ctx.send(embed=embedVar)
        return

    @commands.command()
    async def server(self, ctx):
        self.est_dt = datetime.now(timezone('est'))
        current_time = self.est_dt.strftime("Server Time: %d %B %Y, %I:%M %p")

        url = "https://game.aq.com/game/cf-serverlist.asp"

        count = 0
        data = {}
        desc = ""
        sites_soup = await self.get_site_content(url, parser="html.parser")
        servers = sites_soup.find_all("servers")

        
        total_players = 0
        print("indeed")
        for i in servers:
            ct = int(i["icount"])
            total_players += ct
            data[ct] = i["sname"]

        embedVar = discord.Embed(title=f"🌎 Server Info", description=f"{total_players} Players online", color=BaseProgram.block_color)

        for i in sorted(data.keys(), reverse=True):
            if count == 7:
                embedVar.add_field(name="🖼️ Server", value=desc, inline=True)
                embedVar.add_field(name="\u200b", value="\u200b", inline=True)
                desc = ""
            desc += f'{data[i]}: **{str(i)}**\n'
            count += 1
        embedVar.add_field(name=f"🖼️ Server", value=desc, inline=True)
        print("yes?")
        embedVar.set_author(name="AdventureQuest World", icon_url=BaseProgram.icon_aqw)
        embedVar.set_thumbnail(url="https://cdn.discordapp.com/attachments/805367955923533845/813412831651168266/beleen-youve-got-mail-new-adventure-quest-worlds-aqw-newsletter.png")
        embedVar.set_footer(text=current_time)
        await ctx.send(embed=embedVar)

    # @commands.command()
    # async def charinv(self, ctx):
    #     url = self.char_url + char_name.replace(" ", "+")
    #     sites_soup = await self.get_site_content(url)
    #     try:
    #         ccid = re.search("var ccid = [\d]+;", sites_soup.find_all("script")[-2].text)[0][11:-1]
    #     except:
    #         try:
    #             result = sites_soup.find("div", {"class": "card-body"}).find("p").text
    #             result = result.replace("Disabled", "**Disabled**").replace("wandering", "**wandering**")
    #             result += f" [Click Here]({url}) to go to their Character Page."
    #             await ctx.send(embed=self.embed_single("Character Profile Result", result))
    #             return
    #         except:
    #             await ctx.send(embed=self.embed_single("Character Profile Result", "No Character of that name"))

    #     embedVar = discord.Embed(title="Character Profile Help", color=BaseProgram.block_color)

    #     # Get Badges
    #     char_badge_url = "https://account.aq.com/CharPage/Badges?ccid="+ccid
    #     char_badges = self.get_site_content(char_badge_url).find("body").text[1:-1]
    #     char_badges = literal_eval(char_badges)

    #     # Get Inventory
    #     char_inv_url = "https://account.aq.com/CharPage/Inventory?ccid="+ccid
    #     char_inv_raw = await self.get_site_content(char_inv_url)
    #     char_inv = char_inv_raw.find("body").text[1:-1].replace("false", "False").replace("true", "True")
    #     char_inv = literal_eval(char_inv)

    #     # Categorize the items
    #     items = {}
    #     for item in char_inv:
    #         item_type = item["strType"]
    #         if item_type not in items:
    #             items[item_type] = []
    #         items[item_type].append(item)

    #     

    #     await ctx.send(embed=embedVar)
    #     return