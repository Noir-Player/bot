import disnake
import datetime

from typing import Literal, Optional


templates = {
    "error": {
        "title": "**Ошибка**",
        "colour": disnake.Colour.red(),
    },
    "warn": {
        "title": "**Предупреждение**",
        "colour": disnake.Colour.yellow(),
    },
    "success": {
        "title": "**Успешно**",
        "colour": disnake.Colour.blurple(),
    },
    "info": {
        "title": "**Noir Player**",
        "colour": disnake.Colour.blurple(),
    },
    "load": {
        "title": "**Секундочку...**",
        "colour": disnake.Colour.purple(),
    },
}

"""Func for generate embeds"""


def genembed(
    title: str,
    description: str,
    color=disnake.Colour.blurple(),
    thumbnail: str = None,
    image=None,
    author_url=None,
    author_name=None,
    author_icon=None,
    footer="powered by noirplayer.su",
) -> disnake.Embed:
    embed = disnake.Embed(
        title=title,
        description=description,
        colour=color,
        timestamp=datetime.datetime.now(),
    )

    if author_name:
        embed.set_author(
            name=author_name,
            icon_url=author_icon,
            url=author_url)

    if thumbnail:
        embed.set_thumbnail(thumbnail)

    if image:
        if isinstance(image, disnake.File):
            embed.set_image(file=image)
        else:
            embed.set_image(image)

    if footer:
        embed.set_footer(text=footer)

    return embed


def type_embed(
    type: Optional[Literal["error", "warn", "success", "info", "load"]],
    description: str,
    image=None,
) -> disnake.Embed:
    embed = disnake.Embed(
        title=templates[type]["title"],
        description=description,
        colour=templates[type]["colour"],
        timestamp=datetime.datetime.now(),
        type="video",
    )

    if not image:
        image = "https://noirplayer.su/static/image/noir%20banner.png"

    if isinstance(image, disnake.File):
        embed.set_image(file=image)
    else:
        # if type != "error":
        #     embed.set_image(image)
        # else:
        embed.set_image(image)

    return embed


def help() -> disnake.Embed:
    embed = disnake.Embed(
        title="Noir Player",
        description="Добро пожаловать в **Noir Player.**",
        color=disnake.Colour.blurple(),
        type="image",
        timestamp=datetime.datetime.now(),
    )

    embed.set_thumbnail(
        "https://cdn.discordapp.com/avatars/1097854004920320080/3eb23895aa8f2751596118120b3054e4.png?size=1024"
    )

    embed.set_image("https://noirplayer.su/static/image/noir%20banner.png")

    return embed


def setup() -> disnake.Embed:
    return genembed(
        title="Давайте все тут настроим для вас!",
        description="**{}**\n```yaml\n# Main\n24/7    - {}\nchannel - {}\ncolor   - {}\nrole    - @{}\n\n# Subscribe\nlevel  - {}\nperiod - from {} to {}\n\n```".format(),
        image="https://i.pinimg.com/564x/b2/cd/65/b2cd65bd6855bfb7eb98deecc4519e33.jpg",
    )
