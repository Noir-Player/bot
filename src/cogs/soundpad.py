from disnake.ext import commands

from objects.bot import NoirBot
from validators.player import check_player_decorator


class SounpadCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @check_player_decorator()
    @commands.slash_command(
        description="🟣 | где контроллер плеера?",
        dm_permission=False,
    )
    async def soundpad(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)

        try:
            return await ctx.send(
                embed=self.bot.embedding.get(
                    title="🟣 | Расположение",
                    description=f"[⭐ клик]({player.controller.jump_url})",
                ),
                ephemeral=True,
            )
        except BaseException:
            return await ctx.send(
                embed=self.bot.embedding.get(
                    title="🟠 | Не найдено",
                    description="Не удалось найти контроллер плеера. Вы по-прежнему можете смотреть текущий трек через команду `/now playing`",
                    color="warning",
                ),
                ephemeral=True,
            )

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @check_player_decorator()
    @commands.slash_command(
        description="🟣 | повторно отправить контроллер", dm_permission=False
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
                ephemeral=True,
            )


def setup(bot: commands.Bot):
    bot.add_cog(SounpadCog(bot))
