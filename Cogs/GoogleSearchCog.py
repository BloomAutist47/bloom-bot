import pyshorteners

from .Base import *
from discord.ext import commands

class GoogleSearchCog(commands.Cog, BaseTools):
    def __init__(self, Bot):
        self.setup()
        self.bot = Bot
        self.s = pyshorteners.Shortener()


    def search(self, term, num_results=10, lang="en"):
        usr_agent = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/61.0.3163.100 Safari/537.36'}

        def fetch_results(search_term, number_results, language_code):
            escaped_search_term = search_term.replace(' ', '+')

            google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results+1,
                                                                                  language_code)
            # response = requests.get(google_url, headers=usr_agent)
            response = self.get_site_content_looped(URL=google_url, headers=usr_agent)
            # response = BaseProgram.loop.run_until_complete(self.get_site(google_url, headers=usr_agent))
            # response.raise_for_status()

            # return (response.decode("utf-8"), google_url)
            return (response, google_url)

        def parse_results(soup):
            links = {}

            # soup = Soup(raw_html, 'html.parser')
            result_block = soup.find_all('div', attrs={'class': 'g'})
            for result in result_block:
                link = result.find('a', href=True)
                title = result.find('h3')
                name = result.find("span").text
                if link and title:
                    links[name] = link['href']
            return links
        html = fetch_results(term, num_results, lang)
        return [parse_results(html[0]), html[1]]


    @commands.command(pass_context=True)
    async def go(self, ctx, *, value:str=""):
        if not value:
            await ctx.send(self.embed_single("Google Search Warning", "Please input a search keyword."))
            return
        item = self.search(value, 10)
        # item = self.floop(lambda: self.search(value, 10))
        link_all = self.floop(lambda: self.s.tinyurl.short(item[1]))
        embedVar = discord.Embed(title=f"Search - __{value}__", color=self.block_color,
            )
        embedVar.set_author(name="Google Chrome", icon_url=BaseProgram.icon_google)
        desc = f"[Click here for all Result]({link_all})\n\n**Results**\n"
        # response = BaseProgram.loop.run_until_complete(
        for i in item[0]:
            # print(item[0][i])
            # link_ = BaseProgram.loop.run_until_complete(BaseProgram.s.tinyurl.short(item[0][i]))
            link_ = item[0][i]
            desc += f"[{i}]({link_})\n"
        embedVar.description = desc
        # embedVar.add_field(name="Results", value=desc, inline=False)
        await ctx.send(embed=embedVar)
        return