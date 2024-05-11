import datetime

from disnake import Embed

from services.persiktunes import LoopMode, Player

loop = {LoopMode.QUEUE: "очередь", LoopMode.TRACK: "трек"}


def progress_slider(start, end):
    bar, indicator = "", False

    for i in range(24):
        try:
            if start / end * 24 >= i + 1:
                if not indicator:
                    bar += "▬"
            else:
                if not indicator:
                    bar += "⚪"
                    indicator = True
                else:
                    bar += "▬"
        except BaseException:
            bar += "▬"

    return bar


async def state(player: Player):
    # if player.current.info.isStream:
    #     embed = genembed(
    #         title=f"{player.current.author}",
    #         author_name=None,
    #         footer=f"громкость: {player.volume}%",
    #         description=f"{player.current.title}",
    #     )

    #     embed.set_image("https://noirplayer.su/cdn/noir%20banner%20primary.png")

    #     return embed

    times = ""

    if not player.current.info.isStream:

        total = (player.adjusted_length / 1000) % (24 * 3600)
        curr = (player.adjusted_position / 1000) % (24 * 3600)

        total = datetime.time(
            second=int(total % 60),
            minute=int((total % 3600) // 60),
            hour=int(total // 3600),
        ).strftime("%H:%M:%S" if total // 3600 else "%M:%S")
        curr = datetime.time(
            second=int(curr % 60),
            minute=int((curr % 3600) // 60),
            hour=int(curr // 3600),
        ).strftime("%H:%M:%S" if curr // 3600 else "%M:%S")

        times = f"{curr} / {total}"

    image = (
        player.current.info.artworkUrl
        if player.current.info.artworkUrl
        else f"https://mir-s3-cdn-cf.behance.net/project_modules/disp/a11a4893658133.5e98adbead405.gif"
    )

    prog = (
        progress_slider(player.adjusted_position, player.adjusted_length)
        if not player.current.info.isStream
        else ""
    )

    embed = Embed(
        title=player.current.info.title,
        color=player.color,
        description=f"*{player.current.info.author}*",
        type="image",
    )

    embed.set_image(image) if image else None

    embed.set_footer(
        text=f"{prog}\n{times}\nгромкость: {player.volume}% {f' • повтор: {loop[player.queue.loop_mode]}' if player.queue.loop_mode else ''}"
    )

    if player.current.playlist:
        embed.set_author(
            name=player.current.playlist.info.name,
            icon_url=player.current.playlist.pluginInfo.get(
                "artworkUrl", player.current.playlist.tracks[0].info.artworkUrl
            ),
        )

    return embed
