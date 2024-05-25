import disnake
from disnake.ext import commands

from components.ui.objects.queue import EmbedQueue
from objects.bot import NoirBot
from objects.exceptions import *
from validators.player import check_player_decorator


class QueueCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Избранные

    # TODO: Database

    @commands.slash_command(name="queue", dm_permission=False)
    async def queue(self, ctx):
        pass

    @check_player_decorator(with_defer=False)
    @queue.sub_command(description="⭐ | очередь")
    async def open(
        self,
        ctx,
        hidden: int = commands.Param(
            default=1,
            description="Видимость всем",
            choices=[
                disnake.OptionChoice(name="Скрыть", value=1),
                disnake.OptionChoice(name="Показать", value=0),
            ],
        ),
    ):
        await ctx.response.defer(ephemeral=bool(hidden))
        await EmbedQueue(self.bot.node).send(ctx, ephemeral=hidden)

    @check_player_decorator()
    @queue.sub_command(description="🟣 | очистить очередь")
    async def clear(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.queue.clear()
        await ctx.delete_original_message()

    @check_player_decorator()
    @queue.sub_command(description="🟣 | удалить из очереди")
    async def remove(
        self, ctx, sound: int = commands.Param(description="номер в очереди")
    ):
        player = self.bot.node.get_player(ctx.guild_id)

        try:
            await player.queue.remove(sound - 1)
        except BaseException:
            await ctx.delete_original_message()
            raise InvalidIndex(
                "нет элемента с таким индексом, или невозможно переместить позицию"
            )

        await ctx.delete_original_message()

    @check_player_decorator()
    @queue.sub_command(description="🟣 | перемешать")
    async def shuffle(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.queue.shuffle()
        await ctx.delete_original_message()

    @check_player_decorator()
    @queue.sub_command(description="🟣 | пропустить")
    async def skip(
        self,
        ctx,
        count: int = commands.Param(default=1, description="сколько нужно пропустить"),
    ):
        player = self.bot.node.get_player(ctx.guild_id)
        track = player.queue.jump(player.queue.find_position(player.current) + count)
        if track:
            await player.play(track)
        await ctx.delete_original_message()

    @check_player_decorator()
    @queue.sub_command(description="🟣 | переместить трек")
    async def move(
        self,
        ctx,
        old: int = commands.Param(description="изначальная позиция трека"),
        new: int = commands.Param(description="новая позиция трека"),
    ):
        player = self.bot.node.get_player(ctx.guild_id)
        try:
            player.queue._insert(new - 1, player.queue._queue.pop(old - 1))
        except BaseException:
            raise InvalidIndex(
                "нет элемента с таким индексом, или невозможно переместить позицию"
            )
        await ctx.delete_original_message()

    @check_player_decorator()
    @queue.sub_command(description="🟣 | пропустить (к позиции)")
    async def jump(
        self,
        ctx,
        position: int = commands.Param(
            description="позиция трека, к которому нужно переместиться"
        ),
    ):
        player = self.bot.node.get_player(ctx.guild_id)
        if position - 1 >= 0 and position <= player.queue.count:
            await player.play(player.queue.jump(position - 1))
        await ctx.delete_original_message()

    @check_player_decorator()
    @queue.sub_command(description="🟣 | ")
    async def rewind(
        self, ctx, seconds: int = commands.Param(description="количество секунд")
    ):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.seek(player.position + float(seconds * 1000))
        await player.update_controller_once()
        await ctx.delete_original_message()


def setup(bot: commands.Bot):
    bot.add_cog(QueueCog(bot))
