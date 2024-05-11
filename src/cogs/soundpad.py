from disnake.ext import commands

from objects.bot import NoirBot
from validators.player import check_player_decorator


class SounpadCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @check_player_decorator()
    @commands.slash_command(
        description="🔵 | где плеер?",
        dm_permission=False,
    )
    async def soundpad(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)

        try:
            return await ctx.send(
                embed=self.bot.embedding.get(
                    title="🔵 | Расположение",
                    description=f"[⭐ клик]({player.controller.jump_url})",
                    color="info",
                ),
                # embed=type_embed(
                #     "info",
                #     f"Сейчас плеер находится [здесь]({player.controller.jump_url})\nВы можете не видеть его, если не имеете прав.",
                # ),
                ephemeral=True,
            )
        except BaseException:
            return await ctx.send(
                embed=self.bot.embedding.get(
                    title="🟠 | Не найдено",
                    description="Не удалось найти плеер. Вы по-прежнему можете смотреть текущий трек через команду `/now playing`",
                    color="warning",
                ),
                # embed=type_embed(
                #     "load",
                #     "Похоже, плеера на этом сервере нет. Вы можете его создать, используя одну из этих команд: `/play zaycevfm`, `/play multiple`, `/play search`",
                # ),
                ephemeral=True,
            )

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @check_player_decorator()
    @commands.slash_command(
        description="🔵 | повторно отправить плеер", dm_permission=False
    )
    async def resend(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)

        if player:
            await player.update_controller_once(True, ctx)
        else:
            return await ctx.send(
                embed=self.bot.embedding.get(
                    title="🟠 | Не найдено",
                    description="Не удалось найти плеер. Вы по-прежнему можете смотреть текущий трек через команду `/now playing`",
                    color="warning",
                ),
                # embed=type_embed(
                #     "load",
                #     "Не смогла найти плеер. Вы можете его создать, используя одну из этих команд: `/play zaycevfm`, `/play multiple`, `/play search`",
                # ),
                ephemeral=True,
            )


def setup(bot: commands.Bot):
    bot.add_cog(SounpadCog(bot))
