import os
from .Base import *
from discord.ext import commands

class GuideCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot
        # self.bot.remove_command("help")
        self.fotter = "Tip: Use \";g\" to summon a list of all guides. Type `;bhelp` to summon a list of all commands."



    @commands.command()
    async def g(self, ctx, guide=""):
        if os.name == "nt": # PC Mode
            self.file_read("guides") 

        if guide == "":
            embedVar = discord.Embed(title="🔹 List of Guide Commands 🔹", color=BaseProgram.block_color,
                description="To summon this list, use `;g`. Please read the following carefully.\n To know all Bloom Bot commands, use `;bhelp`.\n\n")
            # embedVar.set_author()
            desc = ""
            guild_id = str(ctx.guild.id)
            if guild_id in BaseProgram.settings["server_settings"]:
                if BaseProgram.settings["server_settings"][guild_id]["server_privilage"] == "Homie":
                    for guide_name in BaseProgram.guides:
                        guide_data = BaseProgram.guides[guide_name]
                        if "type" in guide_data:
                            if guide_data["type"] == "header":
                                if "tag" not in guide_data:
                                    desc += "\u200b"
                                embedVar.add_field(name=f"{guide_name}", inline=False, value=desc)
                                desc = ""
                                continue
                        if "title" in guide_data:
                            desc += "`;g {}` - {}.\n".format(guide_name, guide_data["title"])


            if guild_id not in BaseProgram.settings["server_settings"]:
                for guide_name in BaseProgram.guides:
                    if guide_name not in BaseProgram.settings["server_settings"]["Basic"]["banned_guides"]:
                        guide_data = BaseProgram.guides[guide_name]
                        if "type" in guide_data:
                            if guide_data["type"] == "header":
                                if "tag" not in guide_data:
                                    desc += "\u200b"
                                embedVar.add_field(name=f"{guide_name}", inline=False, value=desc)
                                desc = ""
                                continue
                        if "title" in guide_data:
                            desc += "`;g {}` - {}.\n".format(guide_name, guide_data["title"])
            await ctx.send(embed=embedVar)
            return

        g_name = guide.lower()
        guide_mode = await self.check_guild_guide(ctx)
        if not guide_mode:
            if g_name in BaseProgram.settings["server_settings"]["Basic"]["banned_guides"]:
                return

        if g_name in BaseProgram.guides:
            if "common_key" in BaseProgram.guides[g_name]:
                key = BaseProgram.guides[g_name]["common_key"]
                guide_data = BaseProgram.guides[key]
            else:
                guide_data = BaseProgram.guides[g_name]

            if guide_data["type"] == "header":
                return

            au_title = BaseProgram.icons[guide_data["auth"]]["title"]
            au_icon = BaseProgram.icons[guide_data["auth"]]["icon"]

            if guide_data["type"] == "guide":
                
                embedVar = discord.Embed(title="🔹 " + guide_data["title"] + " 🔹", color=BaseProgram.block_color,
                    description="The following is a short guide of %s. "\
                                "For the [Full Guide click this](%s)."%(guide_data["title"], guide_data["full_guide"]))
                embedVar.set_image(url=guide_data["short_link"])
                embedVar.set_thumbnail(url=guide_data["thumbnail"])
                embedVar.set_footer(text=self.fotter)
                embedVar.set_author(name=au_title, icon_url=au_icon)
                await ctx.send(embed=embedVar)
                return

            if guide_data["type"] == "guide_links":

                embedVar = discord.Embed(title="🔹 " + guide_data["title"] + " 🔹", color=BaseProgram.block_color)
                desc = guide_data["description"]
                for text in guide_data["content"]:
                    desc += "➣ [{}]({}).\n".format(text[0], text[1])
                embedVar.description = desc
                embedVar.set_thumbnail(url=guide_data["thumbnail"])
                embedVar.set_footer(text=self.fotter)
                embedVar.set_author(name=au_title, icon_url=au_icon)
                await ctx.send(embed=embedVar)
                return

            if guide_data["type"] == "text":
                embedVar = discord.Embed(title="🔹 " + guide_data["title"] + " 🔹", color=BaseProgram.block_color)
                desc = guide_data["description"] + "\n\n"
                bullet = ""
                if "bullet" in guide_data:
                    bullet = "%s "%(guide_data["bullet"])
                if type(guide_data["content"]) is list:
                    for sentence in guide_data["content"]:
                        desc += bullet + sentence + "\n"
                else:
                    desc = guide_data["content"]
                embedVar.description = desc
                if "thumbnail" in guide_data:
                    embedVar.set_thumbnail(url=guide_data["thumbnail"])
                if "image" in guide_data:
                    embedVar.set_image(url=guide_data["image"])
                embedVar.set_footer(text=self.fotter)
                embedVar.set_author(name=au_title, icon_url=au_icon)
                await ctx.send(embed=embedVar)
                return

            if guide_data["type"] == "text":
                embedVar = discord.Embed(title="🔹 " + guide_data["title"] + " 🔹", color=BaseProgram.block_color)
                desc = guide_data["description"] + "\n\n"
                bullet = ""
                if "bullet" in guide_data:
                    bullet = "%s "%(guide_data["bullet"])
                if type(guide_data["content"]) is list:
                    for sentence in guide_data["content"]:
                        desc += bullet + sentence + "\n"
                else:
                    desc = guide_data["content"]
                embedVar.description = desc
                if "thumbnail" in guide_data:
                    embedVar.set_thumbnail(url=guide_data["thumbnail"])
                if "image" in guide_data:
                    embedVar.set_image(url=guide_data["image"])
                embedVar.set_footer(text=self.fotter)
                embedVar.set_author(name=au_title, icon_url=au_icon)
                await ctx.send(embed=embedVar)
                return

            if guide_data["type"] == "text-field":
                embedVar = discord.Embed(title="🔹 " + guide_data["title"] + " 🔹", color=BaseProgram.block_color,
                description=guide_data["description"] + "\n\n")
                count = 0
                for item in guide_data["content"]:
                    if count == 1:
                        embedVar.add_field(name="\u200b", value="\u200b", inline=True)
                    if count == 2: count = 0
                    embedVar.add_field(name=item, value=guide_data["content"][item], inline=True)
                    count += 1

                if "thumbnail" in guide_data:
                    embedVar.set_thumbnail(url=guide_data["thumbnail"])
                if "image" in guide_data:
                    embedVar.set_image(url=guide_data["image"])
                embedVar.set_footer(text=self.fotter)
                embedVar.set_author(name=au_title, icon_url=au_icon)
                await ctx.send(embed=embedVar)
                return

            if guide_data["type"] == "image":
                embedVar = discord.Embed(title="🔹 " + guide_data["title"] + " 🔹", color=BaseProgram.block_color)
                embedVar.description = guide_data["description"]
                embedVar.set_image(url=guide_data["content"])
                embedVar.set_footer(text=self.fotter)
                embedVar.set_author(name=au_title, icon_url=au_icon)
                await ctx.send(embed=embedVar)
                return


            if guide_data["type"] == "single_link":
                embedVar = discord.Embed(title="🔹 " + guide_data["title"] + " 🔹", color=BaseProgram.block_color)
                if type(guide_data["description"]) is list:
                    desc = ""
                    for sentence in guide_data["description"]:
                        desc += sentence + "\n"
                else:
                    desc = guide_data["description"] + "\n"
                desc += "➣ [Click this link]({}).".format(guide_data["content"])
                embedVar.description = desc
                if "thumbnail" in guide_data:
                    embedVar.set_thumbnail(url=guide_data["thumbnail"])
                embedVar.set_footer(text=self.fotter)
                embedVar.set_author(name=au_title, icon_url=au_icon)
                await ctx.send(embed=embedVar)
                return
        else:
            rec = ""
            for guide in BaseProgram.guides:
                if "type" in BaseProgram.guides[guide] and BaseProgram.guides[guide]["type"] == "header":
                    continue
                if "common_key" in BaseProgram.guides[guide]:
                    continue
                listed = []
                print(f"➣ `;g {guide}` - {BaseProgram.guides[guide]['title']}")
                if g_name in guide.lower() and guide not in listed:
                    rec += f"➣ `;g {guide}` - {BaseProgram.guides[guide]['title']}\n"
                    listed.append(guide)
                if guide.lower() in g_name and guide not in listed:
                    rec += f"➣ `;g {guide}` - {BaseProgram.guides[guide]['title']}\n"
                    listed.append(guide)
            if rec:
                embedVar = discord.Embed(title="Guides", color=BaseProgram.block_color,
                    description="No specific guide name came up. Maybe one of these?")
                embedVar.add_field(name="Suggestions:", value=rec, inline=False)
                await ctx.send(embed=embedVar)
                return
            else:



                embedVar = discord.Embed(title="Guides", color=BaseProgram.block_color,
                    description=f"No guide name came up with your search term `;g {g_name}`.")
                await ctx.send(embed=embedVar)
                return   
