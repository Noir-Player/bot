import json
import disnake
import pomice
from disnake.ext import commands
from classes.Bot import NoirBot

from classes.Exceptions import *
from classes.Player import NoirPlayer
from checks.check_player import check_player_decorator
from cogs.components.ui.modals import AddMultiple
from cogs.components.ui.views import StarsView
from utils.embeds import *
from utils.printer import *


"""Список станций по json"""

RadioNames = list(
    dict(json.load(open("json-obj/radio.json", "r", encoding="utf-8")))[
        "Зайцев.FM"
    ].keys()
)
RadioUrls = list(
    dict(json.load(open("json-obj/radio.json", "r", encoding="utf-8")))[
        "Зайцев.FM"
    ].values()
)


class Music(commands.Cog):
    def __init__(self, bot: NoirBot):
        self.bot = bot
        self.pool = bot.pool

    # -------------------------------------------------------------------------------------------------------------------------------------
    # ИВЕНТЫ ЛАВАЛИНКА

    @commands.Cog.listener()
    async def on_pomice_track_start(self, player: NoirPlayer, track: pomice.Track):
        await player.edit_bar(track.ctx)

        if player.update_bar.is_running():
            player.update_bar.restart()
        else:
            player.update_bar.start()

        if not track.is_stream:
            try:
                player.update_bar.change_interval(
                    minutes=(track.length / 1000 / 60 / 20)
                )
            except BaseException:
                pass
        else:
            try:
                player.update_bar.stop()
            except BaseException:
                pass

    """Если саундбара нет, его измененение не имеет смысла"""

    """Прослушивание окончания трека"""

    @commands.Cog.listener()
    async def on_pomice_track_end(
        self, player: NoirPlayer, track: pomice.Track, reason
    ):
        player.update_bar.stop()  # останавливаем обновление плеера

        if not player.queue.is_empty and reason in [
            "FINISHED",
            "finished",
            "STOPPED",
            "stopped",
        ]:  # если трек завершился самостоятельно или использовано skip
            sound = player.queue.get()  # получаем трек
            if sound:  # если очередь не пуста
                return await player.play(sound)

        elif reason in ["REPLACED", "replaced"]:  # если трек был заменен
            return

        await player.queue.clear()

        return await player.edit_bar(
            track.ctx,
            embed=type_embed(
                type="info",
                description=f"В очереди ничего нет\n\nВключите **поток** для генерации треков",
                image=f"https://mir-s3-cdn-cf.behance.net/project_modules/disp/a11a4893658133.5e98adbead405.gif",
            ),
        )

    # -------------------------------------------------------------------------------------------------------------------------------------
    # VOICE_STATE_UPDATE ИВЕНТ NOTE: перенесен в fetcher.py

    # @commands.Cog.listener()
    # async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
    #     if not hasattr(self, 'node'): # если нода еще не инициализировалась
    #         return

    #     player: NoirPlayer = self.bot.node.get_player(member.guild.id)

    #     if not player:
    #         return

    # if not member.guild.voice_client or ((len(player.channel.members) < 2)
    # and not player.is_radio) or (member == self.bot.user and not
    # after.channel):

    #         try:
    #             player.update_bar.stop()
    #         except:
    #             pass

    #         try:
    #             await player.bar.delete()
    #         except:
    #             pass

    #         try:
    #             await player.destroy()
    #         except:
    #             pass

    # -------------------------------------------------------------------------------------------------------------------------------------
    # КОМАНДЫ
    # Группа play

    """Подключается к войсу и добавляет в очередь трек"""

    @commands.slash_command(name="play", dm_permission=False)
    async def add(self, ctx):
        pass

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="Проигрывание трека вне очереди")
    async def now(
        self, ctx, search: str = commands.Param(description="ссылка / название")
    ):  # , replace: bool = commands.Param(description="заменить текущий трек")):
        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        query = await player.get_tracks(
            query=search, ctx=ctx, search_type=pomice.SearchType.ytmsearch
        )

        if not query:
            return await ctx.edit_original_response(
                embed=type_embed(type="error", description=f"Не удалось найти")
            )

        if isinstance(query, pomice.Playlist):
            await player.queue.put_list(query.tracks)
            await player.play(player.queue.get())
            # for track in query.tracks:
            #     await player.queue.put(track)
            #     if not index:
            #         await player.play(player.queue.jump(track))

            #         index += 1

        else:
            await player.play(query[0])

        await ctx.delete_original_message()

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="Поиск sound")
    async def search(
        self,
        ctx,
        search: str = commands.Param(description="слова из текста или название"),
    ):  # , replace: bool = commands.Param(description="заменить текущий трек")):
        await ctx.edit_original_response(
            f"Добавляю в очередь <a:load:1147820235634790411>\nПоиск со spotify может занять некоторое время."
        )

        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        query = await player.get_tracks(
            query=search, ctx=ctx, search_type=pomice.SearchType.ytmsearch
        )

        if not query:
            return await ctx.edit_original_response(
                embed=type_embed(type="error", description=f"Не удалось найти")
            )

        if isinstance(query, pomice.Playlist):
            await player.queue.put_list(query.tracks)
            if not player.current:
                await player.play(player.queue.get())
            # for track in query.tracks:
            #     await player.queue.put(track)
            #     if not player.current:
            #         await player.play(player.queue.get())
        else:
            await player.queue.put(query[0])

        if not player.current:
            await player.play(player.queue.get())

        await ctx.delete_original_message()

    @search.autocomplete("search")
    async def autosearch(self, inter, user_input):
        if not user_input:
            return

        try:
            search = await self.bot.node.get_tracks(
                query=user_input, ctx=inter, search_type=pomice.SearchType.ytmsearch
            )
        except BaseException:
            return

        list = []

        if search:
            if isinstance(search, pomice.Playlist):
                list.append(
                    disnake.OptionChoice(
                        name=f"PLAYLIST | {search.name}", value=search.uri
                    )
                )
            else:
                for track in search:
                    if len(f"{track.author} - {track.title}") <= 100:
                        list.append(
                            disnake.OptionChoice(
                                name=f"{track.author} - {track.title}",
                                value=track.uri))

        return list

    """Поиск радиостанции по json"""

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="Радиостанции радио ЗайцевFM")
    async def zaycevfm(
        self, ctx, station: str = commands.Param(description="радиостанция")
    ):
        await ctx.edit_original_response(
            f"Добавляю в очередь <a:load:1147820235634790411>"
        )

        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        query = await player.get_tracks(query=station, ctx=ctx)

        await player.queue.put(query[0])

        if not player.current:
            await player.play(player.queue.get())

        await ctx.delete_original_message()

    @zaycevfm.autocomplete("station")
    async def autostation(self, inter, user_input):
        list = []

        for station in RadioNames:
            if user_input in station or not user_input:
                list.append(
                    disnake.OptionChoice(
                        name=station, value=RadioUrls[RadioNames.index(station)]
                    )
                )

        return list

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="Добавить несколько сразу")
    async def multiple(self, ctx):
        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        await ctx.response.send_modal(AddMultiple(player))

    @check_player_decorator(with_connection=True)
    @add.sub_command(description="Добавить плейлист в очередь")
    async def playlist(
        self, ctx, playlist: str = commands.Param(description="имя плейлиста")
    ):
        await ctx.edit_original_response(
            f"Добавляю в очередь <a:load:1147820235634790411>"
        )

        player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

        playlist = self.bot.db.playlists.get_playlist(playlist)

        if not playlist:
            return await ctx.edit_original_message(
                embed=type_embed(type="error", description="Неизвестный плейлист")
            )

        if playlist.get("tracks"):
            items = []
            
            for track in playlist.get("tracks"):
                try:
                    query = (await player.get_tracks(query=track.get("url"), ctx=ctx))[0]

                    if (
                        not player.current
                    ):  # чтобы не создавать задержку, играть первый найденный
                        player.queue.put(query)
                        await player.play(player.queue.get())

                    else:
                        items.append(query)
                        
                except:
                    continue

            await player.queue.put_list(items)
               

        else:
            return await ctx.edit_original_message(
                embed=type_embed(type="error", description="Пустой плейлист")
            )

        await ctx.delete_original_message()

    @playlist.autocomplete("playlist")
    async def autoplaylist(self, inter, user_input):
        results, list = self.bot.db.playlists.get_user_playlists(
            inter.author.id), []

        for playlist in results:
            list.append(
                disnake.OptionChoice(
                    name=playlist.get("title"), value=playlist.get("uuid")
                )
            )

        return list

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Избранные

    @commands.slash_command(
        description="Посмотреть свои звездочки", dm_permission=False
    )
    async def stars(self, ctx):
        await ctx.response.defer(ephemeral=True)
        stars = self.bot.db.stars.get_stars(ctx.author.id)

        if stars and stars.get("tracks"):
            try:
                view = StarsView(
                    songs=stars.get("tracks"),
                    player=self.bot.node.get_player(ctx.guild.id),
                )
                return await view.refresh_pages(ctx)
            except BaseException:
                return await ctx.edit_original_message(
                    embed=genembed(
                        title="", description="Похоже, у вас нет избранных треков"
                    )
                )

        else:
            return await ctx.edit_original_message(
                embed=genembed(title="У вас нет избранных треков", description="")
            )

    @check_player_decorator(with_connection=True)
    @add.sub_command(name="stars", description="Добавить звездочки в очередь")
    async def play_stars(self, ctx):
        stars = self.bot.db.stars.get_stars(ctx.author.id)

        if stars and stars.get("tracks"):
            player: NoirPlayer = self.bot.node.get_player(ctx.guild_id)

            for track in stars.get("tracks"):
                try:
                    query = (await player.get_tracks(query=track.get("url"), ctx=ctx))[
                        0
                    ]

                    query.thumbnail = track.get("thumbnail")

                    await player.queue.put(query)

                    if (
                        not player.current
                    ):  # чтобы не создавать задержку, играть первый найденный
                        await player.play(player.queue.get())
                except BaseException:
                    continue

            await ctx.delete_original_message()

        else:
            await ctx.edit_original_message(
                embed=genembed(title="У вас нет избранных треков", description="")
            )

    @check_player_decorator()
    @commands.slash_command(
        description="Поставить треку звездочку", dm_permission=False
    )
    async def star(self, ctx):
        player = self.bot.node.get_player(ctx.guild_id)

        if not player.current:
            raise NoCurrent("нет текущего трека")

        if not player.current.is_stream:
            track = player.current
            self.bot.db.stars.add_to_stars(
                ctx.author.id,
                self.bot.build.track(
                    track.info, track.track_type.value, track.thumbnail
                ),
            )

            await ctx.send(
                embed=genembed(
                    title="",
                    description="## Звездочка поставлена.\n\nПосмотрите ее в своем [профиле](https://noirplayer.su/me/stars).",
                ),
                ephemeral=True,
            )
        else:
            return await ctx.delete_original_message()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Подключение онли (для веба)

    @check_player_decorator(with_connection=True)
    @commands.slash_command(description="Подключиться", dm_permission=False)
    async def join(self, ctx):
        self.bot.node.get_player(ctx.guild_id)

        await ctx.delete_original_message()

    # -------------------------------------------------------------------------------------------------------------------------------------
    # Если плеер стакнулся

    @check_player_decorator(with_connection=True)
    @commands.slash_command(
        description="Удалить плеер при неисправности", dm_permission=False
    )
    async def fix(self, ctx):
        player = self.bot.node.get_player(ctx.guild.id)

        if player:
            try:
                await player.destroy()
            except BaseException:
                self.bot.node._players.pop(ctx.guild.id)
                if self.bot.node.is_connected:
                    await self._node.send(
                        method="DELETE",
                        path=player._player_endpoint_uri,
                        guild_id=ctx.guild.id,
                    )

        await ctx.delete_original_message()


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))
