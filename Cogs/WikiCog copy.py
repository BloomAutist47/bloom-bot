import re

from .Base import *
from discord.ext import commands
from pprintpp import pprint
import html2text
import textwrap

class WikiCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot
        self.field_count = 0
        self.black_listed = "Tercessuinotlim"

    # @commands.command()
    # async def ws(self, ctx, *, item=""):
    #     if item == "":
    #         embedVar = self.embed_single("Wiki Search", "Please enter a value.")
    #         await ctx.send(embed=embedVar)F
    #         return



    #     wiki = self.convert_aqurl(item, "wikisearch")


    #     result_desc = ""
    #     wiki_soup = await self.get_wiki_search_content(wiki)
        

    #     if wiki_soup == "shit":
    #         result_desc = "Timeout error. The wikidot fucked up. Not me."
    #     elif not wiki_soup:
    #         result_desc = "None"
    #     else:
    #         for item in wiki_soup:
    #             re_name = item.find("div", {"class":"title"}).find("a").text.strip()
    #             link = item.find("div", {"class":"title"}).find("a")["href"]
    #             result_desc += f"➣ [{re_name}]({link})\n"

    #     embedVar = self.embed_single("Wiki Search", wiki)
    #     embedVar.add_field(name="Top Result", value=result_desc, inline=False)
    #     embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
    #     await ctx.send(embed=embedVar)
    #     return



    @commands.command()
    async def w(self, ctx, *, item=""):
        if item == "":
            embedVar = self.embed_single("Wiki Search", "Please enter a value.")
            await ctx.send(embed=embedVar)
            return

        self.loop.create_task(self.basic_search(ctx, item))

    async def basic_search(self, ctx, item):
        # convert item into something useful
        item =  re.sub(' +', ' ', item)
        item = re.sub(r"(\`)|(\))|(\()|(\+)|(\.)", "", item)
        item = re.sub(r"(\')|(\s)", "-", item).lower()

        paged = "http://aqwwiki.wikidot.com/"+ item
        wikid = "http://aqwwiki.wikidot.com/search:site/q/" + item.replace("-", "%20")
        print("SITE: ", paged)
        sites_soup = await self.get_site_content(paged)
        page_content = sites_soup.find("div", {"id":"page-content"})
        
        refer_list = ""

        try:
            page_check = page_content.text.strip()
        except Exception as e:
            await ctx.send(f"\> **Exception**: {e}. Please try writing the correct name search. \n\> **Note:**: This feature is still on beta.")
            return  
        if "This page doesn't exist yet" in page_check:
            print("page doesn't exists")
            result = await self.get_wiki_search(wikid)

            if not result:
                embedVar = discord.Embed(title="Wiki Search", color=BaseProgram.block_color,
                    description="Sorry, nothing came up with your search.")
                await ctx.send(embed=embedVar)
                return

            embedVar = discord.Embed(title="Wiki Search", color=BaseProgram.block_color,
                description="Sorry, no result came up. Maybe one of these?")
            desc = ""
            for item in result:
                desc += item
            embedVar.add_field(name="Top Result", value=desc, inline=False)
            embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
            await ctx.send(embed=embedVar)
            return

        elif "usually refers to" in page_check:
            refer_content = page_content.find_all("a")
            refer_list = '\n'.join([f"➣ __[Link](http://aqwwiki.wikidot.com{x['href']})__ `{x.text.strip()}`    " for x in refer_content])

            sites_soup = await self.get_site_content("http://aqwwiki.wikidot.com/" + refer_content[0]["href"])
            page_content = sites_soup.find("div", {"id":"page-content"})

            print("usually refers")
            result = self.get_wiki_page(sites_soup, page_content)
        else:
            result = self.get_wiki_page(sites_soup, page_content)
        pprint(result)

        # embed for true stuffs
        data = result["data"]
        note_storage = ""
        also_storage = ""
        embedVar = discord.Embed(title=result["title"], color=BaseProgram.block_color,
            url=paged)

        embedVar.add_field(name="All Result:", value=f"[Click here for all Results]({wikid})", inline=True)
        # result["breadcrumbs"] = [f"[{x}](http://aqwwiki.wikidot.com/{x})" for x in result["breadcrumbs"]]
        embedVar.add_field(name="Section:", value=f" » ".join(result["breadcrumbs"]), inline=False)
        # embedVar.add_field(name="\u200b", value="\u200b", inline=False)
        if refer_list:
            embedVar.add_field(name="Search Usually refer to:", value=refer_list, inline=False)
            # legend specialoffer rare ac pseudo-rare seasonal
        if result["tags"]:
            tag_ = result["tags"]
            if "ac" in tag_:
                ac = discord.utils.get(self.bot.emojis, name='tagAC')
                embedVar.title = embedVar.title + f" {ac}"
            if "specialoffer" in tag_:
                ac = discord.utils.get(self.bot.emojis, name='tagSpecialOffer')
                embedVar.title = embedVar.title + f" {ac}"
            if "pseudo-rare" in tag_:
                ac = discord.utils.get(self.bot.emojis, name='tagPseudoRare')
                embedVar.title = embedVar.title + f" {ac}"
            if "legend" in tag_:
                ac = discord.utils.get(self.bot.emojis, name='tagLegend')
                embedVar.title = embedVar.title + f" {ac}"
            if "seasonal" in tag_:
                ac = discord.utils.get(self.bot.emojis, name='tagSeasonal')
                embedVar.title = embedVar.title + f" {ac}"
            if "rare" in tag_:
                ac = discord.utils.get(self.bot.emojis, name='tagRare')
                embedVar.title = embedVar.title + f" {ac}"

        # Data
        fc = 0
        if "Description:" in data and data["Description:"]:
            embedVar.add_field(name="Description:", value=self.combine_str(data["Description:"]), inline=False)

        if "Price:" in data and data["Price:"]:
            
            res = self.combine_lst_str(data["Price:"])
            for item in res:
                if fc == 2:
                    fc = 0
                    embedVar.add_field(name="\u200b", value="\u200b", inline=True)
                if len(item) <= 5:
                    print(len(item))
                    embedVar.add_field(name="Price:", value='\n '.join(item), inline=True)
                else:
                    embedVar.add_field(name="Price:", value=self.combine_list(item, "➣"), inline=True)
                fc += 1

        if "Sellback:" in data and data["Sellback:"]:
            if fc == 2:
                fc = 0
                embedVar.add_field(name="\u200b", value="\u200b", inline=True)
            embedVar.add_field(name="Sellback:", value='\n'.join(data["Sellback:"]), inline=True)
            fc += 1
        if "Weapon Damage:" in data and data["Weapon Damage:"]:
            if fc == 2:
                fc = 0
                embedVar.add_field(name="\u200b", value="\u200b", inline=True)
            embedVar.add_field(name="Weapon Damage:", value='\n'.join(data["Weapon Damage:"]), inline=True)
            fc += 1
        if "Base Level:" in data and data["Base Level:"]:
            if fc == 2:
                fc = 0
                embedVar.add_field(name="\u200b", value="\u200b", inline=True)
            embedVar.add_field(name="Base Level:", value='\n'.join(data["Base Level:"]), inline=True)
            fc += 1
        if "Rarity:" in data and data["Rarity:"]:
            if fc == 2:
                fc = 0
                embedVar.add_field(name="\u200b", value="\u200b", inline=True)
            embedVar.add_field(name="Rarity:", value='\n'.join(data["Rarity:"]), inline=True)
            fc += 1

        if "Locations:" in data and data["Locations:"]:
            res = self.combine_lst_str(data["Locations:"])
            for item in res:
                if fc == 2:
                    fc = 0
                    embedVar.add_field(name="\u200b", value="\u200b", inline=True)

                if len(item) <= 5:
                    embedVar.add_field(name="Locations:", value='\n '.join(item), inline=True)
                else:
                    embedVar.add_field(name="Locations:", value=self.combine_list(item, "➣"), inline=True)
                fc += 1
        if "Location:" in data and data["Location:"]:
            res = self.combine_lst_str(data["Location:"])
            for item in res:
                if fc == 2:
                    fc = 0
                    embedVar.add_field(name="\u200b", value="\u200b", inline=True)

                if len(item) <= 5:
                    embedVar.add_field(name="Locations:", value='\n '.join(item), inline=True)
                else:
                    embedVar.add_field(name="Locations:", value=self.combine_list(item, "➣"), inline=True)
                fc += 1
        if "Rooms:" in data and data["Rooms:"]:
            if fc == 2:
                fc = 0
                embedVar.add_field(name="\u200b", value="\u200b", inline=True)
            embedVar.add_field(name="Rooms:", value='\n'.join(data["Rooms:"]), inline=True)
            fc += 1

        if "SpecialEffects:" in data and data["SpecialEffects:"]:
            embedVar.add_field(name="Special Effects:", value=''.join(data["SpecialEffects:"]), inline=False)
        if "Special Effects:" in data and data["Special Effects:"]:
            embedVar.add_field(name="Special Effects:", value=''.join(data["Special Effects:"]), inline=False)
        if "Shops:" in data and data["Shops:"]:
            res = self.combine_lst_str(data["Shops:"])
            for item in res:
                embedVar.add_field(name="Shops:", value=self.combine_list(item, "➣"), inline=False)
        if "Quests:" in data and data["Quests:"]:
            res = self.combine_lst_str(data["Quests:"])
            for item in res:
                embedVar.add_field(name="Quests:", value=self.combine_list(item, "➣"), inline=False)
        if "AI:" in data and data["AI:"]:
            res = self.combine_lst_str(data["AI:"])
            for item in res:
                embedVar.add_field(name="AI:", value=self.combine_list(item, "➣"), inline=False)
        if "NPCs:" in data and data["NPCs:"]:
            res = self.combine_lst_str(data["NPCs:"])
            for item in res:
                embedVar.add_field(name="NPCs:", value=self.combine_list(item, "➣"), inline=False)
        if "Monsters:" in data and data["Monsters:"]:
            res = self.combine_lst_str(data["Monsters:"])
            for item in res:
                embedVar.add_field(name="Monsters:", value=self.combine_list(item, "➣"), inline=False)
        if "Access Points:" in data and data["Access Points:"]:
            res = self.combine_lst_str(data["Access Points:"])
            for item in res:
                embedVar.add_field(name="Access Points:", value=self.combine_list(item, "➣"), inline=False)

        if "Note:" in data: note_storage = data["Note:"]
        if "Also see:" in data: also_storage = data["Also see:"]



        list_ = ["SpecialEffects:","Special Effects:", "Access Points:", "AI:", "Rooms:", "Base Level:","Monsters:", "NPCs:", "Rarity:", "Quests:", "Shops:", "Locations:", "Location:", "Description:", "Price:", "Sellback:", "Weapon Damage:", "Note:", "Also see:"]
        for key in list_:
            data.pop(key, None)

        # loops through remaining shit
        for item_name in data:
            if data[item_name] == []:
                continue
            if fc == 2:
                fc = 0
                embedVar.add_field(name="\u200b", value="\u200b", inline=True)
            embedVar.add_field(name=item_name, value='\n'.join(data[item_name]), inline=True)
            fc += 1

        if note_storage and result["title"] not in self.black_listed:
            res = self.combine_lst_str(note_storage)
            for item in res:
                embedVar.add_field(name="Note:", value=self.combine_list(item, "➣"), inline=False)
        if also_storage:
            res = self.combine_lst_str(also_storage)
            for item in res:
                embedVar.add_field(name="Also See:", value=self.combine_list(item, "➣"), inline=False)

        if result["image"]:
            embedVar.set_image(url=result["image"])
        if "tags" in result:
            tag_str = ", ".join(result["tags"])
            embedVar.set_footer(text="Tags: " + tag_str)
        if "breadcrumbs" in result:
            embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
            # embedVar.set_author(name=" > ".join(result["breadcrumbs"]))

        await ctx.send(embed=embedVar)
        # return {"title": title, "data": data, "breadcrumbs": breadcrumbs, "tags": tags, "image": image}
        return

    def add_category(self, category):
        if "Locations:" in data and data["Locations:"]:
            res = self.combine_lst_str(data["Locations:"])
            for item in res:
                if fc == 2:
                    fc = 0
                    embedVar.add_field(name="\u200b", value="\u200b", inline=True)

                if len(item) <= 5:
                    embedVar.add_field(name="Locations:", value='\n '.join(item), inline=True)
                else:
                    embedVar.add_field(name="Locations:", value=self.combine_list(item, "➣"), inline=True)
                fc += 1

    def get_wiki_page(self, sites_soup, page_content):
        title = sites_soup.find("div", {"id":"main-content"}).find("div", {"id": "page-title"}).text.strip()
        main_page = sites_soup.find("div", {"id":"main-content"})
        breadcrumbs = [f"[{x.text.strip()}](http://aqwwiki.wikidot.com{x['href']})" for x in main_page.find("div", {"id":"breadcrumbs"}).find_all("a")][1:]


        tags = [x.text.strip() for x in main_page.find("div", {"class":"page-tags"}).find("span").find_all("a")]
        # legend specialoffer rare ac pseudo-rare seasonal

        note = ""
        data = {}
        also_see = ""

        # Get image part
        image = self.get_wiki_image(sites_soup)
        if image and "aclarge.png" in image:
            image = None

        for div in page_content.find_all("span", {'style':'text-decoration: line-through;'}): 
            div.decompose()
        for div in page_content.find_all("span", {'style':'font-size:x-small;'}): 
            div.decompose()
        for div in page_content.find_all("div", {'class':'yui-navset'}): 
            div.decompose()
        for div in page_content.find_all("span", {'style':'font-size:60%;'}): 
            div.decompose()
        for div in page_content.find_all("img", {'alt':'raresmall.png'}): 
            div.parent.decompose()
        if "Classes" in breadcrumbs:
            for div in page_content.find_all("div", {'class':'skills'}): 
                div.decompose()


        # Remove unnecessary parts
        for x in page_content.find_all():
            cond = x.get_text(strip=True)
            if len(cond) == 0 or cond == "*":
                x.extract()
        data_ = html2text.html2text(str(page_content))
        data_ = data_.replace("\n", " ")
        data_list = data_

        # Get note part
        if "**Notes:**" in data_:
            data_list = data_.split("**Notes:**")[0]
            note = re.findall("(\*\*Notes:\*\*.+)", data_)
            if note:
                note = [x.strip() for x in note[0].strip().split("*") if x.strip() != "" and x.strip() != "Notes:"]
                for ind in range(len(note)):
                    note[ind] = note[ind].replace("](/","](http://aqwwiki.wikidot.com/")

                if "Also see:" in note:
                    as_ind = note.index("Also see:")
                    also_see = note[as_ind+1:]
                    note = note[:as_ind]
                if "Also see" in note:
                    as_ind = note.index("Also see")
                    also_see = note[as_ind+1:]
                    note = note[:as_ind]

        # Get data list
        data_list = [x.strip() for x in re.split("\*\*(.+?)\*\*", data_list) if x != ""]
        for category,value in zip(data_list[0::2], data_list[1::2]):
            list_result = [x.strip() for x in value.split("*") if x != ""]

            for ind in range(len(list_result)):
                list_result[ind] = re.sub("(\-\s)", "-", list_result[ind].replace("](/","](http://aqwwiki.wikidot.com/"))
            data[category] = list_result

        if note:
            data["Note:"] = note
            if also_see:
                data["Also see:"] = also_see


        return {"title": title, "data": data, "breadcrumbs": breadcrumbs, "tags": tags, "image": image}


    async def get_wiki_search(self, wikid):

        wiki_soup = await self.get_site_content(wikid)
        sites_soup = wiki_soup.find("div", {"id":"page-content"})
        wiki_box = sites_soup.find("div", {"class":"search-box"})

        page_check = wiki_box.text.strip()
        if "Sorry, no results found for your query." in page_check:
            return None
        
        
        if not wiki_box:
            return "shit"
        elif "Sorry, no results found for your query." in wiki_box.text.strip():
            return None
        else:
            page_content = sites_soup.find("div", {"class":"search-results"}).find_all("div", {"class":"title"})
            result = []
            for item in page_content:
                item_ = item.find("a")
                result.append(f"➣ [__Link__]({item_['href']}) `{item_.text.strip()}` \n")
            return result

    def get_wiki_image(self, soup_item):

        try:
            images = soup_item.find_all("img", {"class":"image"})
            for img in images:
                if "http://i.imgur.com/" in img["src"] or "https://i.imgur.com" in img["src"]:
                    if "aclarge.png" in img["src"]:
                        continue
                    print(img["src"])

                    return img["src"]
        except:
            pass

        try:
            image = soup_item.find_all("div", {"class":"yui-content"}).find_all("img")[-1]["src"]
            images = self.check_stuff(image)
            return images
        except: pass

        try:
            image = soup_item.find_all("img")[-1]["src"]
            images = self.check_stuff(image)
            # print(images)
            return images
        except:
            pass
        return None

    def combine_lst_str(self, list_):
        res = 0
        lis_ = []
        result = []
        for item in list_:
            if res >= 900:
                result.append(lis_)
                lis_ = []
                res = 0
            res += len(item)
            lis_.append(item)
        result.append(lis_)
        return result

    def combine_str(self, list_):
        result = ""
        for item in list_:
            result += f" {item} "
        return result

    def combine_list(self, list_, mark):
        result = ""
        for item in list_:
            if item.strip() == ".":
                continue
            result += f"{mark} {item}\n"
        return result

    def check_http(self, image_url):
        if "https" not in image_url:
            return image_url.replace("http:", "https:")
        return image_url




                    # if "ac_tag" in data:
                    #     if data["ac_tag"] == True:
                    #         ac = discord.utils.get(self.bot.emojis, name='tagAC')
                    #         embedVar.title = embedVar.title + f" {ac}"

                    # if "special_tag" in data:
                    #     if data["special_tag"] == True:
                    #         ac = discord.utils.get(self.bot.emojis, name='tagSpecialOffer')
                    #         embedVar.title = embedVar.title + f" {ac}"
                    # if "pseudo_tag" in data:
                    #     if data["pseudo_tag"] == True:
                    #         ac = discord.utils.get(self.bot.emojis, name='tagPseudoRare')
                    #         embedVar.title = embedVar.title + f" {ac}"
                    # if "legend_tag" in data:
                    #     if data["legend_tag"] == True:
                    #         ac = discord.utils.get(self.bot.emojis, name='tagLegend')
                    #         embedVar.title = embedVar.title + f" {ac}"

                    # if "seasonal_tag" in data:
                    #     if data["seasonal_tag"] == True:
                    #         ac = discord.utils.get(self.bot.emojis, name='tagSeasonal')
                    #         embedVar.title = embedVar.title + f" {ac}"

                    # if "rare_Tag" in data:
                    #     if data["rare_Tag"] == True:
                    #         ac = discord.utils.get(self.bot.emojis, name='tagRare')
                    #         embedVar.title = embedVar.title + f" {ac}"



