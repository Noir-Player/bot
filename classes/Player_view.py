import datetime

from pomice import Player, LoopMode
from utils.embeds import genembed

from disnake import Embed


loop = {LoopMode.QUEUE: "очередь", LoopMode.TRACK: "звук"}


async def progress_slider(start, end):
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
    if player.current.is_stream:
        embed = genembed(
            title=f"{player.current.author}",
            author_name=None,
            footer=f"громкость: {player.volume}%",
            description=f"{player.current.title}",
        )

        embed.set_image("https://noirplayer.su/static/image/noir%20banner.png")

        return embed

    total = (player.adjusted_length / 1000) % (24 * 3600)
    curr = (player.adjusted_position / 1000) % (24 * 3600)

    total = datetime.time(
        second=int(total % 60),
        minute=int((total % 3600) // 60),
        hour=int(total // 3600),
    ).strftime("%H:%M:%S" if total // 3600 else "%M:%S")
    curr = datetime.time(
        second=int(
            curr %
            60),
        minute=int(
            (curr %
             3600) //
            60),
        hour=int(
            curr //
            3600)).strftime(
        "%H:%M:%S" if curr //
        3600 else "%M:%S")

    track = f"{curr} / {total}"  # f"`{curr}`/`{total}`"

    image = (
        player.current.thumbnail
        if player.current.thumbnail
        else f"https://mir-s3-cdn-cf.behance.net/project_modules/disp/a11a4893658133.5e98adbead405.gif"
    )

    # await progress(player.position, player.current.length, player.indicator,
    # max=16)
    prog = await progress_slider(player.adjusted_position, player.adjusted_length)

    embed = Embed(
        title=player.current.title,
        color=player.color,
        description=f"""
        {player.current.author}
        """,
        type="image",
    )
    embed.set_image(image)
    embed.set_footer(
        text=f"{prog}\n{track}\nгромкость: {player.volume}% {f' • повтор: {loop[player.queue.loop_mode]}' if player.queue.loop_mode else ''}"
    )

    if player.current.playlist:
        embed.set_author(
            name=player.current.playlist.name,
            icon_url=player.current.playlist.thumbnail,
        )

    return embed
