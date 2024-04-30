import json
import time

import disnake
import pomice
import requests
from disnake import SelectOption
from disnake.ext import commands
from disnake.ext.commands import Paginator

from helpers.dump import Dump as Build
from helpers.embeds import *
from objects.exceptions import *
from validators.player import check_player_btn_decorator

build = Build()

errors = json.load(open("data/resources/errors.json", "r", encoding="utf-8"))

filters = {
    "ChannelMix": pomice.ChannelMix(tag="mix"),
    "Distortion": pomice.Distortion(tag="dist"),
    "Karaoke": pomice.Karaoke(tag="kar"),
    "LowPass": pomice.LowPass(tag="low"),
    "Rotation": pomice.Rotation(tag="rot", rotation_hertz=1),
    "Tremolo": pomice.Tremolo(tag="trem"),
    "Vibrato": pomice.Vibrato(tag="vibr"),
    "Boost": pomice.Equalizer.boost(),
    "Metal": pomice.Equalizer.metal(),
    "Piano": pomice.Equalizer.piano(),
    "VaporWave": pomice.Timescale.vaporwave(),
    "Nightcore": pomice.Timescale.nightcore(),
}

descriptions = [
    "панорамирование звука",
    "искажение",
    "убрать голос",
    "подавление высоких частот",
    "вращение",
    "колебания громкости",
    "колебания высоты",
    "усиление бассов",
    "усиление средних частот",
    "усиление средних и высоких частот",
    "эффект кассеты",
    "повышение скорости",
]

options = []

for i in range(len(filters)):
    options.append(
        SelectOption(
            label=list(filters.keys())[i],
            description=descriptions[i],
            emoji="<:flag:1115610864054190121>",
        )
    )


