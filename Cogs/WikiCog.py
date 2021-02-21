
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
        x = re.sub("[']", "-", item).replace(" ", "-")
        x = re.sub("[^A-Za-z0-9\-]+", "", x)
        straight = "http://aqwwiki.wikidot.com/" + x
        wiki = "http://aqwwiki.wikidot.com/search:site/q/" + x.replace("-", "%20")

        only_wiki = False
        sites_soup = BaseProgram.loop.run_until_complete(self.get_site_content(straight))
        try:
            page_content = sites_soup.find("div", {"id":"page-content"})
            page_check = page_content.find("p").text.strip()
            if page_check == "This page doesn't exist yet!":
                result = wiki
                image = None
                only_wiki = True
            elif "usually refers to:" in page_check:
                result = straight
                first_refer = "http://aqwwiki.wikidot.com/" + page_content.find_all("a")[0]["href"]
                fr_sites_soup = BaseProgram.loop.run_until_complete(self.get_site_content(first_refer))
                fr_page_content = fr_sites_soup.find("div", {"id":"page-content"})
                image = self.get_image_wiki(fr_page_content)
                only_wiki = False
            else:
                result = straight
                image = self.get_image_wiki(page_content)
                only_wiki = False
        except:
            result = "http://aqwwiki.wikidot.com/search:site/q/" + item.replace(" ", "%20")
            image = None
            only_wiki = True
            
        
        
        if not only_wiki:
            desc = f"{result}\n[[Click here for all result.]({wiki})]" 
        else:
            desc = f"{result}"

        embedVar = self.embed_single("Wiki Search", desc)
        if image:
            embedVar.set_image(url=image)

        await ctx.send(embed=embedVar)
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
        await ctx.send(embed=embedVar)
        return

    def get_image_wiki(self, soup_item):
        try:
            image = soup_item.find_all("div", {"class":"yui-content"})[-1].find_all("div")[0].find_all("img")[-1]["src"]
            return image
        except: pass

        try:
            image = soup_item.find_all("img")[-1]["src"]
            return image
        except:
            return Nonee


