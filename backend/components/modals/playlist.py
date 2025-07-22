from asyncio import run_coroutine_threadsafe
from typing import List

import disnake
from components.embeds import WarningEmbed
from disnake.interactions.modal import ModalInteraction
from services.database.models.playlist import PlaylistDocument
from services.persiktunes.models import LavalinkPlaylistInfo, Track


class PlaylistInfoModal(disnake.ui.Modal):
    def __init__(
        self,
        *,
        node,
        title: str = "Playlist",
        uuid: str | None = None,  # used for editing existing playlist
        forked: bool = False,
        tracks: List[Track] | None = None,
        custom_id: str = "playlist_info_modal",
        timeout: float = 600,
    ) -> None:
        self.uuid = uuid
        self.node = node
        self.forked = forked
        self.tracks = tracks

        fetched = (
            run_coroutine_threadsafe(
                PlaylistDocument.find_one(PlaylistDocument.uuid == uuid),  # type: ignore
                node.bot.loop,
            ).result()
            if uuid
            else None
        )

        components = [
            disnake.ui.TextInput(
                label="Name",
                placeholder="",
                value=fetched.info.name if fetched else None,
                custom_id="name",
                style=disnake.TextInputStyle.short,
                max_length=40,
            ),
            disnake.ui.TextInput(
                label="URL to cover image",
                placeholder="",
                value=fetched.thumbnail if fetched else None,
                custom_id="thumbnail",
                style=disnake.TextInputStyle.short,
                required=False,
            ),
            disnake.ui.TextInput(
                label="Public",
                placeholder="Leave empty for make private",
                value=("yep" if fetched.public else None) if fetched else None,
                custom_id="public",
                style=disnake.TextInputStyle.short,
                required=False,
            ),
            disnake.ui.TextInput(
                label="Description",
                placeholder="My first **cool** playlist",
                value=fetched.description if fetched else None,
                custom_id="description",
                style=disnake.TextInputStyle.long,
                required=False,
            ),
        ]

        super().__init__(
            title=title, components=components, custom_id=custom_id, timeout=timeout
        )

        if fetched:
            self.fetched = fetched  # Do not searching twice

    async def callback(self, interaction: ModalInteraction):
        await interaction.response.defer(ephemeral=True)

        values = interaction.text_values

        if (
            self.fetched
            or not await PlaylistDocument.find(
                PlaylistDocument.info.name == values.get("name")
            ).to_list()
        ):
            if not self.fetched:
                playlist = PlaylistDocument(
                    info=LavalinkPlaylistInfo(
                        name=values["name"],
                    ),
                    user_id=interaction.author.id,
                    thumbnail=values.get("thumbnail"),
                    description=values.get("description"),
                    public=bool(values.get("public")),
                    tracks=self.tracks if self.tracks else [],
                )

                await playlist.save()

            else:
                playlist = self.fetched

            from components.views.playlist import EmbedPlaylist

            await EmbedPlaylist(self.node, playlist).send(interaction)

        else:
            await interaction.edit_original_response(
                embed=WarningEmbed(
                    title="Duplicate!", description="Whoa, that playlist name is taken!"
                ),
            )
