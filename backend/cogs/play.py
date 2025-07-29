import time

import disnake
from _logging import get_logger
from components.embeds import *
from components.modals.multiple import AddMultipleModal
from disnake.ext import commands
from entities.bot import NoirBot
from entities.node import Node
from entities.node import get_instance as get_node
from entities.player import NoirPlayer
from services.persiktunes import Playlist
from validators.player import check_player

log = get_logger("play")


class MusicCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.node: Node = get_node()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # COMMANDS
    # Group play

    @commands.slash_command(name="play")
    @commands.contexts(guild=True, private_channel=True)
    async def add(self, _):
        pass

    @check_player(with_connection=True)
    @add.sub_command(
        description="⭐⭐ | Play track from any source (ytsearch:, spsearch:, ymsearch:...)"
    )
    async def search(
        self,
        inter: disnake.ApplicationCommandInteraction,
        search: str = commands.Param(description="Type name of track... 🔍"),
    ):

        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore

        query = await self.node.search(
            search,
            ctx=inter,
            requester=inter.author,
        )

        if query is None or await player.queue.put_auto(query) == False:
            return await inter.edit_original_response(
                embed=WarningEmbed(
                    title="I cant find this track...",
                    description="Try another keywords or provide a link to the track.",
                )
            )

        if not player.current:
            if item := player.queue.get():
                await player.play(item)

        await inter.delete_original_message()  # Clean up after @check_player

    @search.autocomplete("search")
    async def autosearch(self, _, user_input) -> list:
        if not user_input:
            return []

        start = time.perf_counter()

        # if URLRegex.BASE_URL.match(user_input):
        #     return [disnake.OptionChoice(name=f"🔗 | {user_input[:95]}", value=user_input)]

        search = await self.node.search(query=user_input)

        if not search:
            return []

        if isinstance(search, Playlist):
            return [
                disnake.OptionChoice(
                    name=f"📂 | {search.info.name[:95]}", value=search.uri or user_input
                )
            ]

        result = []

        for track in search:
            result.append(
                disnake.OptionChoice(
                    name=f"🎵 | {track.info.title[:95]}",
                    value=track.info.uri,  # type: ignore
                )
            )

        end = time.perf_counter()

        log.debug(f"Autocomplete took {end - start:.3f}s")

        return result

    # TODO return radio

    @check_player(with_connection=True, with_defer=False)
    @add.sub_command(description="⭐ | Add multiple tracks")
    async def multiple(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore

        await inter.response.send_modal(AddMultipleModal(player))

    @check_player(with_connection=True)
    @add.sub_command(description="⭐ | Add playlist from noirplayer.su")
    async def playlist(
        self,
        inter: disnake.ApplicationCommandInteraction,
        playlist: str = commands.Param(description="Type to search... 🔍"),
    ):

        await inter.edit_original_message(
            embed=PrimaryEmbed(description="💔 this feature is coming soon!")
        )

        # player: NoirPlayer = self.bot.node.get_player(inter.guild_id)

        # playlist = self.bot.db.playlists.get_playlist(playlist)

        # if not playlist:
        #     return await inter.edit_original_message(
        #         embed=self.bot.embedding.get(
        #             title="🟠 | Не найдено",
        #             description="Не удалось найти плейлист",
        #             color="warning",
        #         ),
        #         # embed=type_embed(type="error", description="Неизвестный плейлист")
        #     )

        # if playlist.get("tracks"):
        #     items = []

        #     for track in playlist.get("tracks"):
        #         try:
        #             query = (
        #                 await player.search(
        #                     query=track.get("url"),
        #                     ctx=ctx,
        #                     requester=ctx.author.display_name,
        #                 )
        #             )[0]

        #             if (
        #                 not player.current
        #             ):  # чтобы не создавать задержку, играть первый найденный
        #                 player.queue.put(query)
        #                 await player.play(player.queue.get())

        #             else:
        #                 items.append(query)

        #         except:
        #             continue

        #     await player.queue.put_list(items)

        # else:
        #     return await ctx.edit_original_message(
        #         embed=self.bot.embedding.get(
        #             title="🟠 | Пусто",
        #             description="Пустой плейлист",
        #             color="warning",
        #         ),
        #         # embed=type_embed(type="error", description="Пустой плейлист")
        #     )

        # await ctx.delete_original_message()

    @playlist.autocomplete("playlist")
    async def autoplaylist(self, inter, user_input):
        # results, list = self.bot.db.playlists.get_user_playlists(inter.author.id), []

        # for playlist in results:
        #     list.append(
        #         disnake.OptionChoice(
        #             name=playlist.get("title"), value=playlist.get("uuid")
        #         )
        #     )

        # return list

        return []

    @check_player(with_connection=True)
    @add.sub_command(name="file", description="⭐ | Play track from file")
    async def file(
        self,
        inter: disnake.ApplicationCommandInteraction,
        file: disnake.Attachment = commands.Param(description="File to play ✨"),
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore

        if not file.filename.endswith(("mp3", "m4a", "wav", "ogg", "flac", "opus")):
            raise commands.UserInputError(
                "You can only play mp3, m4a, wav, ogg, flac, opus files 👾"
            )

        search = await self.node.search(
            file.url,
            ctx=inter,
            requester=inter.author,
        )

        if not search:
            raise commands.UserInputError("I cant play this file...")

        state = await player.queue.put_auto(search)

        if not player.current and state:
            await player.play(player.queue.get())  # type: ignore


def setup(bot: NoirBot):
    bot.add_cog(MusicCog(bot))
