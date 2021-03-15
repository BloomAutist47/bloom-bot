
import re
from .Base import *
from discord.ext import commands
from io import BytesIO
import textwrap

class TextUploaders(commands.Cog, BaseTools):
    def __init__(self, Bot):
        self.setup()
        self.bot = Bot
        BaseProgram.sqlock = False


    @commands.command()
    async def textlock(self, ctx, value=""):
        """ Description: Toggles the lock for the text upload commands
            Arguments:
                [ctx] - context
                [value] -aaccepts on or off strings
        """
        allow_ = await self.allow_evaluator(ctx, mode="role_privilege", command_name="listlock")
        if not allow_:
            print("NOPE")
            return
        
        value = value.lower().lstrip().rstrip()
        if value == "off":
            BaseProgram.sqlock = False
            await ctx.send("\> Text upload lock turned off!")
            return
            
        if value == "on":
            BaseProgram.sqlock = True
            await ctx.send("\> Text upload lock turned on!")
            return
        else:
            await ctx.send("\> Text upload lock requires <on> or <off>")
            return

    @commands.command()
    async def upfile(self, ctx):
        allow_ = await self.allow_evaluator(ctx, mode="role_privilege-update", command_name="up_quest")
        if not allow_:
            return

        if BaseProgram.sqlock:
            return

        try:
            attach = ctx.message.attachments[0]
        except:
            await ctx.send("\> Please attach a .txt file.")
            return

        file_n = attach.filename
        if file_n.split(".")[-1] != "txt":
            await ctx.send("\> Only a .txt files are allowed with `;uptext` command.")
            return  

        target_url = attach.url
        print(target_url)
        
        data = await self.get_site_content(URL=target_url, is_soup=False, encoding="cp1252")
        text = str(data).split("\n")

        desc = ""
        for i in text:
            if len(desc) >1700:
                await ctx.send(desc)
                desc = ""
            desc += i + "\n"
        await ctx.send(desc)

        BaseProgram.database_updating = False
         
        
        fp = BytesIO()
        await ctx.message.attachments[0].save(fp)
        await ctx.send(file=discord.File(fp, filename=file_n))
        return
        # await self.send_webhook(hook_link, "file", fp, file_n)





    @commands.command()
    async def uptext(self, ctx, textfile=""):
        allow_ = await self.allow_evaluator(ctx, mode="role_privilege-update", command_name="up_fags")
        if not allow_:
            return

        if BaseProgram.sqlock:
            return

        if not textfile:
            await ctx.send("\> Please enter valid value.")
            return

        if textfile not in BaseProgram.texts:
            await ctx.send("\> Text does not exists in current repository.")
            return

        index = {}

        BaseProgram.database_updating = True
        embedVar = discord.Embed(title=BaseProgram.texts[textfile]["title"], color=BaseProgram.block_color,
            description=BaseProgram.texts[textfile]["description"])
        item_1 = await ctx.send(embed=embedVar)
        start_link_1 = f'https://discordapp.com/channels/{item_1.guild.id}/{item_1.channel.id}/{item_1.id}'
        await ctx.send("\u200b")
        for title in BaseProgram.texts[textfile]["content"]:


            embedVar = discord.Embed(title=title, color=BaseProgram.block_color,
                description=BaseProgram.texts[textfile]["content"][title]["text"])
            if "image" in BaseProgram.texts[textfile]["content"][title]:
                embedVar.set_image(url=BaseProgram.texts[textfile]["content"][title]["image"])
            item = await ctx.send(embed=embedVar)
            start_link = f'https://discordapp.com/channels/{item.guild.id}/{item.channel.id}/{item.id}'
            index[title] = start_link
            await ctx.send("\u200b")

        # chunks = textwrap.wrap(text_, 1024, break_long_words=False)

        desc = ""
        count = 1
        start_shit = False
        embedVar = self.embed_single(BaseProgram.texts[textfile]["title"], BaseProgram.texts[textfile]["description"] + f"\n[Click here to go to the Top]({start_link_1})")
        for title in index:
            if count == 8:
                if not start_shit:
                    embedVar.add_field(name="Table of Contents", value=desc, inline=False)
                    start_shit = True
                else:
                    embedVar.add_field(name="\u200b", value=desc, inline=False)
                desc = ""
                count = 0
            desc += f"{count} [{title.split(')')[-1].strip()}]({index[title]})\n"
            count += 1
        if not start_shit:
            embedVar.add_field(name="Table of Contents", value=desc, inline=False)
            start_shit = True
        else:
            embedVar.add_field(name="\u200b", value=desc, inline=False)
        await ctx.send(embed=embedVar)
        BaseProgram.database_updating = False
        return


    def read_text(self, path):
        f = open(path, "r", encoding='cp1252')
        return f.read().split("\n")
