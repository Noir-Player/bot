import json

import disnake
from disnake.ext import commands

import services.persiktunes as persik
from components.ui.modals import AddMultiple
from components.ui.views import StarsView
from objects.bot import NoirBot
from objects.exceptions import *
from objects.player import NoirPlayer
from validators.player import check_player_decorator

"""Список станций по json"""

RadioNames = list(
    dict(json.load(open("data/resources/radio.json", "r", encoding="utf-8")))[
        "Зайцев.FM"
    ].keys()
)
RadioUrls = list(
    dict(json.load(open("data/resources/radio.json", "r", encoding="utf-8")))[
        "Зайцев.FM"
    ].values()
)


class Music(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool

    # -------------------------------------------------------------------------------------------------------------------------------------
    # КОМАНДЫ
    # Группа play

    """Подключается к войсу и добавляет в очередь трек"""

    @commands.slash_command(name="play", dm_permission=False)
    async def add(self, ctx):
        pass

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="🟣 | играть (вне очереди)")
    async def now(
        self, ctx, search: str = commands.Param(description="пишите для поиска... 🔍")
    ):
        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        query = await player.search(search, ctx=ctx, requester=ctx.author)

        if query.loadType == "playlist":
            await player.queue.put_list(query.data.tracks)
            await player.play(player.queue.get())

        elif query.loadType == "search":
            await player.queue.put(query.data)
            await player.play(query[0])

        elif query.loadType == "track":
            await player.play(query)

        else:
            return await ctx.edit_original_response(
                embed=self.bot.embedding.get(
                    title="🟠 | Не найдено",
                    description="Не удалось найти трек",
                    color="warning",
                ),
                # embed=type_embed(type="error", description=f"Не удалось найти")
            )

        await ctx.delete_original_message()

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="🟣 | играть")
    async def search(
        self,
        ctx,
        search: str = commands.Param(description="пишите для поиска... 🔍"),
    ):  # , replace: bool = commands.Param(description="заменить текущий трек")):

        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        query = await player.search(search, ctx=ctx, requester=ctx.author)

        if query.loadType == "playlist":
            await player.queue.put_list(query.data.tracks)

        elif query.loadType == "search":
            await player.queue.put(query.data[0])

        elif query.loadType == "track":
            await player.queue.put(query.data)

        else:
            return await ctx.edit_original_response(
                embed=self.bot.embedding.get(
                    title="🟠 | Не найдено",
                    description="Не удалось найти трек",
                    color="warning",
                ),
                # embed=type_embed(type="error", description=f"Не удалось найти")
            )

        if not player.current:
            await player.play(player.queue.get())

        await ctx.delete_original_message()

    @search.autocomplete("search")
    async def autosearch(self, inter, user_input):
        if not user_input:
            return []

        search = await self.bot.node.rest.search(
            query=user_input,
            ctx=inter,
            stype=persik.SearchType.ytmsearch,
            requester=inter.author,
        )

        result = []

        if search.loadType == "playlist":
            result.append(
                disnake.OptionChoice(
                    name=f"🎶 | {search.data.info.name}"[:100],
                    value=user_input,
                )
            )

        elif search.loadType == "search":
            for track in search.data:
                result.append(
                    disnake.OptionChoice(
                        name=f"🎵 | {track.info.title} ({track.info.author})"[:100],
                        value=track.info.uri,
                    )
                )

        elif search.loadType == "track":
            result.append(
                disnake.OptionChoice(
                    name=f"🎵 | {search.data.info.title} ({search.data.info.author})"[
                        :100
                    ],
                    value=search.data.info.uri,
                )
            )

        return result

    """Поиск радиостанции по json"""

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="🟣 | радио ZaycevFM")
    async def zaycevfm(
        self, ctx, station: str = commands.Param(description="пишите для поиска... 🔍")
    ):

        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        query = await player.search(query=station, ctx=ctx)

        await player.queue.put(query[0])

        if not player.current:
            await player.play(player.queue.get())

        await ctx.delete_original_message()

    @zaycevfm.autocomplete("station")
    async def autostation(self, inter, user_input):
        list = []

        for station in RadioNames:
            if user_input in station or not user_input:
                list.append(
                    disnake.OptionChoice(
                        name=station, value=RadioUrls[RadioNames.index(station)]
                    )
                )

        return list

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="🟣 | играть (несколько)")
    async def multiple(self, ctx):
        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        await ctx.response.send_modal(AddMultiple(player))

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="🟣 | играть (плейлист)")
    async def playlist(
        self, ctx, playlist: str = commands.Param(description="пишите для поиска... 🔍")
    ):

        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        playlist = self.bot.db.playlists.get_playlist(playlist)

        if not playlist:
            return await ctx.edit_original_message(
                embed=self.bot.embedding.get(
                    title="🟠 | Не найдено",
                    description="Не удалось найти плейлист",
                    color="warning",
                ),
                # embed=type_embed(type="error", description="Неизвестный плейлист")
            )

        if playlist.get("tracks"):
            items = []

            for track in playlist.get("tracks"):
                try:
                    query = (
                        await player.search(
                            query=track.get("url"), ctx=ctx, requester=ctx.author
                        )
                    )[0]

                    if (
                        not player.current
                    ):  # чтобы не создавать задержку, играть первый найденный
                        player.queue.put(query)
                        await player.play(player.queue.get())

                    else:
                        items.append(query)

                except:
                    continue

            await player.queue.put_list(items)

        else:
            return await ctx.edit_original_message(
                embed=self.bot.embedding.get(
                    title="🟠 | Пусто",
                    description="Пустой плейлист",
                    color="warning",
                ),
                # embed=type_embed(type="error", description="Пустой плейлист")
            )

        await ctx.delete_original_message()

    @playlist.autocomplete("playlist")
    async def autoplaylist(self, inter, user_input):
        results, list = self.bot.db.playlists.get_user_playlists(inter.author.id), []

        for playlist in results:
            list.append(
                disnake.OptionChoice(
                    name=playlist.get("title"), value=playlist.get("uuid")
                )
            )

        return list

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Избранные

    @commands.slash_command(description="🟣 | избранное", dm_permission=False)
    async def stars(self, ctx):

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

    @check_player_decorator(with_connection=True)
    @add.sub_command(name="stars", description="🟣 | играть (ваше избранное)")
    async def play_stars(self, ctx):
        stars = self.bot.db.stars.get_stars(ctx.author.id)

        if stars and stars.get("tracks"):
            player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

            for track in stars.get("tracks"):
                try:
                    query = (await player.get_tracks(query=track.get("url"), ctx=ctx))[
                        0
                    ]

                    query.thumbnail = track.get("thumbnail")

                    await player.queue.put(query)

                    if (
                        not player.current
                    ):  # чтобы не создавать задержку, играть первый найденный
                        await player.play(player.queue.get())
                except BaseException:
                    continue

            await ctx.delete_original_message()

        else:
            await ctx.edit_original_message(
                embed=self.bot.embedding.get(
                    title="🟠 | Пусто",
                    description="У вас нет избранных треков",
                    color="warning",
                ),
            )

    @check_player_decorator()
    @commands.slash_command(
        description="🟣 | звездануть текущий трек", dm_permission=False
    )
    async def star(self, ctx):
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

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Подключение онли (для веба)

    @check_player_decorator(with_connection=True)
    @commands.slash_command(
        description="🟣 | подключить Noir к войсу", dm_permission=False
    )
    async def join(self, ctx):
        self.bot.node.get_player(ctx.guild_id)

        await ctx.delete_original_message()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Если плеер стакнулся

    @check_player_decorator(with_connection=True)
    @commands.slash_command(description="🔴 | неисправен плеер?", dm_permission=False)
    async def fix(self, ctx):
        player = self.bot.node.get_player(ctx.guild.id)

        if player:
            try:
                await player.destroy()
            except BaseException:
                self.bot.node._players.pop(ctx.guild.id)
                if self.bot.node.is_connected:
                    await self._node.send(
                        method="DELETE",
                        path=player._player_endpoint_uri,
                        guild_id=ctx.guild.id,
                    )

        await ctx.delete_original_message()


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))
