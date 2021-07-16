import re

from .Base import *
from discord.ext import commands
from pprintpp import pprint
import html2text

class WikiCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot
        self.field_count = 0

    @commands.command()
    async def w(self, ctx, *, item=""):
        if item == "":
            embedVar = self.embed_single("Wiki Search", "Please enter a value.")
            await ctx.send(embed=embedVar)
            return
        item = item.lower().replace(".", "").replace("+", "").replace("'", "")

        straight = self.convert_aqurl(item, "wiki")
        print(straight)
        wiki = self.convert_aqurl(item, "wikisearch")

        only_wiki = False
        true_item = False
        text_content = False
        sites_soup = await self.get_site_content(straight)
        # pprint(sites_soup)
        wiki_soup_site = ""

        try:
            title = sites_soup.find("div", {"id":"main-content"}).find("div", {"id": "page-title"}).text.strip()
            page_content = sites_soup.find("div", {"id":"page-content"})
            page_check = page_content.find("p").text.strip()
            if page_check == "This page doesn't exist yet!":
                # Empty
                title = ""
                result = wiki
                image = None
                only_wiki = True
            elif "usually refers to:" in page_check:
                refer_content = page_content.find_all("a")
                text_content = '\n'.join([f"➣ [{x.text.strip()}](http://aqwwiki.wikidot.com+{x['href']})" for x in refer_content])
                pprint("WHUTS")
                # Referals
                title = sites_soup.find("div", {"id":"main-content"}).find("div", {"id": "page-title"}).text.strip()
                result = straight
                first_refer = "http://aqwwiki.wikidot.com/" + page_content.find_all("a")[0]["href"]
                fr_sites_soup = await self.get_site_content(first_refer)
                fr_page_content = fr_sites_soup.find("div", {"id":"page-content"})
                image = self.get_image_wiki(fr_page_content)
                only_wiki = False

                if fr_page_content:
                    true_item = True
                    sites_soup = fr_sites_soup

            else:
                # True Item
                title = sites_soup.find("div", {"id":"main-content"}).find("div", {"id": "page-title"}).text.strip()
                result = straight
                image = self.get_image_wiki(page_content)
                only_wiki = False
                true_item = True
        except:
            # Search
            title = ""
            result = wiki
            image = None
            only_wiki = True

        if only_wiki:
            result_desc = ""
            wiki_soup = await self.get_wiki_search_content(result)

            if wiki_soup == "shit":
                result_desc = "Timeout error. The wikidot fucked up. Not me."
            elif not wiki_soup:
                result_desc = "None"
            else:
                for item in wiki_soup:
                    re_name = item.find("div", {"class":"title"}).find("a").text.strip()
                    link = item.find("div", {"class":"title"}).find("a")["href"]
                    result_desc += f"➣ [{re_name}]({link})\n"
            
        if not only_wiki:
            embedVar = self.embed_single(title, f"{result}" )
            embedVar.add_field(name="All Result", value=f"[Click here for all result]({wiki})", inline=False)

        if only_wiki:
            embedVar = self.embed_single("Wiki Search", f"{result}" )
            embedVar.add_field(name="Top Result", value=result_desc, inline=False)

        if image:
            embedVar.set_thumbnail(url=image)
        if text_content:
            embedVar.add_field(name="Search Usually refers to: ", value=text_content, inline=False)
        no_list = ["note", "descrip", "special effect", "location", "rare_tag","price", "ac_tag", "sellback", "seasonal_tag","special_tag","rarity", "damage", "legend_tag", "pseudo_tag"]
        ac_tagged = False
        cont = False
        field_inline = False
        setup_two = False
        note_storage = ""
        if true_item:
            while True:
                try:
                    # pprint(sites_soup)
                    data = self.new_wiki_content(result, sites_soup)
                except:
                    break
                # print(data)
                if data:
                    for head in data:
                        head_ = head.lower()
                        if setup_two == True:
                            if "note" in head_:
                                note_storage = data[head]
                                break
                            continue


                        if "note" in head_:
                            break
                        if "skills" in head_:
                            setup_two = True
                            break
                        for i in no_list:
                            if i in head_:
                                cont = True
                                break
                        if cont:
                            cont = False
                            continue


                        else:
                            if data[head]:
                                embedVar.add_field(name=head, value=data[head], inline=field_inline)
                        

                    if "Rarity:" in data:
                        # if len(data["Rarity:"]) > 15:
                        embedVar.add_field(name="Rarity:", value=data["Rarity:"], inline=field_inline)
                        # embedVar = self.embed_check(embedVar)

                    if "Base Damage:" in data:
                        embedVar.add_field(name="Base Damage:", value=data["Base Damage:"], inline=field_inline)
                        # embedVar = self.embed_check(embedVar)

                    if "Price:" in data:
                        embedVar.add_field(name="Price:", value=data["Price:"], inline=field_inline)
                        # embedVar = self.embed_check(embedVar)


                    if "Sellback:" in data:
                        embedVar.add_field(name="Sellback:", value=data["Sellback:"], inline=field_inline)
                        # embedVar = self.embed_check(embedVar)

                    if "Locations:" in data:
                        embedVar.add_field(name="Locations:", value=data["Locations:"], inline=field_inline)
                        # embedVar = self.embed_check(embedVar)


                    if "ac_tag" in data:
                        if data["ac_tag"] == True:
                            ac = discord.utils.get(self.bot.emojis, name='tagAC')
                            embedVar.title = embedVar.title + f" {ac}"

                    if "special_tag" in data:
                        if data["special_tag"] == True:
                            ac = discord.utils.get(self.bot.emojis, name='tagSpecialOffer')
                            embedVar.title = embedVar.title + f" {ac}"
                    if "pseudo_tag" in data:
                        if data["pseudo_tag"] == True:
                            ac = discord.utils.get(self.bot.emojis, name='tagPseudoRare')
                            embedVar.title = embedVar.title + f" {ac}"
                    if "legend_tag" in data:
                        if data["legend_tag"] == True:
                            ac = discord.utils.get(self.bot.emojis, name='tagLegend')
                            embedVar.title = embedVar.title + f" {ac}"

                    if "seasonal_tag" in data:
                        if data["seasonal_tag"] == True:
                            ac = discord.utils.get(self.bot.emojis, name='tagSeasonal')
                            embedVar.title = embedVar.title + f" {ac}"

                    if "rare_Tag" in data:
                        if data["rare_Tag"] == True:
                            ac = discord.utils.get(self.bot.emojis, name='tagRare')
                            embedVar.title = embedVar.title + f" {ac}"


                    if "Special Effects:" in data:
                        embedVar.add_field(name="Special Effects:", value=data["Special Effects:"], inline=False)

                    if "Descriptions:" in data:
                        embedVar.add_field(name="Descriptions:", value=data["Descriptions:"], inline=False)

                    if "Description:" in data:
                        embedVar.add_field(name="Description:", value=data["Description:"], inline=False)
     
                    if "Notes:" in data:
                        note_dat = data["Notes:"].split("Male Female")[0]
                        embedVar.add_field(name="Notes:", value=note_dat, inline=False)
                    if "Note:" in data:
                        note_dat = data["Note:"].split("Male Female")[0]
                        embedVar.add_field(name="Note:", value=note_dat, inline=False)
                    if note_storage:
                        note_dat = note_storage.split("Male Female")[0]
                        embedVar.add_field(name="Note:", value=note_dat, inline=False)

                break

        embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
        
        try:
            await ctx.send(embed=embedVar)
        except:
            print("Error, too big I guess", item)

        return

        # while True:
        #     try:
        #         await ctx.send(embed=embedVar)
        #         print(f"> Function send executed...Success!")
        #         break
        #     except:
        #         print(f"> Failed Executing send... Trying again.")
        #         print("> Reloading...")
        #         continue

    @commands.command()
    async def ws(self, ctx, *, item=""):
        if item == "":
            embedVar = self.embed_single("Wiki Search", "Please enter a value.")
            await ctx.send(embed=embedVar)
            return



        wiki = self.convert_aqurl(item, "wikisearch")


        result_desc = ""
        wiki_soup = await self.get_wiki_search_content(wiki)
        

        if wiki_soup == "shit":
            result_desc = "Timeout error. The wikidot fucked up. Not me."
        elif not wiki_soup:
            result_desc = "None"
        else:
            for item in wiki_soup:
                re_name = item.find("div", {"class":"title"}).find("a").text.strip()
                link = item.find("div", {"class":"title"}).find("a")["href"]
                result_desc += f"➣ [{re_name}]({link})\n"

        embedVar = self.embed_single("Wiki Search", wiki)
        embedVar.add_field(name="Top Result", value=result_desc, inline=False)
        embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
        await ctx.send(embed=embedVar)
        return

    async def get_wiki_search_content(self, link):

        wiki_soup = await self.get_site_content(link)
        wiki_content = wiki_soup.find("div", {"id":"page-content"})
        wiki_box = wiki_content.find("div", {"class":"search-box"})
        
        if not wiki_box:
            return "shit"
        elif "Sorry, no results found for your query." in wiki_box.text.strip():
            return None
        else:
            result = wiki_box.find("div", {"class":"search-results"}).find_all("div", {"class":"item"})
            return result


    def new_wiki_content(self, result, sites_soup):
        black_list = ["Cutscene Scripts", "NPC", "Shops", "Maps"]
        check = sites_soup.find("div", {"id":"main-content"}).find("div", {"id":"breadcrumbs"}).text.strip()
        for i in black_list:
            if i in check:
                return None

        page_content = sites_soup.find("div", {"id":"page-content"})

        # Test ac
        data = {}

        # pprint(page_content)

        ac_tag = page_content.find("img", {"alt":"aclarge.png"})
        pseudo_tag = page_content.find("img", {"alt":"pseudolarge.png"})
        special_tag = page_content.find("img", {"alt":"speciallarge.png"})
        legend_tag = page_content.find("img", {"alt":"legendlarge.png"})
        rare_Tag = page_content.find("img", {"alt":"rarelarge.png"})
        seasonal_tag = page_content.find("img", {"alt":"seasonallarge.png"})

        # print(ac_tag)
        if special_tag:
            data["special_tag"] = True
        if ac_tag:
            data["ac_tag"] = True
        if pseudo_tag:
            data["pseudo_tag"] = True
        if legend_tag:
            data["legend_tag"] = True
        if rare_Tag:
            data["rare_Tag"] = True
        if seasonal_tag:
            data["seasonal_tag"] = True


        for div in page_content.find_all("span", {'style':'text-decoration: line-through;'}): 
            div.decompose()
        for div in page_content.find_all("span", {'style':'font-size:x-small;'}): 
            div.decompose()
        for div in page_content.find_all("img", {'alt':'raresmall.png'}): 
            div.parent.decompose()


        for x in page_content.find_all():
            if len(x.get_text(strip=True)) == 0:
                x.extract()
        x = html2text.html2text(str(page_content))
        # pprint(x)
        data_list = x.split("**")[1:]
        data_list = [data.replace("\n", " ") for data in data_list]
        # data_list = re.split(r"(\*\*.+?:\*\*)(.+?[**])", x)

        # data_list = list(filter(None, data_list))
        
        it = iter(data_list)
        for x in it:

            head = x.lower()
            target = next(it)

            # if "skill" in head:
            #     break

            links = re.findall(r"(\(/.+?\))", target)
            if links:
                for link in links:
                    
                    rep_link = f"(http://aqwwiki.wikidot.com{link.replace('(', '').replace(')', '')})"
                    target = target.replace(link, rep_link)
            # if "price" in head:
            #     if "*" in target:
            #         target = [tar.strip() for tar in target.split("*")]
            #         target = target[1]

            if "location" in head:
                if "*" in target:
                    str_list = list(filter(None, target.split(" *")))
                    target = '\n'.join(["- " + tar.strip() for tar in str_list[1:]])

            if "price" in head:
                if "*" in target:
                    str_list = list(filter(None, target.split(" *")))
                    target = '\n'.join(["- " + tar.strip() for tar in str_list])

            if " *" in target:
                target = ' '.join([tar.strip() for tar in target.split(" *")])

            data[x] = target.strip()

        # ac_tag = [a.text.strip() for a in sites_soup.find("div", {"class": "page-tags"}).find("span").find_all("a")]


        # if "ac" in ac_tag:
        #     data["ac_tag"] = True
        # pprint("Data:", data)
        return data


    def get_image_wiki(self, soup_item):
        try:
            images = soup_item.find_all("img", {"class":"image"})
            for img in images:
                if "http://i.imgur.com/" in img["src"] or "https://i.imgur.com" in img["src"]:
                    print(img["src"])
                    return img["src"]
        except:
            pass

        try:
            image = soup_item.find_all("div", {"class":"yui-content"})[-1].find_all("div")[0].find_all("img")[-1]["src"]
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
        return "https://cdn.discordapp.com/attachments/805367955923533845/814852887598989342/6M513.png"

    def check_stuff(self, image_url):
        if "https" not in image_url:
            return image_url.replace("http:", "https:")
        return image_url


    def embed_check(self, embedVar):
        self.field_count += 1
        if self.field_count == 2:
            embedVar.add_field(name="\u200b", value="\u200b", inline=False)
            self.field_count = 0
        return embedVar