async def check_voice(player, inter: disnake.Interaction, with_message=False):
    await inter.response.defer(ephemeral=True, with_message=with_message)

    if not inter.author.voice:
        raise NoInVoice("не в войсе")

    if not player or inter.author.voice.channel != inter.guild.voice_client.channel:
        raise NoInVoiceWithMe("бот не в войсе")

    if (
        player.dj_role
        and player.dj_role not in [role.id for role in inter.author.roles]
        and not inter.permissions.administrator
    ):
        raise commands.MissingPermissions(["setup or manage player"])


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class ActionsView(disnake.ui.View):
    """View меню активностей"""

    def __init__(self, player, *, timeout: float | None = None) -> None:
        super().__init__(timeout=timeout)

        self.player: pomice.Player = player

    # async def on_error(self, error: Exception, item, interaction):
    #     if error is commands.CommandError or error is commands.CommandInvokeError:
    #         e = errors.get(error.__cause__.__class__.__name__, 'Неизвестная ошибка. Простите...')
    #     else:
    #         e = errors.get(error.__class__.__name__, 'Неизвестная ошибка. Простите...')

    #     await interaction.send(
    #         embed=type_embed("error", f"```diff\n- {e}```"),
    #         ephemeral=True,
    #         components=[disnake.ui.Button(style=disnake.ButtonStyle.url, label="report", url="https://discord.gg/ua4kpgzpWJ")]
    #         )

    #     logging.error(f'error in view:')
    #     logging.error(traceback.format_exc())

    @disnake.ui.button(
        emoji="<:flag:1115610864054190121>",
        label="поставить звездочку",
        row=0,
        style=disnake.ButtonStyle.blurple,
    )
    @check_player_btn_decorator()
    async def recomendations(self, button, interaction):
        if not self.player.current:
            raise NoCurrent("нет текущего трека")

        if not self.player.current.is_stream:
            track = self.player.current
            interaction.bot.db.stars.add_to_stars(
                interaction.author.id,
                build.track(track.info, track.track_type.value, track.thumbnail),
            )

            await interaction.send(
                embed=genembed(
                    title="",
                    description="Звездочка поставлена.\n\nПосмотрите ее в своем [профиле](https://noirplayer.su/me/stars).",
                ),
                ephemeral=True,
            )
        else:
            return

    @disnake.ui.button(
        emoji="<:alt:1110216568295653459>",
        label="найти альтернативы",
        row=1,
        style=disnake.ButtonStyle.blurple,
    )
    @check_player_btn_decorator(with_message=True)
    async def alternative(self, button, interaction):
        if self.player.current and self.player.current.track_type in [
            pomice.TrackType.YOUTUBE,
            pomice.TrackType.SPOTIFY,
        ]:
            tracks = await self.player.get_recommendations(
                track=self.player.current, ctx=self.player.current.ctx
            )

            view = TracksView(songs=tracks, player=self.player)
            return await view.refresh_pages(interaction)

        await interaction.delete_original_message()

    # @disnake.ui.button(emoji="<:chatlefttext:1110271673975984291>", label="найти текст⠀⠀⠀⠀⠀⠀", row=2, style=disnake.ButtonStyle.blurple)
    # async def lyric(self, button, interaction):
    #     await check_voice(self.player, interaction)

    #     if self.player.current:
    #         try:
    #             lyric = self.client.get_lyrics(self.client.get_watch_playlist(self.player.current.identifier).get('lyrics', {})).get('lyrics', "Нет текста для этой песни ¯\_(ツ)_/¯")
    #         except:
    # return await interaction.send(embed=genembed(title=f"Нет текста песни |
    # {self.player.current.title}", description=""), ephemeral=True)

    #         async with interaction.channel.typing():
    #             pag = Paginator(prefix="```yaml\n")

    #             for line in lyric.split("\n"):
    #                pag.add_line(line)

    #             for page in pag.pages:
    # await interaction.send(embed=genembed(title=f"Текст песни |
    # {self.player.current.title}", description=page), ephemeral=True)

    @disnake.ui.button(
        emoji="<:trash3:1117078782096982037>",
        label="удалить из очереди",
        row=3,
        style=disnake.ButtonStyle.blurple,
    )
    @check_player_btn_decorator()
    async def remove(self, button, interaction):
        if self.player.current:
            try:
                await self.player.queue.remove(self.player.current)
                await self.player.play(self.player.queue.next())
            except BaseException:
                pass

    @disnake.ui.button(
        emoji="<:sliders2vertical:1107250314991652904>",
        label="эквалайзер⠀⠀⠀⠀⠀⠀",
        row=4,
        style=disnake.ButtonStyle.blurple,
    )
    @check_player_btn_decorator()
    async def eq(self, button, inter):
        await inter.send(ephemeral=True, view=FiltersView(self.player))


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class FiltersView(disnake.ui.View):
    """View фильтры"""

    def __init__(self, player, *, timeout: float | None = 600) -> None:
        super().__init__(timeout=timeout)
        self.player = player

        if self.player.disable_eq:  # Если эквалайзер выключен
            self.eq._underlying.disabled = True

    @disnake.ui.select(placeholder="фильтры", options=options, row=0, max_values=7)
    async def eq(self, select: disnake.ui.StringSelect, inter):
        await self.player.reset_filters(fast_apply=True)

        await inter.response.defer()

        for filter in inter.data.values:
            try:
                await self.player.add_filter(filters[filter], fast_apply=True)
            except BaseException:
                pass

    @disnake.ui.button(
        emoji="<:trash3:1117078782096982037>",
        label="сбросить все фильтры",
        row=2,
        style=disnake.ButtonStyle.blurple,
    )
    async def reset_filters(self, button, inter):
        await self.player.reset_filters()

        await inter.response.defer()

    # async def on_error(self, error: Exception, item, interaction):
    #     pass


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class QueueView(disnake.ui.View):
    """View очередь"""

    def __init__(self, player, *, timeout: float | None = 180) -> None:
        self.player: pomice.Player = player
        self.index = 0
        self.pag = Paginator(prefix="```yaml\n")

        super().__init__(timeout=timeout)

    # async def on_error(self, error: Exception, item, interaction):
    #     pass

    async def refresh_pages(self, interaction):
        self.pag.clear()

        if self.player.queue.is_empty:
            return await interaction.edit_original_message(
                embed=genembed(
                    title=(
                        f'Очередь пуста | Сейчас играет "{self.player.current.title}"'
                        if self.player.current
                        else "Очередь пуста | Ничего не играет"
                    ),
                    description="",
                )
            )

        i = n = 0
        for val in self.player.queue.get_queue():
            if n >= 30:
                self.pag.close_page()
                n = 0

            if i == self.player.queue.find_position(self.player.current):
                ind = ">"
            else:
                ind = ""

            self.pag.add_line(
                f"{i + 1} -{ind} "
                + val.title
                + f" [{val.requester.display_name if val.requester else 'неизвестно'}]"
            )

            i += 1
            n += 1

        total = (
            (
                (
                    sum(
                        i.length
                        for i in self.player.queue.get_queue()[
                            self.player.queue.find_position(self.player.current) :
                        ]
                    )
                    - self.player.position
                )
                / 1000
            )
            if not self.player.queue.is_empty
            else 0
        )

        total = int(time.time() + total)

        await interaction.edit_original_message(
            embed=genembed(
                title=(
                    f'Очередь | Сейчас играет "{self.player.current.title}"'
                    if self.player.current
                    else "Очередь | Ничего не играет"
                ),
                description=self.pag.pages[self.index],
                footer=f"page {self.index + 1}/{len(self.pag.pages)}",
            )
            .add_field(name="Всего треков", value=f"`{self.player.queue.count}`")
            .add_field(name="Закончится", value=f"<t:{total}:R>")
            .add_field(
                name="Поток",
                value=f"`{'Да' if self.player.queue.is_nonstop else 'Нет'}`",
            ),
            view=self,
        )

    @disnake.ui.button(
        emoji="<:prev:1110211620052942911>", row=0, style=disnake.ButtonStyle.blurple
    )
    async def prev(self, button, interaction):
        await interaction.response.defer()
        if self.index > 0:
            self.index -= 1
            return await self.refresh_pages(interaction)

    @disnake.ui.button(
        emoji="<:skipforward:1107250322801442877>",
        row=0,
        style=disnake.ButtonStyle.blurple,
    )
    async def next(self, button, interaction):
        await interaction.response.defer()
        if (self.index + 1) < len(self.pag.pages):
            self.index += 1
            return await self.refresh_pages(interaction)

    @disnake.ui.button(
        emoji="<:shuffle:1107250313221640223>", row=0, style=disnake.ButtonStyle.blurple
    )
    async def shuffle(self, button, interaction):
        await interaction.response.defer()
        await self.player.queue.shuffle()
        await self.refresh_pages(interaction)

    @disnake.ui.button(
        emoji="<:disc:1116756102596530339>",
        label="поток",
        row=0,
        style=disnake.ButtonStyle.blurple,
    )
    async def recomendations(self, button, interaction):
        await interaction.response.defer()
        if not self.player.current:
            return

        self.player.queue.set_nonstop(not self.player.queue.is_nonstop)

        return await self.refresh_pages(interaction)

    @disnake.ui.button(
        emoji="<:musicnotelist:1107250545523183616>",
        label="сохранить как плейлист",
        row=1,
        style=disnake.ButtonStyle.blurple,
    )
    async def shuffle(self, button, interaction):
        tracks = [
            build.track(track.info, track.track_type.value, track.thumbnail)
            for track in self.player.queue.get_queue()
        ]

        from components.ui.modals import PlaylistInfoModal

        await interaction.response.send_modal(
            PlaylistInfoModal(
                node=self.player.node, title="Сохранить очередь", tracks=tracks
            )
        )


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class TracksView(disnake.ui.View):
    """View альтернативные треки"""

    def __init__(
        self, songs, player, *, title="Похожие", timeout: float | None = 180
    ) -> None:
        self.player = player
        self.songs = songs
        self.title = title

        self.index = 0

        super().__init__(timeout=timeout)

    # async def on_error(self, error: Exception, item, interaction):
    #     pass

    async def refresh_pages(self, interaction):
        embed = genembed(
            author_name=self.title,
            title=self.songs[self.index].title,
            description=self.songs[self.index].author,
            image=self.songs[self.index].thumbnail,
            footer=f"страница {self.index + 1}/{len(self.songs)}",
        )

        await interaction.edit_original_message(embed=embed, view=self)

    @disnake.ui.button(
        emoji="<:prev:1110211620052942911>", row=0, style=disnake.ButtonStyle.blurple
    )
    async def prev(self, button, interaction):
        await interaction.response.defer()
        if self.index > 0:
            self.index -= 1
            return await self.refresh_pages(interaction)

        await interaction.response.defer(ephemeral=True)

    @disnake.ui.button(
        emoji="<:skipforward:1107250322801442877>",
        row=0,
        style=disnake.ButtonStyle.blurple,
    )
    async def next(self, button, interaction):
        await interaction.response.defer()
        if (self.index + 1) < len(self.songs):
            self.index += 1
            return await self.refresh_pages(interaction)

        await interaction.response.defer(ephemeral=True)

    @disnake.ui.button(
        label="Добавить в очередь", row=0, style=disnake.ButtonStyle.blurple
    )
    async def add_to_queue(self, button, interaction):
        if self.player:
            track = (
                await self.player.get_tracks(
                    query=self.songs[self.index].get("url"),
                    ctx=interaction,
                    search_type=pomice.SearchType.ytmsearch,
                )
            )[0]
            await self.player.queue.put(track)
            if not self.player.current:
                await self.player.play(self.player.queue.get())

        await interaction.response.defer(ephemeral=True)


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class StarsView(disnake.ui.View):
    """View  звездочки"""

    def __init__(
        self, songs, player, *, title="Избранное", timeout: float | None = 600
    ) -> None:
        self.player = player
        self.songs = songs
        self.title = title

        self.index = 0

        super().__init__(timeout=timeout)

    # async def on_error(self, error: Exception, item, interaction):
    #     pass

    async def refresh_pages(self, interaction):
        embed = (
            genembed(
                author_name=self.title,
                title=self.songs[self.index].get("title", "Неизвестное название"),
                description=self.songs[self.index].get("author", "Неизвестный автор"),
                image=self.songs[self.index].get("thumbnail"),
                footer=f"song {self.index + 1}/{len(self.songs)}",
            )
            if len(self.songs)
            else genembed(title="", description="У вас нет избранных треков.")
        )

        await interaction.edit_original_message(embed=embed, view=self)

    @disnake.ui.button(
        emoji="<:prev:1110211620052942911>", row=0, style=disnake.ButtonStyle.blurple
    )
    async def prev(self, button, interaction):
        await interaction.response.defer()
        if self.index > 0:
            self.index -= 1
            return await self.refresh_pages(interaction)

        await interaction.response.defer(ephemeral=True)

    @disnake.ui.button(
        emoji="<:skipforward:1107250322801442877>",
        row=0,
        style=disnake.ButtonStyle.blurple,
    )
    async def next(self, button, interaction):
        await interaction.response.defer()
        if (self.index + 1) < len(self.songs):
            self.index += 1
            return await self.refresh_pages(interaction)

        await interaction.response.defer(ephemeral=True)

    @disnake.ui.button(
        label="Добавить в очередь", row=0, style=disnake.ButtonStyle.blurple
    )
    async def add_to_queue(self, button, interaction):
        if self.player:
            track = (
                await self.player.get_tracks(
                    query=self.songs[self.index].get("url"), ctx=interaction
                )
            )[0]
            await self.player.queue.put(track)
            if not self.player.current:
                await self.player.play(self.player.queue.get())

        await interaction.response.defer(ephemeral=True)

    @disnake.ui.button(
        label="Снять звездочку", row=1, style=disnake.ButtonStyle.blurple
    )
    async def unstar(self, button, interaction):
        await interaction.response.defer()
        interaction.bot.db.stars.remove_from_stars(
            self.songs[self.index].get("url"), interaction.author.id
        )
        self.songs = interaction.bot.db.stars.get_stars(interaction.author.id).get(
            "tracks"
        )

        if self.index + 1 >= len(self.songs):
            self.index -= 1

        return await self.refresh_pages(interaction)


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


