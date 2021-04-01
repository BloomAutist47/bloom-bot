
from .Base import *
from discord.ext import commands
from math import ceil


# Illegal Cog lol
class BoatSearchCog(commands.Cog, BaseTools):
    def __init__(self, bot):
        self.setup()
        self.bot = bot
        self.bot.remove_command("help")

    @commands.command()
    async def bverify(self, ctx, author_name:str=""):
        """ Description: Verifies an author and adds them to the settings
                         So that bloom bot can identify their name
            Arguments:
                [ctx] - context
                [author_name] - author to be verified
        """
        allow_ = await self.allow_evaluator(ctx, mode="all-update", command_name="bverify")
        if not allow_:
            return

        if not author_name:
            await ctx.send(f"\> Please input valid author name to verify.")
            return

        if author_name.lower() in BaseProgram.author_list_lowercase:
            await ctx.send(f"\> Author `{author_name}` already verified.")
            return

        BaseProgram.database_updating = True
        author_name = author_name.capitalize()
        BaseProgram.settings["confirmed_authors"][author_name] = {}
        try:
            BaseProgram.settings["confirmed_authors"][author_name]["alias"].append(author_name)
        except:
            BaseProgram.settings["confirmed_authors"][author_name]["alias"] = []
            BaseProgram.settings["confirmed_authors"][author_name]["alias"].append(author_name)

        await ctx.send(r"\> Saving to settings.json")
        self.file_save("settings")
        self.git_save("settings")
        await ctx.send(r"\> Author Successfully added!")
        await ctx.send(r"\> Please update the database with `;update database <type>`!")
        BaseProgram.database_updating = False
        return
                

    @commands.command()
    async def bunverify(self, ctx, author_name:str=""):
        """ Description: Removes an author from the settings
                         So that bloom bot cannot identify their name
            Arguments:
                [ctx] - context
                [author_name] - author to be unverified
        """
        allow_ = await self.allow_evaluator(ctx, mode="all-update", command_name="bunverify")
        if not allow_:
            return

        if not author_name:
            await ctx.send(f"\> Please input valid author name to unverify.")
            return

        author_removed = False
        BaseProgram.database_updating = True
        author_name = author_name.lower()

        for author in BaseProgram.settings["confirmed_authors"]:
            if author_name == author.lower() and not author_removed:
                BaseProgram.settings["confirmed_authors"].pop(author, None)
                author_removed = True
                break
            aliases = self.find_author_aliases(author)
            if author_name in aliases:
                BaseProgram.settings["confirmed_authors"].pop(author, None)
                author_removed = True
                break

        if not author_removed:
            await ctx.send(f"\> No author of name `{author_name}` found in the confirmed list.")
            BaseProgram.database_updating = False
            return

        await ctx.send(r"\> Saving to settings.json")
        self.file_save("settings")
        self.git_save("settings")
        await ctx.send(r"\> Author Successfully removed!")
        await ctx.send(r"\> Please update the database with `;update database <type>`!")
        BaseProgram.database_updating = False
        return

    @commands.command()
    async def b(self, ctx, *, bot_name:str=""):
        """ Description: Searches the database for a boat
            Arguments:
                [ctx] - context
                [bot_name] - bot search keyword
        """

        # Conditional Checks
        allow_ = await self.allow_evaluator(ctx, mode="guild_privilege-user_permissions",
                command_name="b")
        if not allow_:
            return

        bot_name = bot_name.lower()
        allowed_word = await self.check_word_count(ctx, bot_name, BaseProgram.icon_auqw)
        if not allowed_word:
            return

        cmd_title = "Bot Result"

        """
        # Bot command search
        if bot_name == "all": # Checks if using all command
            priveleged = self.check_role_privilege(ctx, "b all")
            if not priveleged:
                return
            if priveleged:
                bot_results = self.return_all_bots()
                target = self.chunks_list(bot_results, 48)
                desc = "The following are all of the bots"
                for bot_chunk in target:
                    await ctx.send(embed=embed_multi_link(cmd_title, desc, bot_chunk))
                return
        """

        # Actual Searching of boats 
        bot_results = self.find_bot_by_name(bot_name)
        # No boat came up.
        if not bot_results:
            desc = f"We're sorry. No boat came up with your search word: `{bot_name}`"
            await ctx.send(embed=self.embed_single(cmd_title, desc, BaseProgram.icon_auqw))
            return

        await self.embed_multiple_links(ctx, bot_name, bot_results, BaseProgram.icon_auqw)
        return

    @commands.command()
    async def a(self, ctx, *, bot_author: str=""):
        """ Description: Searches for boats by by an author
            Arguments:
                [ctx] - context
                [bot_author] - author search keyword
        """

        # Conditional Checks
        allow_ = await self.allow_evaluator(ctx, mode="guild_privilege-user_permissions",
                command_name="b")
        if not allow_:
            return

        bot_author = bot_author.lower()

        cmd_title = "Bot Author"

        # All bot_author var is empty. Sends list of all authors.
        if bot_author == "":
            author_count = ceil((len(BaseProgram.settings["confirmed_authors"].keys())/3))
            bot_list = sorted([author.lower() for author in BaseProgram.settings["confirmed_authors"]])
            desc ='List of all verified bot authors.'
            embedVar = self.embed_multi_text(cmd_title + "s", "Author", desc, bot_list, author_count, False, BaseProgram.icon_auqw)
            note_desc = "Some bots have unknown authors or were still not \nmanually listed in the "\
                        "confirmed list. To check bots with \nunknown authors, use command `;a u`."
            embedVar.add_field(name="Note:", value=note_desc, inline=True)
            await ctx.send(embed=embedVar)
            return

        # Checks if using author id
        if "<@!" in bot_author:
            author_id_name = self.find_author_id(bot_author)
            if author_id_name:
                bot_author = author_id_name
            else:
                bot_author = None
                desc = f"No author with id `{bot_list[0]}`."
                await ctx.send(embed=self.embed_single(cmd_title, desc, BaseProgram.icon_auqw))
                return

        # Checks if author is unknown
        if bot_author=="unknown" or bot_author=="u":
            bot_author = "Unknown"

        # Actual author command search
        result = self.find_bot_by_author(bot_author)
        found_author = result[0]    # Returns a bool if an exact author is found
        bot_list = result[1]        # List of found bots or possible authors

        # If an author is found
        if found_author:
            
            target = self.chunks_list(bot_list, 49)
            for bot_set in target:
                desc = f"The following are bots created by `{bot_author}`."
                await ctx.send(embed=self.embed_multi_link(cmd_title, "Link", desc, bot_set, BaseProgram.icon_auqw))
            return

        # if no exact author appeared
        if not found_author:
            # if author has no boats
            if len(bot_list) == 1:
                if bot_list[0] not in BaseProgram.database["sort_by_bot_authors"].keys():
                    desc = f"Author `{bot_list[0]}` has not created any boats yet. "
                    await ctx.send(embed=self.embed_single(cmd_title, desc, BaseProgram.icon_auqw))
                    return
            # No author found
            if not bot_list:
                desc = f"We're sorry. No author name came up with your search word: `{bot_author}`"
                await ctx.send(embed=self.embed_single(cmd_title, desc, BaseProgram.icon_auqw))
                return

            # No exact author found but gives suggestions.
            if bot_list and not found_author:
                desc = f"Nothing came up with search key `{bot_author}`.\nMaybe one of these authors?."
                author_count = round((len(BaseProgram.settings["confirmed_authors"].keys())/3))
                embedVar = self.embed_multi_text(cmd_title, "Author", desc, bot_list, author_count, False, BaseProgram.icon_auqw)
                await ctx.send(embed=embedVar)
            return