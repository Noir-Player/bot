import json
import time

import disnake
from disnake.ext import commands

from components.modals.multiple import AddMultiple
from objects.bot import NoirBot
from objects.exceptions import *
from objects.player import NoirPlayer
from validators.player import check_player_decorator

"""Список станций по json"""

radio = json.load(open("data/resources/radio.json", "r", encoding="utf-8"))["Record"]


class MusicCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool

    # -------------------------------------------------------------------------------------------------------------------------------------
    # КОМАНДЫ
    # Группа play

    @commands.slash_command(name="play", dm_permission=False)
    async def add(self, ctx):
        pass

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="⭐ | играть")
    async def search(
        self,
        ctx,
        search: str = commands.Param(description="Поиск трека или плейлиста... 🔍"),
    ):

        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        query = await player.node.rest.abstract_search.search(
            search,
            ctx=ctx,
            requester=ctx.author.display_name,
        )

        if await player.queue.put_auto(query) == False:
            return await ctx.edit_original_response(
                embed=self.bot.embedding.get(
                    title="🟠 | Не найдено",
                    description=("Не удалось найти трек. "),
                    color="warning",
                    image="https://noirplayer.su/cdn/ambient.gif",
                ),
            )

        if not player.current:
            await player.play(player.queue.get())

        await ctx.delete_original_message()

    @search.autocomplete("search")
    async def autosearch(self, inter, user_input):
        if not user_input:
            return []

        start = time.perf_counter()

        # if persik.URLRegex.BASE_URL.match(user_input):
        #     return [disnake.OptionChoice(name=f"🔎 | {user_input}", value=user_input)]

        # search = await self.bot.node.rest.ytmclient.complete_search(query=user_input)

        # result = []

        # for object in search:
        #     names = []

        #     try:
        #         if object["resultType"] in ("song", "video"):
        #             emoji = "⭐"
        #             (
        #                 names.append(", ".join([i["name"] for i in object["artists"]]))
        #                 if object["artists"]
        #                 else None
        #             )

        #             uri = "https://youtube.com/watch?v=" + object["videoId"]

        #         elif object["resultType"] == "playlist":
        #             emoji = "📁"
        #             (names.append(object["author"]) if object.get("author") else None)

        #             uri = (
        #                 "https://music.youtube.com/playlist?list="
        #                 + object["browseId"][2:]
        #             )

        #         else:
        #             continue
        #     except:
        #         continue

        #     names.append(object["title"])

        #     result.append(
        #         disnake.OptionChoice(
        #             name=(f"{emoji} | " + " - ".join(names))[:100],
        #             value=uri,
        #         )
        #     )

        result = []

        for suggestion in await self.bot.node.rest.abstract_search.search_suggestions(
            user_input
        ):
            result.append(
                disnake.OptionChoice(name=f"🔎 | {suggestion}", value=suggestion)
            )

        if not result:
            result = [disnake.OptionChoice(name=f"🔎 | {user_input}", value=user_input)]

        end = time.perf_counter()

        self.bot._log.debug(f"Autocomplete took {end - start:.3f}s")

        return result

    """Поиск радиостанции по json"""

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="🟣 | радиостанции")
    async def radio(
        self, ctx, station: str = commands.Param(description="пишите для поиска... 🔍")
    ):

        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        query = (
            await player.search(
                query=station, ctx=ctx, requester=ctx.author.display_name
            )
        ).data

        if not query.info.isStream:
            return await ctx.edit_original_response(
                embed=self.bot.embedding.get(
                    title="🟠 | Не найдено",
                    description=("Нет такой радиостанции."),
                    color="warning",
                ),
            )

        player.queue.set_primary(query)

        await player.play(player.queue.primary)

        await ctx.delete_original_message()

    @radio.autocomplete("station")
    async def autostation(self, inter, user_input):
        list = []

        i = 0
        for name, url in radio.items():
            if user_input.lower() in name.lower() or not user_input:
                list.append(
                    disnake.OptionChoice(
                        name=f"📻 | {name}",
                        value=url,
                    )
                )

                i += 1

                if i == 19:
                    break

        return list

    # TODO : Database

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="🟣 | играть (несколько)")
    async def multiple(self, ctx):
        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        await ctx.response.send_modal(AddMultiple(player))

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="🟣 | играть (плейлист на noirplayer.su)")
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
                            query=track.get("url"),
                            ctx=ctx,
                            requester=ctx.author.display_name,
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


def setup(bot: commands.Bot):
    bot.add_cog(MusicCog(bot))
