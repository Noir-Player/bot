import datetime

import disnake
from disnake.ext import commands

from components.ui.objects.context import EmbedContext
from components.ui.objects.effects import EmbedEffects
from components.ui.objects.player import state
from objects.bot import NoirBot
from objects.exceptions import *
from validators.player import check_player_decorator


class PlayerCog(commands.Cog):
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
    # Плеер

    # TODO: Database

    @commands.slash_command(name="player", dm_permission=False)
    async def _player(self, ctx):
        pass

    @check_player_decorator(with_defer=False)
    @_player.sub_command(description="⭐ | текущий трек")
    async def now(
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
        player = self.bot.node.get_player(ctx.guild_id)
        await ctx.send(embed=await state(player), ephemeral=True)

    @check_player_decorator(with_defer=False)
    @_player.sub_command(description="🟣 | дополнительно")
    async def menu(
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
        await EmbedContext(self.bot.node).send(ctx, ephemeral=hidden)

    @check_player_decorator()
    @_player.sub_command(description="🟣 | корректировка звука")
    async def volume(
        self,
        ctx,
        volume: int = commands.Param(description="громкость в процентах от 0 до 500"),
    ):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.set_volume(volume)
        await ctx.delete_original_message()

    @check_player_decorator()
    @_player.sub_command(description="🟣 | пауза")
    async def pause(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        if player.is_playing or player.is_paused:
            await player.set_pause()
        await ctx.delete_original_message()

    @check_player_decorator()
    @_player.sub_command(description="🟣 | перемотать")
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
    @_player.sub_command(description="🟣 | перемотать (в секундах)")
    async def rewind(
        self, ctx, seconds: int = commands.Param(description="количество секунд")
    ):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.seek(player.position + float(seconds * 1000))
        await player.update_controller_once()
        await ctx.delete_original_message()

    @check_player_decorator()
    @_player.sub_command(description="🟣 | отключить плеер")
    async def stop(self, ctx):
        self.bot.node.get_player(ctx.guild_id)
        try:
            await ctx.guild.voice_client.disconnect(force=True)
        except BaseException:
            pass

        await ctx.delete_original_message()

    @check_player_decorator(with_connection=True)
    @_player.sub_command(description="🟣 | подключить Noir к войсу")
    async def join(self, ctx):
        await ctx.delete_original_message()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Эффекты

    @_player.sub_command_group()
    async def effects(self, ctx):
        pass

    @check_player_decorator()
    @effects.sub_command(description="⭐ | эффекты")
    async def open(
        self,
        ctx,
        hidden: bool = commands.Param(
            default=True,
            description="Видимость всем",
            choices=[
                disnake.OptionChoice(name="Скрыть", value=True),
                disnake.OptionChoice(name="Показать", value=False),
            ],
        ),
    ):
        await EmbedEffects(self.bot.node).send(ctx, ephemeral=hidden)

    @check_player_decorator()
    @effects.sub_command(description="🟣 | сбросить эффекты")
    async def reset(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)
        await player.reset_filters()
        await ctx.delete_original_message()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Контроллер

    @_player.sub_command_group()
    async def embed(self, ctx):
        pass

    @check_player_decorator()
    @embed.sub_command(description="⭐ | где эмбед плеера?")
    async def message(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)

        try:
            return await ctx.send(
                embed=self.bot.embedding.get(
                    title="🟣 | Расположение",
                    description=f"[⭐ клик]({player.controller.jump_url})",
                ),
                ephemeral=True,
            )
        except BaseException:
            return await ctx.send(
                embed=self.bot.embedding.get(
                    title="🟠 | Не найдено",
                    description="Не удалось найти контроллер плеера. Вы по-прежнему можете смотреть текущий трек через команду `/now playing`",
                    color="warning",
                ),
                ephemeral=True,
            )

    @check_player_decorator()
    @embed.sub_command(description="🟣 | повторно отправить контроллер")
    async def resend(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)

        if player:
            await player.update_controller_once(True, ctx)
        else:
            return await ctx.send(
                embed=self.bot.embedding.get(
                    title="🟠 | Не найдено",
                    description="Не удалось найти плеер. Вы по-прежнему можете смотреть текущий трек через команду `/now playing`",
                    color="warning",
                ),
                ephemeral=True,
            )


def setup(bot: commands.Bot):
    bot.add_cog(PlayerCog(bot))
