import disnake
from components.embeds import *
from exceptions import on_view_error
from services.database.models.star import StarDocument
from services.persiktunes import Node
from services.persiktunes.filters import *
from services.persiktunes.models import LavalinkPlaylistInfo, Playlist
from validators.player import check_player_btn

from .effects import EmbedEffects
from .playlist import EmbedPlaylist


class ContextView(disnake.ui.View):

    def __init__(self, node: Node):
        self.node = node

        super().__init__(timeout=600)

        self.api = node.rest.abstract_search

        self.on_error = on_view_error  # type: ignore

    @disnake.ui.button(emoji="<:volume_down:1396929533776498739>", row=0)
    @check_player_btn()
    async def volume_down(self, button, interaction):
        await self.node.get_player(interaction.guild_id).volume_down()  # type: ignore

    @disnake.ui.button(emoji="<:volume_up:1396929535911661648>", row=0)
    @check_player_btn()
    async def volume_up(self, button, interaction):
        await self.node.get_player(interaction.guild_id).volume_up()  # type: ignore

    @disnake.ui.button(
        emoji="<:thumb_up:1396929532384247939>",
        row=1,
    )
    @check_player_btn(with_message=True)
    async def add_to_stars(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)

        if not player.current:  # type: ignore
            return await interaction.delete_original_response()

        item = player.current  # type: ignore

        doc = await StarDocument.find_one(StarDocument.user_id == interaction.author.id)
        if not doc:
            doc = StarDocument(user_id=interaction.author.id)

        if next((obj for obj in doc.tracks if obj.info.uri == item.info.uri), None):
            return await interaction.edit_original_response(
                embed=PrimaryEmbed(description="Track already in stars! 👾")
            )

        item = item.model_copy(update={"ctx": None, "requester": None})

        doc.tracks.append(item)

        await doc.save()

        await interaction.edit_original_response(
            embed=PrimaryEmbed(description="Added to stars! 👾")
        )

    @disnake.ui.button(
        emoji="<:replace_audio:1396929530341622002>",
        row=1,
        style=disnake.ButtonStyle.gray,
    )
    @check_player_btn(with_message=True)
    async def alternative(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)

        if not player.current:  # type: ignore
            return await interaction.delete_original_response()

        raw = await self.node.get_recommendations(track=player.current, ctx=interaction, requester=interaction.author)  # type: ignore

        if not raw:
            return

        if isinstance(raw, list):
            recs = Playlist(
                tracks=raw,
                info=LavalinkPlaylistInfo(
                    name=f"Recomendations for {player.current.info.title}"  # type: ignore
                ),
                ctx=interaction,
                requester=interaction.author,
                thumbnail=player.current.info.artworkUrl,  # type: ignore
            )

        else:
            recs = raw

        await EmbedPlaylist(node=self.node, playlist=recs).send(interaction)

    @disnake.ui.button(
        emoji="<:tune:1396929527883501640>",
        row=2,
    )
    @check_player_btn(with_message=True)
    async def effects_open(self, button, interaction):
        await EmbedEffects(self.node).send(interaction)

    @disnake.ui.button(
        emoji="<:lyrics:1396929525287354410>",
        row=2,
    )
    @check_player_btn()
    async def lyrics(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        if not player.current:  # type: ignore
            return

        track = await self.api.lyrics(player.current) or player.current  # type: ignore

        if not track.lyrics or not isinstance(track.lyrics, str):
            return

        embed = SecondaryEmbed(
            title=track.info.title,
            description="```fix\n" + track.lyrics + "\n```",
        ).set_author(name=track.info.author, icon_url=track.info.artworkUrl)

        if track.album:
            embed.set_footer(text=f"Album: {track.album.name}")

        await interaction.send(
            embed=embed,
            ephemeral=True,
        )


class EmbedContext:

    def __init__(self, node: Node):
        self.node = node

    @property
    def view(self) -> disnake.ui.View:
        return ContextView(node=self.node)

    async def send(self, ctx: disnake.Interaction):
        "Use this function with `response.defer()` first"
        await ctx.edit_original_response(view=self.view)
