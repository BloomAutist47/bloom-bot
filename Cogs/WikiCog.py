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
        x = re.sub("[']", "-", item).replace(" ", "-")
        x = re.sub("[^A-Za-z0-9\-]+", "", x)
        straight = "http://aqwwiki.wikidot.com/" + x
        wiki = "http://aqwwiki.wikidot.com/search:site/q/" + x.replace("-", "%20")

        only_wiki = False
        sites_soup = self.get_url_item(straight)
        title = sites_soup.find("div", {"id":"main-content"}).find("div", {"id": "page-title"}).text.strip()
        # sites_soup = BaseProgram.loop.run_until_complete(self.get_site_content(straight))
        try:
            print("Diid this")
            page_content = sites_soup.find("div", {"id":"page-content"})
            page_check = page_content.find("p").text.strip()
            if page_check == "This page doesn't exist yet!":
                title = ""
                result = wiki
                image = None
                only_wiki = True
            elif "usually refers to:" in page_check:
                title = sites_soup.find("div", {"id":"main-content"}).find("div", {"id": "page-title"}).text.strip()
                result = straight
                first_refer = "http://aqwwiki.wikidot.com/" + page_content.find_all("a")[0]["href"]
                fr_sites_soup = self.get_url_item(first_refer)
                # fr_sites_soup = BaseProgram.loop.run_until_complete(self.get_site_content(first_refer))
                fr_page_content = fr_sites_soup.find("div", {"id":"page-content"})
                image = self.get_image_wiki(fr_page_content)
                only_wiki = False
            else:
                title = sites_soup.find("div", {"id":"main-content"}).find("div", {"id": "page-title"}).text.strip()
                result = straight
                image = self.get_image_wiki(page_content)
                only_wiki = False
        except:
            print("Nope this")
            title = ""
            result = "http://aqwwiki.wikidot.com/search:site/q/" + item.replace(" ", "%20")
            image = None
            only_wiki = True
            
        
        desc = f"{result}" 
 

        if title:  embedVar = self.embed_single(title, desc)
        else: embedVar = self.embed_single("Wiki Search", desc)
        if image:
            print("YUPS")
            embedVar.set_image(url=image)
        if not only_wiki:
            embedVar.add_field(name="All Result", value=f"[Click here for all result]({wiki})", inline=False)
        embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
        while True:
            try:
                await ctx.send(embed=embedVar)
                print(f"> Function send executed...Success!")
                break
            except:
                print(f"> Failed Executing send... Trying again.")
                print("> Reloading...")
                continue
        return

    @commands.command()
    async def ws(self, ctx, *, item=""):
        if item == "":
            embedVar = self.embed_single("Wiki Search", "Please enter a value.")
            await ctx.send(embed=embedVar)
            return
        x = re.sub("[']", "-", item).replace(" ", "-")
        x = re.sub("[^A-Za-z0-9\-]+", "", x)
        straight = "http://aqwwiki.wikidot.com/" + x
        wiki = "http://aqwwiki.wikidot.com/search:site/q/" + x.replace("-", "%20")

        embedVar = self.embed_single("Wiki Search", wiki)
        embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
        await ctx.send(embed=embedVar)
        return

    def get_image_wiki(self, soup_item):
        try:
            image = soup_item.find_all("div", {"class":"yui-content"})[-1].find_all("div")[0].find_all("img")[-1]["src"]
            images = self.check_stuff(image)
            print(images)
            return images
        except: pass

        try:
            image = soup_item.find_all("img")[-1]["src"]
            images = self.check_stuff(image)
            print(images)
            return images
        except:
            return Nonee

    def check_stuff(self, image_url):
        if "https" not in image_url:
            return image_url.replace("http:", "https:")
        return image_url

