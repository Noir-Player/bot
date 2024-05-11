import datetime
from typing import Dict, Literal, Union

import disnake
from disnake import Colour


class EmbedBuilder:

    def __init__(
        self,
        *,
        primary: Union[Colour, int, str] = "#FF4ECD",
        primary_light: Union[Colour, int, str] = "#FF95E1",
        secondary: Union[Colour, int, str] = "#7828C8",
        secondary_light: Union[Colour, int, str] = "#AE7EDE",
        accent: Union[Colour, int, str] = "#17C964",
        accent_light: Union[Colour, int, str] = "#74DFA2",
        warning: Union[Colour, int, str] = "#F5A524",
        warning_light: Union[Colour, int, str] = "#F9C97C",
        info: Union[Colour, int, str] = "#006FEE",
        info_light: Union[Colour, int, str] = "#66AAF9",
        use_timestamp: bool = True,
        footer_name: str = "Noir Player",
        footer_icon: str = "",
    ) -> None:
        """"""

        self.primary = primary
        self.primary_light = primary_light
        self.secondary = secondary
        self.secondary_light = secondary_light
        self.accent = accent
        self.accent_light = accent_light
        self.warning = warning
        self.warning_light = warning_light
        self.info = info
        self.info_light = info_light
        self.use_timestamp = use_timestamp

        self.footer_name = footer_name
        self.footer_icon = footer_icon

    def get(
        self,
        *fields: Dict[str, Union[str, int, bool]],
        title: str = None,
        description: str = None,
        url: str = None,
        thumbnail: str = None,
        image: str = None,
        footer: str = None,
        footer_icon: str = None,
        author_name: str = None,
        author_icon: str = None,
        author_url: str = None,
        color: Literal["primary", "secondary", "accent", "warning", "info"] = "primary",
        use_light_color: bool = False,
    ) -> disnake.Embed:

        colour = self.__getattribute__(color + ("_light" if use_light_color else ""))

        if type(colour) == str:
            colour = int(colour.replace("#", ""), 16)

            if " | " in title and not title.startswith("`"):  # griding emojies
                title = f"`{title}`"

        embed = disnake.Embed(
            title=title,
            type="article",
            description=description,
            url=url,
            colour=colour,
            timestamp=datetime.datetime.now() if self.use_timestamp else None,
        )

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        if author_name:
            embed.set_author(name=author_name, url=author_url, icon_url=author_icon)

        if image:
            embed.set_image(url=image)

        if footer or self.footer_name:
            embed.set_footer(
                text=footer or self.footer_name,
                icon_url=footer_icon or self.footer_icon,
            )

        for field in fields:
            embed.add_field(**field)

        return embed