class PlaylistView(disnake.ui.View):
    """View  плейлиста"""

    def __init__(
        self, info: dict, node, edit=True, *, timeout: float | None = None
    ) -> None:
        self.node = node
        self.uuid = info.get("uuid")

        self.info: dict = info
        self.songs: list = info.get("tracks")

        self.index = 0

        super().__init__(timeout=timeout)

        if (
            not pomice.enums.URLRegex.BASE_URL.search(info.get("thumbnail", ""))
            or requests.head(info.get("thumbnail")).status_code != requests.codes.ok
        ):  # Если это не ссылка или ссылка невалидная
            # Заменяем обложку, если ее нет
            info["thumbnail"] = (
                "https://cataas.com/cat/says/Обложка%20не%20найдена?type=square&width=500"
            )

        if not edit:  # Если недоступно изменение плейлиста
            self.remove_item(self.add_to_playlist)
            self.remove_item(self.delete_from_playlist)

        # if not table("playlists").find_one({"uuid": self.info.get('forked')}): # Если плейлист не сихронизируемый
        #     self.remove_item(self.sync_from_playlist)

        self.add_item(
            disnake.ui.Button(
                label="ссылка на плейлист",
                url=f"https://noirplayer.su/playlists/{self.uuid}",
                row=1,
            )
        )

    # async def on_error(self, error: Exception, item, interaction):
    #     pass

    async def refresh_pages(self, interaction):
        if not self.index:
            self.songs = interaction.bot.db.playlists.get_playlist(self.uuid)
            embed = genembed(
                title=self.info.get("title"),
                description=self.info.get("description", "")
                + "\n\nСвайпните на <:skipforward:1107250322801442877>, чтобы посмотреть треки",
                image=self.info.get("thumbnail"),
                author_name=None,
                footer=f"{'публичный плейлист' if self.info.get('public') else 'приватный плейлист'} | {', '.join(self.info.get('tags', []) if self.info.get('tags') else [])}",
            )
            embed.add_field("Автор", f"`{self.info.get('author', {}).get('name')}`")
            embed.add_field(
                "Треки",
                f"{f'`{len(self.songs)}`' if self.songs else 'Добавьте с помощью <:pluscircle:1118459100150378550>'}",
            )

        else:
            embed = genembed(
                author_name=f'Плейлист | {self.info.get("title")}',
                author_icon=self.info.get(
                    "thumbnail", "https://noirplayer.su/static/image/nocover.png"
                ),
                title=self.songs[self.index - 1].get("title"),
                description=self.songs[self.index - 1].get("author"),
                image=self.songs[self.index - 1].get("thumbnail"),
                footer=f"page {self.index}/{len(self.songs)}",
            )
        try:
            await interaction.edit_original_message(embed=embed, view=self)
        except disnake.HTTPException:
            embed.set_image("https://noirplayer.su/static/image/nocover.png")
            await interaction.edit_original_message(embed=embed, view=self)

    @disnake.ui.button(
        emoji="<:prev:1110211620052942911>", row=0, style=disnake.ButtonStyle.blurple
    )
    async def prev(self, button, interaction):
        await interaction.response.defer()
        self.songs = interaction.bot.db.playlists.get_playlist(self.uuid).get("tracks")
        if self.index > 0:
            self.index -= 1
            return await self.refresh_pages(interaction)

    @disnake.ui.button(
        emoji="<:skipforward:1107250322801442877>",
        row=0,
        style=disnake.ButtonStyle.blurple,
    )
    async def next(self, button, interaction):
        await interaction.response.defer()
        self.songs = interaction.bot.db.playlists.get_playlist(self.uuid).get("tracks")
        if (self.index) < (len(self.songs) if self.songs else 0):
            self.index += 1
            return await self.refresh_pages(interaction)

    @disnake.ui.button(
        emoji="<:trash3:1117078782096982037>", row=0, style=disnake.ButtonStyle.blurple
    )
    async def delete_from_playlist(self, button, interaction):
        await interaction.response.defer()

        if self.index:
            interaction.bot.db.playlists.remove_from_playlist(
                self.uuid, interaction.author.id, self.songs[self.index - 1].get("url")
            )
            del self.songs[self.index - 1]
            if self.index >= len(self.songs):
                self.index -= 1
            return await self.refresh_pages(interaction)
        else:
            return

    @disnake.ui.button(
        emoji="<:pluscircle:1118459100150378550>",
        row=0,
        style=disnake.ButtonStyle.blurple,
    )
    async def add_to_playlist(self, button, interaction):
        from components.ui.modals import AddToPlaylist

        await interaction.response.send_modal(AddToPlaylist(self.node, self, self.uuid))
        await interaction.delete_original_message()
