from datetime import datetime

from disnake.ext import commands

from classes.Bot import NoirBot
from classes.Exceptions import InvalidIndex
from classes.Player_view import state

from ..components.ui.views import ActionsView, FiltersView, QueueView
from ..validators.player import check_player_decorator


class AlternativeCog(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool

    def _calculate_seconds(self, time_code):
        if len(time_code) == 5:
            time_format = "%M:%S"
        elif len(time_code) == 8:
            time_format = "%H:%M:%S"
        else:
            return None

        try:
            time_obj = datetime.strptime(time_code, time_format)
            seconds = (time_obj - datetime(1900, 1, 1)).total_seconds()
            return seconds
        except BaseException:
            return None

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Альтернативные команды

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Статичные команды

    @check_player_decorator()
    @commands.slash_command(description="Текущий sound", dm_permission=False)
    async def np(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await ctx.send(embed=await state(player), ephemeral=True)

    @check_player_decorator()
    @commands.slash_command(description="Очередь", dm_permission=False)
    async def queue(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        view = QueueView(player)
        await view.refresh_pages(ctx)

    @check_player_decorator()
    @commands.slash_command(description="Контекстное меню", dm_permission=False)
    async def menu(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await ctx.send(ephemeral=True, view=ActionsView(player))

    @check_player_decorator()
    @commands.slash_command(description="Очистить очередь", dm_permission=False)
    async def clear(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.queue.clear()
        await ctx.delete_original_message()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Плеер

    @check_player_decorator()
    @commands.slash_command(description="Громкость", dm_permission=False)
    async def volume(
        self,
        ctx,
        volume: int = commands.Param(description="громкость в процентах от 0 до 500"),
    ):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.set_volume(volume)
        await ctx.delete_original_message()

    @check_player_decorator()
    @commands.slash_command(description="Остановить/восстановить", dm_permission=False)
    async def pause(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        if player.is_playing or player.is_paused:
            await player.set_pause(not player.is_paused)
        await ctx.delete_original_message()

    @check_player_decorator()
    @commands.slash_command(description="Перемотать на тайм-код", dm_permission=False)
    async def seek(
        self,
        ctx,
        timecode: str = commands.Param(
            description="код в виде ss:mm или ss:mm:hh", min_length=5, max_length=8
        ),
    ):
        player = self.bot.node.get_player(ctx.guild_id)
        mseconnds = self._calculate_seconds(timecode)
        if mseconnds:
            await player.seek(mseconnds * 1000)
            await player.update_bar_once()
        await ctx.delete_original_message()

    @check_player_decorator()
    @commands.slash_command(description="Перемотать на n секунд", dm_permission=False)
    async def rewind(
        self, ctx, seconds: int = commands.Param(description="количество секунд")
    ):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.seek(player.position + float(seconds * 1000))
        await player.update_bar_once()
        await ctx.delete_original_message()

    @check_player_decorator()
    @commands.slash_command(description="Остановить очередь", dm_permission=False)
    async def stop(self, ctx):
        self.bot.node.get_player(ctx.guild_id)
        try:
            await ctx.guild.voice_client.disconnect(force=True)
        except BaseException:
            pass

        await ctx.delete_original_message()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Очередь

    @check_player_decorator()
    @commands.slash_command(description="Удалить звук из очереди", dm_permission=False)
    async def remove(
        self, ctx, sound: int = commands.Param(description="позиция звука из очереди")
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
    @commands.slash_command(description="Перемешать очередь", dm_permission=False)
    async def shuffle(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.queue.shuffle()
        await ctx.delete_original_message()

    @commands.slash_command(dm_permission=False)
    async def skip(self, ctx):
        pass

    @check_player_decorator()
    @skip.sub_command(description="Пропустить sound")
    async def to(
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
    @commands.slash_command(description="Переместить sound", dm_permission=False)
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
    @commands.slash_command(description="Переместить позицию", dm_permission=False)
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

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Эквалайзер

    @check_player_decorator()
    @commands.slash_command(description="Открыть эквалайзер", dm_permission=False)
    async def eq(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await ctx.send(view=FiltersView(player=player))

    @check_player_decorator()
    @commands.slash_command(description="Сбросить фильтры", dm_permission=False)
    async def reset(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.reset_filters(fast_apply=True)
        await ctx.delete_original_message()


def setup(bot: commands.Bot):
    bot.add_cog(AlternativeCog(bot))
