from disnake.ext import commands
from classes.Bot import NoirBot

from utils.embeds import type_embed

from checks.check_player import check_player_decorator


class SounpadCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @check_player_decorator()
    @commands.slash_command(
        description="Не видите плеера? Я помогу его вам найти или создать!",
        dm_permission=False,
    )
    async def soundpad(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)

        try:
            return await ctx.send(
                embed=type_embed(
                    "info",
                    f"Сейчас плеер находится [здесь]({player.bar.jump_url})\nВы можете не видеть его, если не имеете прав.",
                ),
                ephemeral=True,
            )
        except BaseException:
            return await ctx.send(
                embed=type_embed(
                    "load",
                    "Похоже, плеера на этом сервере нет. Вы можете его создать, используя одну из этих команд: `/play zaycevfm`, `/play multiple`, `/play search`",
                ),
                ephemeral=True,
            )

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @check_player_decorator()
    @commands.slash_command(
        description="Нужно переотправить плеер?", dm_permission=False
    )
    async def resend(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)

        if player:
            await player.update_bar_once(True, ctx)
        else:
            return await ctx.send(
                embed=type_embed(
                    "load",
                    "Не смогла найти плеер. Вы можете его создать, используя одну из этих команд: `/play zaycevfm`, `/play multiple`, `/play search`",
                ),
                ephemeral=True,
            )


def setup(bot: commands.Bot):
    bot.add_cog(SounpadCog(bot))
