import disnake
from components.embeds import *
from services.persiktunes import Node, Track
from validators.player import check_player_btn


class TrackButtons(disnake.ui.View):

    def __init__(self, track: Track, node: Node, message: disnake.Message):
        self.track = track
        self.node = node

        self.message = message

        super().__init__(timeout=600)

        self.api = node.rest.abstract_search

    @disnake.ui.button(
        emoji="<:playlist_add_primary:1239115838557126678>",
        row=0,
    )
    @check_player_btn(with_connection=True)
    async def add(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)  # type: ignore

        await player.queue.put_auto(self.track)  # type: ignore

        if not player.current:  # type: ignore
            if item := player.queue.get():  # type: ignore
                await player.play(item)  # type: ignore

    @disnake.ui.button(
        emoji="<:autoplay_primary:1239113693690859564>",
        row=0,
    )
    @check_player_btn(with_connection=True)
    async def start_autoplay(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)  # type: ignore
        await player.queue.start_autoplay(self.track)  # type: ignore

    @disnake.ui.button(
        emoji="<:lyrics_primary:1239113708203020368>",
        row=0,
    )
    async def lyrics(self, button, interaction):
        self.track = await self.api.lyrics(self.track) or self.track

        if isinstance(self.track.lyrics, str):
            embed = SecondaryEmbed(
                title=self.track.info.title,
                description="```fix\n" + self.track.lyrics + "\n```",
            ).set_author(
                name=self.track.info.author, icon_url=self.track.info.artworkUrl
            )

            if self.track.album:
                embed.set_footer(text=f"Album: {self.track.album.name}")

            await interaction.send(embed=embed, ephemeral=True)

    @disnake.ui.button(
        emoji="<:cancel_primary:1241734921454616629>",
        row=0,
    )
    async def close(self, button, interaction):
        await self.message.delete()

    async def on_timeout(self):
        pass


class EmbedTrack:

    def __init__(self, track: Track, node: Node):
        self.track = track
        self.node = node

    def embed(self) -> disnake.Embed:
        image = (
            self.track.info.artworkUrl
            if self.track.info.artworkUrl
            else f"https://i.pinimg.com/originals/41/59/a2/4159a258b81478d2f288a5d675451321.gif"
        )

        embed = (
            PrimaryEmbed(
                description=self.track.info.author,
            )
            .set_author(
                name=self.track.info.title,
                icon_url=self.track.info.artworkUrl,
            )
            .set_image(image)
        )

        if self.track.album:
            embed.set_footer(text=f"Album: {self.track.album.name}")

        return embed

    def view(self, message: disnake.Message) -> disnake.ui.View:
        return TrackButtons(track=self.track, node=self.node, message=message)

    async def send(self, ctx: disnake.Interaction):
        "Use this function with `response.defer()` first"
        await ctx.edit_original_response(embed=self.embed())

        message = await ctx.original_response()

        view = self.view(message)

        await message.edit(view=view)
