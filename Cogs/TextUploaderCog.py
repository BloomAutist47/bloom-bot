
import re
from .Base import *
from discord.ext import commands, tasks
from io import BytesIO
import textwrap
from pprintpp import pprint
class TextUploaders(commands.Cog, BaseTools):
    def __init__(self, Bot):
        self.setup()
        self.bot = Bot
        self.server_inv = ""
        self.server_guild = ""
        # if BaseProgram.texts["Data"]["Server ON"]:
        #     self.server_invite.start()
        #     pass
        # BaseProgram.sqlock = False
# 

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
        
        fp = BytesIO()
        await ctx.message.attachments[0].save(fp)

        await self.clear(ctx)

        desc = ""
        for i in text:
            if len(desc) >1700:
                await ctx.send(desc)
                desc = ""
            desc += i + "\n"
        await ctx.send(desc)

        BaseProgram.database_updating = False
         
        

        await ctx.send(file=discord.File(fp, filename=file_n))
        return
        # await self.send_webhook(hook_link, "file", fp, file_n)

    @commands.command()
    async def upembed(self, ctx, type_=""):
        allow_ = await self.allow_evaluator(ctx, mode="role_privilege-update", command_name="up_fags")
        if not allow_:
            return

        if BaseProgram.sqlock:
            return
        type_ = type_.lower()
        if not type_ or type_ not in BaseProgram.texts["Embed"]:
            await ctx.send("\> Please enter valid text name.")
            return

        await self.clear(ctx)

        start_link_1 = ""

        embed_lis_all = BaseProgram.texts["Embed"][type_]
        for embed in embed_lis_all:
            embed_list = BaseProgram.texts["Embed"][type_][embed]
            msg = ""
            embedVar = discord.Embed(title=embed, color=BaseProgram.block_color)
            if "description" in embed_list:
                embedVar.description = embed_list["description"]

            if "title_url" in embed_list:
                embedVar.url = embed_list["title_url"]

            if "author" in embed_list:
                embedVar.set_author(name=embed_list["author"])

            if "embed_list" in embed_list:
                for field in embed_list["embed_list"]:
                    embedVar.add_field(name=field, value=embed_list["embed_list"][field], inline=False)

            if "image" in embed_list:
                embedVar.set_image(url=embed_list["image"])

            if "thumbnail" in embed_list:
                embedVar.set_thumbnail(url=embed_list["thumbnail"])

            if "message" in embed_list:
                msg += embed_list["message"]

            if embed == "Welcome":
                embedVar.add_field(name="\u200b", value=f"[Click here to go to the Top]({start_link_1})", inline=False)

            item_1 = await ctx.send(msg, embed=embedVar)
            await ctx.send("\n\u200b")
            if not start_link_1:
                start_link_1 = f'https://discordapp.com/channels/{item_1.guild.id}/{item_1.channel.id}/{item_1.id}'
            
            # if os.name != "nt":
            #     if embed == "Pearl Harbor: The AQW Sailor's Paradise":
            #         BaseProgram.texts["Data"]["Server Invite"] = item_1.id
            #         BaseProgram.texts["Data"]["Server Channel"] = ctx.channel.id
            #         BaseProgram.texts["Data"]["Server ON"] = True
            #         self.git_save("texts")
            #         self.server_invite.start()
                


    @tasks.loop(minutes=10)
    async def server_invite(self):
        if os.name == "nt":
            self.server_guild = self.bot.get_guild(761956630606250005)
        else:
            self.server_guild = self.bot.get_guild(811305081063604284)

        print("> channel: ", BaseProgram.texts["Data"]["Server Channel"])
        self.server_channel = await self.bot.fetch_channel(BaseProgram.texts["Data"]["Server Channel"])
        self.server_inv = await self.server_channel.fetch_message(BaseProgram.texts["Data"]["Server Invite"])

        online_mem = sum(member.status!=discord.Status.offline and not member.bot for member in self.server_guild.members)
        total_mem = len([m for m in self.server_guild.members if not m.bot])
        
        embedVar = embedVar = discord.Embed(title="Pearl Harbor: The AQW Sailor's Paradise", color=BaseProgram.block_color,
            url="https://discord.io/AQWBots", description=f"🟢 {online_mem} Online⚪ {total_mem} Members")
        embedVar.set_author(name="Server Invite")
        embedVar.set_thumbnail(url="https://cdn.discordapp.com/attachments/805367955923533845/829203599292366869/i.png")

        await self.server_inv.edit(embed=embedVar)
        print("> did")

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

        if textfile not in BaseProgram.texts["Texts"]:
            await ctx.send("\> Text does not exists in current repository.")
            return

        await self.clear(ctx)

        index = {}

        BaseProgram.database_updating = True
        embedVar = discord.Embed(title=BaseProgram.texts["Texts"][textfile]["title"], color=BaseProgram.block_color,
            description=BaseProgram.texts["Texts"][textfile]["description"])
        item_1 = await ctx.send(embed=embedVar)
        start_link_1 = f'https://discordapp.com/channels/{item_1.guild.id}/{item_1.channel.id}/{item_1.id}'
        for title in BaseProgram.texts["Texts"][textfile]["content"]:


            embedVar = discord.Embed(title=title, color=BaseProgram.block_color,
                description=BaseProgram.texts["Texts"][textfile]["content"][title]["text"])
            if "image" in BaseProgram.texts["Texts"][textfile]["content"][title]:
                embedVar.set_image(url=BaseProgram.texts["Texts"][textfile]["content"][title]["image"])
            item = await ctx.send("\u200b", embed=embedVar)
            start_link = f'https://discordapp.com/channels/{item.guild.id}/{item.channel.id}/{item.id}'
            index[title] = start_link

        desc = ""
        count = 0
        text_count = 1
        start_shit = False
        embedVar = self.embed_single(BaseProgram.texts["Texts"][textfile]["title"], BaseProgram.texts["Texts"][textfile]["description"] + f"\n[Click here to go to the Top]({start_link_1})")
        for title in index:
            if count == 6:
                if not start_shit:
                    embedVar.add_field(name="Table of Contents", value=desc, inline=False)
                    start_shit = True
                else:
                    embedVar.add_field(name="\u200b", value=desc, inline=False)
                # pprint(desc)
                # print()
                desc = ""
                count = 0
            if "numbering" in BaseProgram.texts["Texts"][textfile] and BaseProgram.texts["Texts"][textfile]["numbering"] == False:
                desc += f"[{title}]({index[title]})\n"
                print(f"jereee: {title}")
            else:
                text_count += 1
                desc += f"{text_count} [{title.split(')')[-1].strip()}]({index[title]})\n"

            
            count += 1


        if not start_shit:
            embedVar.add_field(name="Table of Contents", value=desc, inline=False)
            start_shit = True
        else:
            embedVar.add_field(name="\u200b", value=desc, inline=False)
        await ctx.send("\u200b", embed=embedVar)
        BaseProgram.database_updating = False
        return


    @commands.command()
    async def upinfo(self, ctx, textfile=""):
        allow_ = await self.allow_evaluator(ctx, mode="role_privilege-update", command_name="up_fags")
        if not allow_:
            return

        if BaseProgram.sqlock:
            return

        if not textfile:
            await ctx.send(r"\> Please enter valid value.")
            return

        if textfile not in BaseProgram.texts["Embed"]:
            await ctx.send(r"\> Text does not exists in current repository.")
            return

        dat = BaseProgram.texts["Embed"][textfile]
        count = 0
        text_count = 1
        start_shit = False
        embedVar = discord.Embed(title=textfile, color=BaseProgram.block_color, 
            description=dat["description"])

        for item in dat["embed_list"]:
            embedVar.add_field(name="", value=desc, inline=False)

        await ctx.send("\u200b", embed=embedVar)
        BaseProgram.database_updating = False
        return


    async def clear(self, ctx):
        print("yes?")
        length = await ctx.message.channel.history(limit=999).flatten()
        num = len(length)
        div = 100
        target = [num // div + (1 if x < num % div else 0)  for x in range (div)]

        for tar in target:
            async for message in ctx.message.channel.history(limit=tar):
                await ctx.message.channel.delete_messages([message])

        

    def read_text(self, path):
        f = open(path, "r", encoding='cp1252')
        return f.read().split("\n")
