import disnake
from disnake.ext import commands

from components.setup import MainSetup
from objects.bot import NoirBot


class SetupCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Настройка сервера

    @commands.slash_command(
        description="Давайте тут все настроим!",
        default_member_permissions=disnake.Permissions(administrator=True),
        dm_permission=False,
    )
    async def setup(self, ctx):
        settings = (
            self.bot.db.table("guilds").find_one({"id": ctx.guild.id})
            if self.bot.db.table("guilds").find_one({"id": ctx.guild.id})
            else {}
        )

        await ctx.send(
            embed=disnake.Embed(
                title="Setup Noir",
                description="**{}**\n```yaml\n# Основные\n24/7    - {}\nwebhook - {}\ncolor   - {}\nrole    - {}\n\n# Подписка\nlevel  - {}\nperiod - from {} to {}\n\n```".format(
                    ctx.guild.name,
                    settings.get("24/7", "Disabled"),
                    settings.get("webhook", {}).get("name", "Disabled"),
                    settings.get("color", "Default"),
                    settings.get("role", "everyone"),
                    0,
                    "now",
                    "infinity",
                ),
                color=16711679,
            ).set_image("https://noirplayer.su/static/image/noir%20banner.png"),
            view=MainSetup(self.bot.node),
            ephemeral=True,
        )


def setup(bot: commands.Bot):
    bot.add_cog(SetupCog(bot))
