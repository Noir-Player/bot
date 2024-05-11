import uuid as generate_id

import disnake
from disnake.interactions.modal import ModalInteraction

import services.persiktunes as persik
from helpers.dump import Dump as Build
from services.database.core import Database

build = Build()
db = Database()


class AddMultiple(disnake.ui.Modal):
    """Modal добавить несколько"""

    def __init__(
        self,
        player,
        *,
        title: str = "Добавить несколько элементов",
        custom_id: str = "add_multiple_modal",
        timeout: float = 600,
    ) -> None:
        self.player = player

        components = [
            disnake.ui.TextInput(
                label='Названия/ссылки через "; "',
                placeholder="rickroll; Gambare remix",
                custom_id="sounds",
                style=disnake.TextInputStyle.long,
            )
        ]

        super().__init__(
            title=title, components=components, custom_id=custom_id, timeout=timeout
        )

    async def callback(self, inter):
        await inter.response.defer(ephemeral=True)

        values = str(list(inter.text_values.values())[0])

        for val in values.split("; "):
            try:
                query = await self.player.get_tracks(
                    query=val, ctx=inter, search_type=persik.SearchType.ytmsearch
                )
            except BaseException:
                query = None

            if query:
                if isinstance(query, persik.Playlist):
                    await self.player.queue.put_list(query.tracks)

                    if not self.player.current and not self.player.queue.is_empty:
                        await self.player.play(self.player.queue.get())
                    # for track in query.tracks:
                    #     await self.player.queue.put(track)

                    #     if not self.player.current and not self.player.queue.is_empty:
                    #         await self.player.play(self.player.queue.get())

                else:
                    await self.player.queue.put(query[0])

                if not self.player.current and not self.player.queue.is_empty:
                    await self.player.play(self.player.queue.get())

        await inter.delete_original_response()


class AddToPlaylist(disnake.ui.Modal):
    """Modal"""

    def __init__(
        self,
        node,
        playlistview,
        uuid: str,
        *,
        title: str = "Добавить в плейлист",
        custom_id: str = "add_multiple_modal",
        timeout: float = 600,
    ) -> None:
        self.playlistview = playlistview
        self.uuid = uuid
        self.node = node

        components = [
            disnake.ui.TextInput(
                label='Названия/ссылки через "; "',
                placeholder="rickroll; Gambare remix",
                custom_id="sounds",
                style=disnake.TextInputStyle.long,
            )
        ]

        super().__init__(
            title=title, components=components, custom_id=custom_id, timeout=timeout
        )

    async def callback(self, inter):
        await inter.response.defer(ephemeral=True)

        values, result = str(list(inter.text_values.values())[0]), []

        for val in values.split("; "):
            try:
                query = await self.node.get_tracks(
                    query=val, ctx=inter, search_type=persik.SearchType.spsearch
                )
            except BaseException:
                query = None

            if query:
                if isinstance(query, persik.Playlist):
                    for track in query.tracks:
                        result.append(
                            build.track(
                                track.info, track.track_type.value, track.thumbnail
                            )
                        )
                else:
                    result.append(
                        build.track(
                            query[0].info, query[0].track_type.value, query[0].thumbnail
                        )
                    )
            else:
                await inter.edit_original_message(
                    embed=self.node.bot.embedding.get(
                        title="🟠 | Не найдено",
                        description=f"Не удалось найти `{val}`. Попробуйте поискать по названию - автору",
                        color="warning",
                    ),
                    # embed=genembed(
                    #     title=f"Не удалось найти **{val}**. Попробуйте поискать по названию - автору",
                    #     description="",
                    # )
                )

            db.playlists.add_to_playlist(self.uuid, inter.author.id, {"$each": result})

            await self.playlistview.refresh_pages(inter)


class PlaylistInfoModal(disnake.ui.Modal):
    def __init__(
        self,
        *,
        node,
        title: str = "Плейлист",
        uuid: str = None,
        forked=False,
        tracks=[],
        custom_id: str = "playlist_info_modal",
        timeout: float = 600,
    ) -> None:
        self.uuid = uuid
        self.node = node
        self.forked = forked
        self.tracks = tracks

        values = db.playlists.table.find_one({"uuid": self.uuid}) if uuid else {}

        components = [
            disnake.ui.TextInput(
                label="Имя плейлиста",
                placeholder="",
                value=values.get("name"),
                custom_id="name",
                style=disnake.TextInputStyle.short,
                max_length=40,
            ),
            disnake.ui.TextInput(
                label="Ссылка на обложку",
                placeholder="",
                value=values.get("cover"),
                custom_id="cover",
                style=disnake.TextInputStyle.short,
                required=False,
            ),
            disnake.ui.TextInput(
                label="Публичный",
                placeholder="Оставьте пустым, если нет.",
                custom_id="public",
                style=disnake.TextInputStyle.short,
                required=False,
                max_length=2,
            ),
            disnake.ui.TextInput(
                label="Описание к плейлисту",
                placeholder="`Плейлист с музыкой для учебы или отдыха` (можно использовать разметку)",
                value=values.get("notes"),
                custom_id="notes",
                style=disnake.TextInputStyle.long,
                required=False,
            ),
        ]

        # if self.uuid:
        #     components.remove(components.remove(components[2]))

        super().__init__(
            title=title, components=components, custom_id=custom_id, timeout=timeout
        )

    async def callback(self, interaction: ModalInteraction):
        await interaction.response.defer(ephemeral=True)

        values = interaction.text_values

        values = {
            "$set": {
                "title": values.get("name"),
                "thumbnail": values.get("cover", ""),
                "description": values.get("notes", ""),
                "public": bool(values.get("public")),
                "tracks": self.tracks,
                "author": {
                    "name": (
                        interaction.author.name
                        if not int(interaction.author.discriminator)
                        else f"{interaction.author.name}#{interaction.author.discriminator}"
                    ),
                    "id": interaction.author.id,
                },
            }
        }

        if not self.tracks:
            del values["$set"]["tracks"]

        if self.uuid:
            del values["$set"]["title"]
        else:
            self.uuid = str(generate_id.uuid4())

        if not values.get("$set").get("title") or not db.playlists.table.find_one(
            {"title": values.get("$set", {}).get("title")}
        ):
            db.playlists.table.update_one({"uuid": self.uuid}, values, upsert=True)

            from components.ui.views import PlaylistView

            view = PlaylistView(
                db.playlists.table.find_one({"uuid": self.uuid}), self.node
            )
            await view.refresh_pages(interaction)

        else:
            await interaction.edit_original_message(
                embed=self.node.bot.embedding.get(
                    title="🟠 | Дубликат",
                    description="Плейлист с таким именем уже существует",
                    color="warning",
                ),
                # embed=type_embed("error", "Плейлист с таким именем уже существует")
            )
