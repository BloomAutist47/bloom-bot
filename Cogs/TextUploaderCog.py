

class TextUploaders(commands.Cog, BaseTools):
    def __init__(self, Bot):
        self.setup()
        self.bot = Bot


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
    async def uptext(self, ctx):
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

        if str(ctx.channel.id) in BaseProgram.settings["TextUploadSettings"]["channels"]:
            hook_link = BaseProgram.settings["TextUploadSettings"]["channels"][f"{ctx.channel.id}"]
        else:
            await ctx.send("\> Please set a Webhook for this channel with `;upset webhook_name`.")
            return

        file_n = attach.filename
        if file_n.split(".")[-1] != "txt":
            await ctx.send("\> Only a .txt files are allowed with `;uptext` command.")
            return  

        target_url = attach.url
        
        data = BaseProgram.loop.run_until_complete(self.get_site_txt(target_url))
        text = str(data.decode('cp1252') ).split("\n")
        await self.send_item(ctx, hook_link, text)

        
        fp = BytesIO()
        await ctx.message.attachments[0].save(fp)
        await self.send_webhook(hook_link, "file", fp, file_n)


    @commands.command()
    async def upset(self, ctx, *, webhook_name:str=""):
        if not webhook_name:
            await ctx.send("\> Please type a webhook name.")
            return

        channel_id = f"{ctx.channel.id}"
        if channel_id in BaseProgram.settings["TextUploadSettings"]["channels"]:
            await ctx.send(f"\> A Webhook  is **already registered** for this channel.\n\> `{webhook_name}`")
            return

        webhook = await ctx.channel.webhooks()
        for hook in webhook:
            if webhook_name == hook.name:
                hook_url = hook.url
                break
        
        BaseProgram.settings["TextUploadSettings"]["channels"][channel_id] = str(hook_url)
        self.file_save("settings")
        self.git_save("settings")
        await ctx.send(f"\> Webhook `{webhook_name}` Successfully set for this channel.")
        return


    @commands.command()
    async def updel(self, ctx):
        channel_id = f"{ctx.channel.id}"
        if channel_id not in BaseProgram.settings["TextUploadSettings"]["channels"]:
            await ctx.send(f"\> This channel has no registered `;uptext` webhook")
            return

        BaseProgram.settings["TextUploadSettings"]["channels"].pop(channel_id, None)
        self.file_save("settings")
        self.git_save("settings")
        await ctx.send(f"\> Webhook Channel for `;uptext` is Successfully unregistered ")
        return


    @commands.command()
    async def up_fags(self, ctx):
        allow_ = await self.allow_evaluator(ctx, mode="role_privilege-update", command_name="up_fags")
        if not allow_:
            return

        if BaseProgram.sqlock:
            return

        index = {}

        BaseProgram.database_updating = True
        embedVar = discord.Embed(title="Frequently Asked Questions", color=BaseProgram.block_color,
            description="Something's not working? Read The following.")
        item_1 = await ctx.send(embed=embedVar)
        start_link_1 = f'https://discordapp.com/channels/{item_1.guild.id}/{item_1.channel.id}/{item_1.id}'
        await ctx.send("\u200b")
        for title in BaseProgram.texts["faqs"]:
            embedVar = discord.Embed(title=title, color=BaseProgram.block_color,
                description=BaseProgram.texts["faqs"][title]["text"])
            if "image" in BaseProgram.texts["faqs"][title]:
                embedVar.set_image(url=BaseProgram.texts["faqs"][title]["image"])
            item = await ctx.send(embed=embedVar)
            start_link = f'https://discordapp.com/channels/{item.guild.id}/{item.channel.id}/{item.id}'
            index[title] = start_link
            await ctx.send("\u200b")

        desc = ""
        count = 0
        start_shit = False
        embedVar = self.embed_single("Frequently Asked Questions", f"[Click here to go to the TOP]({start_link_1})")
        for title in index:
            if count == 7:
                if not start_shit:
                    embedVar.add_field(name="Table of Contents", value=desc, inline=False)
                    start_shit = True
                else:
                    embedVar.add_field(name="\u200b", value=desc, inline=False)
                desc = ""
                count = 0
            desc += f"🔹 [{title}]({index[title]})\n"
            count += 1
        embedVar.add_field(name="\u200b", value=desc, inline=False)
        await ctx.send(embed=embedVar)
        BaseProgram.database_updating = False
        return


    def read_text(self, path):
        f = open(path, "r", encoding='cp1252')
        return f.read().split("\n")
        
    async def send_item(self, ctx, hook_link, lines):
        desc = ""
        for i in lines:
            if len(desc) >1700:
                await self.send_webhook(hook_link, "txt", desc)
                desc = ""
            desc += i + "\n"
        await self.send_webhook(hook_link, "txt", desc)
        BaseProgram.database_updating = False
        return 

    async def send_webhook(self, hook_link:str, mode:str, *value):
        webhook_urls = [hook_link]
        if mode == "txt":
            webhook = DiscordWebhook(url=webhook_urls, content=value[0])
        elif mode == "file":
            webhook = DiscordWebhook(url=webhook_urls)
            webhook.add_file(file=value[0], filename=value[1])
        response = webhook.execute()    
