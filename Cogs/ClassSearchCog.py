
import re
from .Base import *
from discord.ext import commands


class ClassSearchCog(BaseTools, commands.Cog):

    def __init__(self, bot):
        self.setup()
        self.bot = bot
        self.bot.remove_command("help")
        self.credits = "➣ Thanks to Shiminuki and Molevolent for\nthe Class Tier List"\
            "and to the AuQW Community!\n➣ Type ;credits to see their links!"

    async def embed_image(self, ctx, discord_url:str, wiki_url:str, class_name:str, duplicate_name:str=""):
        """ Description: Sends an Image embed for the ;c class_name command
            Arguments:
                [ctx] - context
                [discord_url] - str. the url link of the class chart
                [wiki_url] - str. the url link for the class wiki
                [class_name] - str. name of the class
                [duplicate_name] - str. sends an embed stating that the class is a duplicate
        """

        if duplicate_name:
            dupliVar = discord.Embed(title="Duplicate", color=self.block_color, 
                description=f"`{duplicate_name[0]}` is a duplicate of the __{duplicate_name[1]}__ Class")
            dupliVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
            await ctx.send(embed=dupliVar)

        embedVar = discord.Embed(title=class_name, color=self.block_color, url=wiki_url,
            description=f"Use `;legends` to understand the chart.")
        embedVar.set_image(url=discord_url)
        embedVar.set_footer(text=self.credits)
        embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
        await ctx.send(embed=embedVar)


    @commands.command()
    async def legends(self, ctx):

        embedVar = discord.Embed(title="Legends", color=self.block_color)
        embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
        embedVar.set_image(url=BaseProgram.settings["ClassSearchCogSettings"]["legends_link"])
        embedVar.set_footer(text=self.credits)
        await ctx.send(embed=embedVar)
        return


    @commands.command()
    async def c(self, ctx, *, class_name: str=""):
        allow_ = await self.allow_evaluator(ctx, mode="user_permissions", command_name="c")
        if not allow_:
            return
        
        class_name = re.sub('[^A-Za-z0-9]+', '', class_name)

        cmd_title = "Class Search"
        if class_name=="":
            desc = f"Please input a valid class name. "
            embedVar = self.embed_single(cmd_title, desc)
            embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
            await ctx.send(embed=embedVar)
            return

        if len(class_name) == 1:
            desc = f"Please input a search word of atleast two character length. "
            embedVar = self.embed_single(cmd_title, desc)
            embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
            await ctx.send(embed=embedVar)
            return

        # Boat Searching
        

        result = self.find_class(class_name.lower())
        found_class = result[0]
        found_data = result[1]
        if found_class[0] == "Authentic":
            await self.embed_image(ctx, found_data[1], found_data[2], found_data[0])
            return
        if found_class[0] == "Duplicate":
            await self.embed_image(ctx, found_data[1], found_data[2], found_data[0], [found_class[1], found_data[0]])
            return
        if found_class[0] == "Basic":
            enh = found_data[1]["enh"].capitalize()
            awe = found_data[1]["awe_enh"].capitalize()
            wiki = found_data[1]["wiki"].capitalize()
            if "note" in found_data[1]:
                note = found_data[1]["note"].capitalize()

            desc = f"```autohotkey\n[Enchancement]: {enh}\n[Awe Enchant]: {awe}\n"
            try:
                if note != "":
                    desc += f"[Note]: {note}\n"
            except: pass
            desc += "```"
            desc += f"\> [Check the Wiki]({wiki})"
            embedVar = self.embed_single(found_data[0] + " Class", desc)
            embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
            await ctx.send(embed=embedVar)
            return
        if not found_class[0] and found_data:
            desc = f'Sorry, nothing came up with your search word {class_name}.\nMaybe one of these?'
            embedVar = self.embed_multi_text(cmd_title, "Classes", desc, found_data, 10, False)
            embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
            await ctx.send(embed=embedVar)
            return
        if not found_class[0] and not found_data: 
            desc = f"No class matches your search word `{class_name}`.\nPlease type exact class name or class acronyms."
            embedVar = self.embed_single(cmd_title, desc)
            embedVar.set_author(name="AdventureQuest Worlds", icon_url=BaseProgram.icon_aqw)
            await ctx.send(embed=embedVar)
            return
