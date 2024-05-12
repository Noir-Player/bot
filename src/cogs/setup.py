import disnake
from disnake.ext import commands

from components.setup import MainSetup, WebhookSetup
from objects.bot import NoirBot


class SetupCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool

    @commands.slash_command(
        dm_permission=False,
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def settings(self, ctx):
        pass

    @settings.sub_command(description="🟣 | настроить роль")
    async def role(
        self,
        ctx,
        role: disnake.Role = commands.Param(
            description="@everyone для доступа без роли"
        ),
    ):
        await ctx.response.defer(ephemeral=True)

        if role.is_default:
            role = None

        self.bot.db.setup.role(ctx.guild.id, role)

        if role:
            description = f"Роль {role.mention} успешно назначена на управляющую позицию. Все участники с данной ролью смогут управлять воспроизведением.\nОднако учтите, администраторы сервера всегда имеют доступ к Noir."
        else:
            description = "Роль удалена. Теперь все участники сервера смогут управлять воспроизведением."

        await ctx.edit_original_message(
            embed=self.bot.embedding.get(
                title=f"🟢 | Роль {'назначена' if role else 'удалена'}",
                description=description,
                color="accent",
            )
        )

    @settings.sub_command(description="🟣 | вебхук")
    async def webhook(self, ctx):
        await ctx.response.send_modal(modal=WebhookSetup(self.bot.node))

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Настройка сервера

    @commands.slash_command(
        description="🟣 | настройка Noir",
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
            ).set_image("https://noirplayer.su/cdn/noir%20banner%20primary.png"),
            view=MainSetup(self.bot.node),
            ephemeral=True,
        )


def setup(bot: commands.Bot):
    bot.add_cog(SetupCog(bot))
