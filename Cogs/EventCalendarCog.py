
class EventCalendarCog(commands.Cog, BaseTools):
    def __init__(self, Bot):
        self.setup()
        self.bot = Bot

        self.est_dt = datetime.now(timezone('est'))
        self.current_day = self.est_dt.strftime("%d")
        self.current_month = self.est_dt.strftime("%B")

        self.events = BaseProgram.settings["EventCalendarCogSettings"]["events"]
        self.check_current_month()

        self.printer.start()




    def check_current_month(self):
        self.current_month = self.est_dt.strftime("%B")
        if self.current_month != BaseProgram.settings["EventCalendarCogSettings"]["latest_update"]:
            BaseProgram.settings["EventCalendarCogSettings"]["latest_update"] = self.current_month
            self.check_calendar()
            self.file_save("settings")
            self.git_save("settings")
            print("System: Updated month EventCalendarCogSettings[\"events\"].")
        else:
            print("System: Not updating month EventCalendarCogSettings[\"events\"].")
        return

    def check_calendar(self):
        url = "https://www.aq.com/aq.com/lore/calendar"
        sites_soup = BaseProgram.loop.run_until_complete(self.get_site_content(url))
        body = sites_soup.find("section", {"id":"main-content"}).find("div", class_="container").find("div", class_="row").find_all("div", class_="col-xs-12 col-sm-12 col-md-12 col-lg-12")[1]
        list_of_events_raw = body.find_all("p")[2:]

        for i in list_of_events_raw:
            data = unicodedata.normalize("NFKD", i.text)
            data = re.split(r"([\w]+\s[\d]+\s)", data)[1:]
            date = data[0].strip().split(" ")
            info = data[1].split("                  ")
            day = date[1].zfill(2)
            # self.events = {}
            self.events[day] = {}
            self.events[day]["month"] = date[0]
            self.events[day]["info"] = info
        BaseProgram.settings["EventCalendarCogSettings"]["events"] = self.events
        self.file_save("settings")
        self.git_save("settings")
        return

    async def check_event_today(self):

        if self.current_day in self.events:
            if self.events[self.current_day]["month"] == self.current_month:
                info = self.events[self.current_day]["info"]
                return info
        else:
            return None


    @tasks.loop(seconds=3600)
    async def printer(self):
        self.current_day = self.est_dt.strftime("%d")
        print("Checked", self.current_day)
        if self.current_day != BaseProgram.settings["EventCalendarCogSettings"]["current_day"]:
            for guild in self.bot.guilds:
                print(f"Guild: {guild}\tID: {guild.id}")
                if os.name == "nt":
                    # Testing
                    channel = await self.bot.fetch_channel(799238286539227136)
                else:
                    guild_id = str(guild.id)
                    if guild_id not in BaseProgram.settings["server_settings"]:
                        continue
                    else:
                        try:
                            guild_set = BaseProgram.settings["server_settings"][guild_id]
                            channel = await self.bot.fetch_channel(guild_set["event_channel_id"])
                        except:
                            continue 

                BaseProgram.settings["EventCalendarCogSettings"]["current_day"] = self.current_day
                self.file_save("settings")
                self.git_save("settings")
                result = await self.check_event_today()
                if not result:
                    return
                if result:
                    if os.name == "nt":
                        desc = "\> <@&807655230467604510>\n"
                    else:
                        desc = f"\> <@&{str(guild_set['server_noice_role'])}>\n"
                    for text in result:
                        desc += f"\> {text.strip()}"
                    await channel.send(embed=self.embed_single("Event Today", desc))
                    return
            return

    @printer.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()