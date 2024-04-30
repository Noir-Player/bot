import asyncio

import disnake
from disnake.ext import commands

from components.ui.modals import *
from components.ui.views import PlaylistView
from objects.bot import NoirBot
from objects.exceptions import *


class Playlists(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool

    @commands.slash_command(name="playlist", dm_permission=False)
    async def playlist(self, ctx):
        pass

    @playlist.sub_command(description="создать плейлист")
    async def create(self, ctx):
        await ctx.response.send_modal(
            PlaylistInfoModal(node=self.bot.node, title="Создать плейлист")
        )

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @playlist.sub_command(description="Посмотреть плейлист")
    async def view(
        self, ctx, playlist: str = commands.Param(description="имя плейлиста")
    ):
        await ctx.response.defer(ephemeral=True)
        result = self.bot.db.playlists.table.find_one({"uuid": playlist})
        view = PlaylistView(
            result, self.bot.node, edit=(result["author"]["id"] == ctx.author.id)
        )
        await view.refresh_pages(ctx)

    @view.autocomplete("playlist")
    async def autoview(self, inter, user_input):
        results, list = (
            self.bot.db.playlists.table.find(
                {
                    "$or": [
                        {"author.id": inter.author.id},
                        {"forked": {"$elemMatch": {"$eq": inter.author.id}}},
                    ]
                }
            ),
            [],
        )

        for playlist in results:
            list.append(
                disnake.OptionChoice(
                    name=playlist.get("title"), value=playlist.get("uuid")
                )
            )

        return list

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @playlist.sub_command(description="Настроить обложку плейлиста")
    async def edit(
        self, ctx, playlist: str = commands.Param(description="имя плейлиста")
    ):
        if not self.bot.db.playlists.table.find_one({"uuid": playlist}):
            return await ctx.send(
                embed=type_embed("error", description="Неизвестный плейлист")
            )

        await ctx.response.send_modal(
            PlaylistInfoModal(
                node=self.bot.node,
                title="Изменить плейлист",
                uuid=playlist,
                forked=bool(
                    self.bot.db.playlists.table.find_one({"uuid": playlist}).get(
                        "forked"
                    )
                ),
            )
        )

    @edit.autocomplete("playlist")
    async def automanage(self, inter, user_input):
        results, list = (
            self.bot.db.playlists.table.find({"author.id": inter.author.id}),
            [],
        )

        for playlist in results:
            list.append(
                disnake.OptionChoice(
                    name=playlist.get("title"), value=playlist.get("uuid")
                )
            )

        return list

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @playlist.sub_command(description="Удалить плейлист")
    async def delete(
        self, ctx, playlist: str = commands.Param(description="имя плейлиста")
    ):
        playlist = self.bot.db.playlists.table.find_one({"uuid": playlist})

        if not playlist:
            return await ctx.send(
                embed=type_embed("error", description="Неизвестный плейлист")
            )

        await ctx.response.send_message(
            "**Вы точно хотите удалить плейлист из библиотеки?**",
            ephemeral=True,
            components=[
                disnake.ui.Button(label="да, удалить", style=disnake.ButtonStyle.red)
            ],
        )
        try:
            await self.bot.wait_for("button_click", timeout=20)
        except asyncio.TimeoutError:
            await ctx.delete_original_response()
        except BaseException:
            pass
        else:
            self.bot.db.playlists.delete_playlist(playlist.get("uuid"), ctx.author.id)

        await ctx.delete_original_response()

        await ctx.send(
            embed=type_embed("success", "**Плейлист был удален**"), ephemeral=True
        )

    @delete.autocomplete("playlist")
    async def autodelete(self, inter, user_input):
        results, list = (
            self.bot.db.playlists.table.find(
                {
                    "$or": [
                        {"author.id": inter.author.id},
                        {"forked": {"$elemMatch": {"$eq": inter.author.id}}},
                    ]
                }
            ),
            [],
        )

        for playlist in results:
            list.append(
                disnake.OptionChoice(
                    name=playlist.get("title"), value=playlist.get("uuid")
                )
            )

        return list

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @playlist.sub_command(description="Удалить треки из плейлиста")
    async def clear(
        self, ctx, playlist: str = commands.Param(description="имя плейлиста")
    ):
        playlist = self.bot.db.playlists.table.find_one({"uuid": playlist})

        if not playlist:
            return await ctx.send(
                embed=type_embed("error", description="Неизвестный плейлист")
            )

        await ctx.response.send_message(
            "**Вы точно хотите очистить плейлист?**",
            ephemeral=True,
            components=[disnake.ui.Button(label="да", style=disnake.ButtonStyle.red)],
        )
        try:
            await self.bot.wait_for("button_click", timeout=20)
        except asyncio.TimeoutError:
            await ctx.delete_original_response()
        except BaseException:
            pass
        else:
            self.bot.db.playlists.clear_playlist(playlist.get("uuid"), ctx.author.id)

        await ctx.delete_original_response()

        await ctx.send(
            embed=type_embed("success", "**Плейлист был очищен**"), ephemeral=True
        )

    @clear.autocomplete("playlist")
    async def autoclear(self, inter, user_input):
        results, list = (
            self.bot.db.playlists.table.find({"author.id": inter.author.id}),
            [],
        )

        for playlist in results:
            list.append(
                disnake.OptionChoice(
                    name=playlist.get("title"), value=playlist.get("uuid")
                )
            )

        return list

    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @playlist.sub_command(description="Удалить трек из плейлиста")
    async def remove(
        self,
        ctx,
        playlist: str = commands.Param(description="имя плейлиста"),
        track: int = commands.Param(description="номер трека"),
    ):
        await ctx.response.defer(ephemeral=True)

        playlist = self.bot.db.playlists.table.find_one({"uuid": playlist})

        if not playlist:
            return await ctx.send(
                embed=type_embed("error", description="Неизвестный плейлист")
            )

        if playlist["author"]["id"] == ctx.author.id:
            self.bot.db.playlists.table.update_one(
                {"uuid": playlist.get("uuid")}, {"$unset": {f"tracks.{track}": 1}}
            )
            self.bot.db.playlists.table.update_one(
                {"uuid": playlist.get("uuid")}, {"$pull": {f"tracks": None}}
            )

        await ctx.delete_original_response()

    @remove.autocomplete("playlist")
    async def autoremove_playlist(self, inter, user_input):
        results, list = (
            self.bot.db.playlists.table.find({"author.id": inter.author.id}),
            [],
        )

        for playlist in results:
            list.append(
                disnake.OptionChoice(
                    name=playlist.get("title"), value=playlist.get("uuid")
                )
            )

        return list

    # @remove.autocomplete("track")
    # async def autoremove_track(self, inter, user_input):
    #     results, list = table("playlists").find({"author.id": inter.author.id}), []

    #     for playlist in results:
    #         list.append(disnake.OptionChoice(name=playlist.get("title"), value=playlist.get("uuid")))

    #     return list


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def setup(bot: commands.Bot):
    bot.add_cog(Playlists(bot))
