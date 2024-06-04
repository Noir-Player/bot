import disnake

from objects.bot import NoirBot
from services.persiktunes import Node, Track
from validators.player import check_player_btn_decorator


class TrackButtons(disnake.ui.View):

    def __init__(self, track: Track, node: Node, message: disnake.Message):
        self.track = track
        self.node = node
        self.bot: NoirBot = node.bot

        self.message = message

        super().__init__(timeout=600)

        self.api = node.rest.abstract_search

    @disnake.ui.button(
        emoji="<:playlist_add_primary:1239115838557126678>",
        row=0,
    )
    @check_player_btn_decorator(with_connection=True)
    async def add(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        await player.queue.put(self.track)
        if not player.current:
            await player.play(player.queue.get())

    @disnake.ui.button(
        emoji="<:autoplay_primary:1239113693690859564>",
        row=0,
    )
    @check_player_btn_decorator(with_connection=True)
    async def start_autoplay(self, button, interaction):
        player = self.node.get_player(interaction.guild_id)
        await player.queue.start_autoplay(self.track)

    @disnake.ui.button(
        emoji="<:lyrics_primary:1239113708203020368>",
        row=0,
    )
    async def lyrics(self, button, interaction):
        self.track = await self.api.lyrics(self.track)

        await interaction.send(
            embed=self.bot.embedding.get(
                author_name=self.track.info.title,
                author_icon=self.track.info.artworkUrl,
                description="```fix\n" + self.track.lyrics + "\n```",
                footer=f"Album: {self.track.album.name}" if self.track.album else "",
                color="info",
            ),
            ephemeral=True,
        )

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
        self.bot: NoirBot = node.bot

    def embed(self) -> disnake.Embed:
        """Return embed with track info"""

        image = (
            self.track.info.artworkUrl
            if self.track.info.artworkUrl
            else f"https://mir-s3-cdn-cf.behance.net/project_modules/disp/a11a4893658133.5e98adbead405.gif"
        )

        embed = self.bot.embedding.get(
            description=self.track.info.author,
            author_name=self.track.info.title,
            author_icon=self.track.info.artworkUrl,
            image=image,
            description=f"<:alternate_email_primary:1239117898912497734> **{self.track.info.author}**",
            footer=f"Album: {self.track.album.name}" if self.track.album else "",
        )

        return embed

    def view(self, message: disnake.Message) -> disnake.ui.View:
        """Return view of track (buttons)"""
        return TrackButtons(track=self.track, node=self.node, message=message)

    async def send(self, ctx: disnake.Interaction, ephemeral: bool = False):
        """Send embed with track info"""
        await ctx.edit_original_response(embed=self.embed())

        message = await ctx.original_response()

        view = self.view(message)

        await message.edit(view=view)
