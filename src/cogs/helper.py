import json

import disnake
from disnake.ext import commands

from helpers.embeds import genembed
from objects.bot import NoirBot


class Help(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot

        self._hello_embed = dict(
            json.load(open("data/embeds/hello.json", "r", encoding="utf-8"))
        )

        self._help_embed = dict(
            json.load(open("data/embeds/help.json", "r", encoding="utf-8"))
        )

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_guild_join(self, guild: disnake.Guild):
        f = self._hello_embed

        embed = disnake.Embed(description=f.get("description"), color=f.get("color"))

        embed.set_author(
            name=f.get("author").get("name"),
            url=f.get("author").get("url"),
            icon_url=f.get("author").get("icon_url"),
        )

        embed.set_footer(
            text=f.get("footer").get("text"), icon_url=f.get("footer").get("icon_url")
        )

        embed.set_image(f.get("image").get("url"))

        try:
            await guild.system_channel.send(embed=embed)
        except BaseException:
            pass

        log = await self.bot.fetch_channel(1119658307729236008)

        await log.send(
            embed=genembed(
                f"Join on {guild.name}",
                f"```yaml\nowner - {guild.owner_id}\nmembers - {guild.member_count}\nboosts - {guild.premium_subscription_count}```\n{guild.id}",
            )
        )

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: disnake.Guild):
        log = await self.bot.fetch_channel(1119658307729236008)
        await log.send(
            embed=genembed(
                f"Leave on {guild.name}",
                f"```yaml\nowner - {guild.owner_id}\nmembers - {guild.member_count}\nboosts - {guild.premium_subscription_count}```\n{guild.id}",
            )
        )

        try:
            self.bot.db.setup.clear_guild(guild.id)
        except BaseException:
            pass

        try:
            await self.bot.node.get_player(guild.id).destroy()
        except BaseException:
            pass

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @commands.slash_command(description="🟣 | нужна помощь?")
    async def help(self, ctx):
        settings = self.bot.db.setup.get_setup(ctx.guild.id) or {}

        f = self._help_embed

        embed = disnake.Embed(
            title=f.get("title"),
            description=f.get("description").format(
                ctx.guild.name,
                settings.get("24/7", "disabled"),
                settings.get("webhook", {}).get("name", "Disabled"),
                settings.get("color", "Default"),
                settings.get("role", "everyone"),
                0,
                "now",
                "infinity",
            ),
            color=f.get("color"),
        )

        for field in f.get("fields"):
            embed.add_field(
                field.get("name"), field.get("value"), inline=field.get("inline", False)
            )

        embed.set_footer(
            text=f.get("footer").get("text"), icon_url=f.get("footer").get("icon_url")
        )

        embed.set_image(f.get("image").get("url"))

        await ctx.send(embed=embed, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
