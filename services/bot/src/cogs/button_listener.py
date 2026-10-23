import disnake
from components.containers.soundpad import MoreMenu
from components.embeds import PrimaryEmbed
from disnake.ext import commands
from entities.bot import NoirBot
from entities.config import BotConfig
from entities.config import get_instance as get_config
from entities.node import get_instance as get_node
from entities.player import NoirPlayer
from exceptions import *
from services.database.models.star import StarDocument
from services.persiktunes import LoopMode
from validators.player import check_player


class ButtonListenerCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot

        self.config: BotConfig = get_config()

        self.node = get_node()

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        self.bot._log.debug(f"button {inter.component.custom_id} clicked")

        if inter.component.custom_id.endswith("button_callback"):
            await inter.response.defer(ephemeral=True)

            await getattr(self, inter.component.custom_id)(inter)

    @check_player()
    async def loop_button_callback(self, interaction):
        player: NoirPlayer = self.node.get_player(interaction.guild.id)  # type: ignore
        if player.queue.loop_mode == LoopMode.QUEUE:
            await player.queue.set_loop_mode(LoopMode.TRACK)
        elif player.queue.loop_mode == LoopMode.TRACK:
            await player.queue.set_loop_mode()
        else:
            await player.queue.set_loop_mode(LoopMode.QUEUE)

    @check_player()
    async def previous_button_callback(self, interaction):
        player: NoirPlayer = self.node.get_player(interaction.guild.id)  # type: ignore

        if player.current:
            if player.queue.loop_mode != LoopMode.TRACK:
                track = player.queue.prev()
                if track:
                    await player.play(track)
            else:
                raise TrackIsLooping("You can't skip track, when it's looping")

    @check_player()
    async def play_pause_button_callback(self, interaction):
        player: NoirPlayer = self.node.get_player(interaction.guild.id)  # type: ignore

        if player.current:
            await player.set_pause()

    @check_player()
    async def next_button_callback(self, interaction):
        player: NoirPlayer = self.node.get_player(interaction.guild.id)  # type: ignore

        if player.queue.loop_mode != LoopMode.TRACK:
            if item := player.queue.next():
                await player.play(item)
        else:
            raise TrackIsLooping("You can't skip track, when it's looping")

    @check_player()
    async def more_menu_button_callback(self, interaction: disnake.MessageInteraction):
        if interaction.guild:
            player: NoirPlayer = self.node.get_player(interaction.guild.id)  # type: ignore

            await interaction.send(view=MoreMenu(player), ephemeral=True)

    @check_player()
    async def add_to_star_button_callback(
        self, interaction: disnake.MessageInteraction
    ) -> None:
        if not interaction.guild:
            return

        player: NoirPlayer = self.node.get_player(interaction.guild.id)  # type: ignore

        if not player.current:  # type: ignore
            return await interaction.delete_original_response()

        item = player.current  # type: ignore

        doc = await StarDocument.find_one(StarDocument.user_id == interaction.author.id)
        if not doc:
            doc = StarDocument(user_id=interaction.author.id)

        if next((obj for obj in doc.tracks if obj.info.uri == item.info.uri), None):
            return await interaction.send(
                embed=PrimaryEmbed(description="Track already in stars! 👾"),
                ephemeral=True,
            )

        item = item.model_copy(update={"ctx": None, "requester": None})

        doc.tracks.append(item)

        await doc.save()

        await interaction.send(
            embed=PrimaryEmbed(
                description=f"Track `{item.info.title}` added to stars! 👾"
            ),
            ephemeral=True,
        )

    @check_player()
    async def start_autoplay_button_callback(
        self, interaction: disnake.MessageInteraction
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        # TODO


def setup(bot: NoirBot):
    bot.add_cog(ButtonListenerCog(bot))
