from .Base import *
from discord.ext import commands
from pprint import pprint
from requests import get as requests_get

class GoogleSearchCog(commands.Cog, BaseTools):
    def __init__(self, Bot):
        self.setup()
        self.bot = Bot


    async def search(self, term, num_results=10, lang="en"):
        usr_agent = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/61.0.3163.100 Safari/537.36'}

        escaped_search_term = term.replace(' ', '+')
        google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, num_results+1,
                                                                              lang)
        soup = await self.get_site_content(URL=google_url, headers=usr_agent, encoding="utf-8", parser="html.parser")
        # response = requests_get(google_url, headers=usr_agent)
        links = {}

        # soup = Soup(response.content, 'html.parser')
        result_block = soup.find_all('div', attrs={'class': 'g'})
        for result in result_block:
            link = result.find('a', href=True)
            title = result.find('h3')
            name = result.find("span").text
            if link and title:
                links[name] = link['href']

        return [links, google_url]

    @commands.command(pass_context=True)
    async def go(self, ctx, *, value:str=""):
        if not value:
            await ctx.send(self.embed_single("Google Search Warning", "Please input a search keyword."))
            return
        item = await self.search(value, 11)

        embedVar = discord.Embed(title=f"Search: __{value}__", color=BaseProgram.block_color,
            url=item[1]
            )
        embedVar.set_author(name="Google Chrome", icon_url=BaseProgram.icon_google)
        desc = f"**Results**\n"
        for i in item[0]:
            link_ = item[0][i]
            desc += f"[{i}]({link_})\n"
        embedVar.description = desc
        await ctx.send(embed=embedVar)
        return