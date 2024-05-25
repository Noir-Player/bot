from disnake.ext import commands

from components.ui.views import StarsView
from objects.bot import NoirBot
from objects.exceptions import *
from validators.player import check_player_decorator


class StarsCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Избранные

    # TODO: Database

    @commands.slash_command(name="star", dm_permission=False)
    async def star(self, ctx):
        pass

    @star.sub_command(description="⭐ | избранное")
    async def open(self, ctx):

        stars = self.bot.db.stars.get_stars(ctx.author.id)

        if stars and stars.get("tracks"):
            try:
                view = StarsView(
                    songs=stars.get("tracks"),
                    player=self.bot.node.get_player(ctx.guild.id),
                )
                return await view.refresh_pages(ctx)
            except BaseException:
                return await ctx.edit_original_message(
                    embed=self.bot.embedding.get(
                        title="🟠 | Пусто",
                        description="У вас нет избранных треков",
                        color="warning",
                    ),
                    # embed=genembed(
                    #     title="", description="Похоже, у вас нет избранных треков"
                    # )
                )

        else:
            return await ctx.edit_original_message(
                embed=self.bot.embedding.get(
                    title="🟠 | Пусто",
                    description="У вас нет избранных треков",
                    color="warning",
                ),
            )

    # TODO: Database

    @check_player_decorator()
    @star.sub_command(description="🟣 | текущий трек в избранное")
    async def add(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)

        if not player.current:
            raise NoCurrent("нет текущего трека")

        if not player.current.info.isStream:
            track = player.current
            self.bot.db.stars.add_to_stars(ctx.author.id, track.model_dump())

            await ctx.send(
                embed=self.bot.embedding.get(
                    title="🟢 | Добавлено",
                    description="Звездочка добавлена в `⭐ стандартный набор`",
                    color="accent",
                ),
                # embed=genembed(
                #     title="",
                #     description="## Звездочка поставлена.\n\nПосмотрите ее в своем [профиле](https://noirplayer.su/me/stars).",
                # ),
                ephemeral=True,
            )
        else:
            return await ctx.delete_original_message()


def setup(bot: commands.Bot):
    bot.add_cog(StarsCog(bot))
