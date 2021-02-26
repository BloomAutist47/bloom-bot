import re

from .Base import *
from discord.ext import commands

class WikiCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot

    @commands.command()
    async def w(self, ctx, *, item=""):
        if item == "":
            embedVar = self.embed_single("Wiki Search", "Please enter a value.")
            await ctx.send(embed=embedVar)
            return
        item = item.lower()

        straight = self.convert_aqurl(item, "wiki")
        wiki = self.convert_aqurl(item, "wikisearch")

        only_wiki = False
        sites_soup = await self.get_site_content(straight)

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
                # Referals
                title = sites_soup.find("div", {"id":"main-content"}).find("div", {"id": "page-title"}).text.strip()
                result = straight
                first_refer = "http://aqwwiki.wikidot.com/" + page_content.find_all("a")[0]["href"]
                fr_sites_soup = await self.get_site_content(first_refer)
                fr_page_content = fr_sites_soup.find("div", {"id":"page-content"})
                image = self.get_image_wiki(fr_page_content)
                only_wiki = False
            else:
                # True Item
                title = sites_soup.find("div", {"id":"main-content"}).find("div", {"id": "page-title"}).text.strip()
                result = straight
                image = self.get_image_wiki(page_content)
                only_wiki = False
        except:
            # Search
            title = ""
            result = wiki
            image = None
            only_wiki = True
            
        if title:
            embedVar = self.embed_single(title, f"{result}" )
        else:
            embedVar = self.embed_single("Wiki Search", f"{result}" )


        if not only_wiki:
            embedVar.add_field(name="All Result", value=f"[Click here for all result]({wiki})", inline=False)
        if image:
            embedVar.set_thumbnail(url=image)

        embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
        await ctx.send(embed=embedVar)
        # while True:
        #     try:
        #         await ctx.send(embed=embedVar)
        #         print(f"> Function send executed...Success!")
        #         break
        #     except:
        #         print(f"> Failed Executing send... Trying again.")
        #         print("> Reloading...")
        #         continue
        return

    @commands.command()
    async def ws(self, ctx, *, item=""):
        if item == "":
            embedVar = self.embed_single("Wiki Search", "Please enter a value.")
            await ctx.send(embed=embedVar)
            return

        wiki = self.convert_aqurl(item, "wikisearch")

        embedVar = self.embed_single("Wiki Search", wiki)
        embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
        await ctx.send(embed=embedVar)
        return

    def get_image_wiki(self, soup_item):
        try:
            images = soup_item.find_all("img", {"class":"image"})
            for img in images:
                if "http://i.imgur.com/" in img["src"] or "https://i.imgur.com" in img["src"]:
                    print(img["src"])
                    return img["src"]
            return "https://cdn.discordapp.com/attachments/805367955923533845/814852887598989342/6M513.png"
        except:
            return "https://cdn.discordapp.com/attachments/805367955923533845/814852887598989342/6M513.png"

        # try:
        #     image = soup_item.find_all("div", {"class":"yui-content"})[-1].find_all("div")[0].find_all("img")[-1]["src"]
        #     images = self.check_stuff(image)
        #     print(images)
        #     return images
        # except: pass

        # try:
        #     image = soup_item.find_all("img")[-1]["src"]
        #     images = self.check_stuff(image)
        #     print(images)
        #     return images
        # except:
        #     return Nonee

    def check_stuff(self, image_url):
        if "https" not in image_url:
            return image_url.replace("http:", "https:")
        return image_url

