from datetime import datetime

from disnake.ext import commands

from components.ui.player import state
from components.ui.views import ActionsView, FiltersView, QueueView
from objects.bot import NoirBot
from objects.exceptions import InvalidIndex
from validators.player import check_player_decorator


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
    # Статичные команды

    @commands.slash_command(dm_permission=False)
    async def now(self, ctx):
        pass

    @check_player_decorator()
    @now.sub_command(description="🟣 | текущий трек")
    async def playing(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await ctx.send(embed=await state(player), ephemeral=True)

    @check_player_decorator()
    @commands.slash_command(description="🟣 | очередь", dm_permission=False)
    async def queue(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        view = QueueView(player)
        await view.refresh_pages(ctx)

    @check_player_decorator()
    @commands.slash_command(description="🟣 | дополнительно", dm_permission=False)
    async def menu(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await ctx.send(ephemeral=True, view=ActionsView(player))

    @check_player_decorator()
    @commands.slash_command(description="🟣 | очистить очередь", dm_permission=False)
    async def clear(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.queue.clear()
        await ctx.delete_original_message()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Плеер

    @check_player_decorator()
    @commands.slash_command(description="🟣 | корректировка звука", dm_permission=False)
    async def volume(
        self,
        ctx,
        volume: int = commands.Param(description="громкость в процентах от 0 до 500"),
    ):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.set_volume(volume)
        await ctx.delete_original_message()

    @check_player_decorator()
    @commands.slash_command(description="🟣 | пауза", dm_permission=False)
    async def pause(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        if player.is_playing or player.is_paused:
            await player.set_pause()
        await ctx.delete_original_message()

    @check_player_decorator()
    @commands.slash_command(description="🟣 | перемотать", dm_permission=False)
    async def seek(
        self,
        ctx,
        timecode: str = commands.Param(
            description="таймкод 00:00 или 00:00:00", min_length=5, max_length=8
        ),
    ):
        player = self.bot.node.get_player(ctx.guild_id)
        mseconnds = self._calculate_seconds(timecode)
        if mseconnds:
            await player.seek(mseconnds * 1000)
            await player.update_controller_once()
        await ctx.delete_original_message()

    @check_player_decorator()
    @commands.slash_command(
        description="🟣 | перемотать (в секундах)", dm_permission=False
    )
    async def rewind(
        self, ctx, seconds: int = commands.Param(description="количество секунд")
    ):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.seek(player.position + float(seconds * 1000))
        await player.update_controller_once()
        await ctx.delete_original_message()

    @check_player_decorator()
    @commands.slash_command(description="🟣 | отключить плеер", dm_permission=False)
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
    @commands.slash_command(description="🟣 | удалить из очереди", dm_permission=False)
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
    @commands.slash_command(description="🟣 | перемешать", dm_permission=False)
    async def shuffle(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.queue.shuffle()
        await ctx.delete_original_message()

    @commands.slash_command(dm_permission=False)
    async def skip(self, ctx):
        pass

    @check_player_decorator()
    @skip.sub_command(description="🟣 | пропустить")
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
    @commands.slash_command(description="🟣 | переместить трек", dm_permission=False)
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
    @commands.slash_command(
        description="🟣 | пропустить (к позиции)", dm_permission=False
    )
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

    @commands.slash_command(dm_permission=False)
    async def effects(self, ctx):
        pass

    @check_player_decorator()
    @effects.sub_command(description="🟣 | эквалайзер")
    async def open(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await ctx.send(view=FiltersView(player=player))

    @check_player_decorator()
    @effects.sub_command(description="🟣 | сбросить фильтры")
    async def reset(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.reset_filters()
        await ctx.delete_original_message()


def setup(bot: commands.Bot):
    bot.add_cog(AlternativeCog(bot))
