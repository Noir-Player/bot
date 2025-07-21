import disnake
from components.views.queue import EmbedQueue
from disnake.ext import commands
from entities.bot import NoirBot
from entities.node import Node
from entities.node import get_instance as get_node
from entities.player import NoirPlayer
from exceptions import *
from validators.player import check_player_decorator


class QueueCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.node: Node = get_node()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Queue

    # TODO: Database

    @commands.slash_command()
    @commands.contexts(guild=True)
    async def queue(self, _):
        pass

    @check_player_decorator(with_defer=False)
    @queue.sub_command(description="👾👾 | Queue")
    async def open(
        self,
        inter: disnake.ApplicationCommandInteraction,
        hidden: int = commands.Param(
            default=0,
            description="Must I show it to you only?",
            choices=[
                disnake.OptionChoice(name="Yes", value=1),
                disnake.OptionChoice(name="No", value=0),
            ],
        ),
    ):
        await inter.response.defer(ephemeral=bool(hidden))
        await EmbedQueue(self.node).send(inter)

    @check_player_decorator()
    @queue.sub_command(description="👾 | Clear queue")
    async def clear(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore
        player.queue.clear()
        await inter.delete_original_message()

    @check_player_decorator()
    @queue.sub_command(description="👾 | Remove track from queue")
    async def remove(
        self,
        inter: disnake.ApplicationCommandInteraction,
        position: int = commands.Param(description="Position of track to remove"),
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore

        try:
            await player.queue.remove(position - 1)
        except BaseException:
            await inter.delete_original_message()
            raise InvalidIndex("💔 I can't find track with position: " + str(position))

        await inter.delete_original_message()

    @check_player_decorator()
    @queue.sub_command(description="👾 | Shuffle queue")
    async def shuffle(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore
        player.queue.shuffle()
        await inter.delete_original_message()

    @check_player_decorator()
    @queue.sub_command(description="👾 | Skip track")
    async def skip(
        self,
        inter: disnake.ApplicationCommandInteraction,
        count: int = commands.Param(default=1, description="Count of tracks to skip"),
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore
        track = player.queue.jump(player.queue.find_position(player.current) + count)  # type: ignore
        if track:
            await player.play(track)
        await inter.delete_original_message()

    @check_player_decorator()
    @queue.sub_command(description="👾 | Move track")
    async def move(
        self,
        inter: disnake.ApplicationCommandInteraction,
        old: int = commands.Param(description="Old position of track"),
        new: int = commands.Param(description="New position of track"),
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore
        try:
            player.queue._insert(new - 1, player.queue._queue.pop(old - 1))
        except BaseException:
            raise InvalidIndex(
                "I can't find track with position, or element are not movable"
            )
        await inter.delete_original_message()

    @check_player_decorator()
    @queue.sub_command(description="👾 | Skip to position")
    async def jump(
        self,
        inter: disnake.ApplicationCommandInteraction,
        position: int = commands.Param(description="Position of track to play"),
    ):
        player: NoirPlayer = self.node.get_player(inter.guild_id)  # type: ignore
        if position - 1 >= 0 and position <= player.queue.count:
            await player.play(player.queue.jump(position - 1))  # type: ignore
        await inter.delete_original_message()


def setup(bot: NoirBot):
    bot.add_cog(QueueCog(bot))
