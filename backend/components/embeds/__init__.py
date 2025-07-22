from datetime import datetime

from assets.colors import *
from disnake import Embed


class BaseEmbed(Embed):
    """Base embed class for all embeds in the bot"""

    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
        colour: str | int | None = None,
    ):

        type = "rich"
        timestamp = datetime.now()

        if isinstance(colour, str):
            colour = int(colour.replace("#", ""), base=16) if colour else None

        super().__init__(
            title=title,
            type=type,
            description=description,
            url=url,
            timestamp=timestamp,
            colour=colour,
        )


class SuccessEmbed(BaseEmbed):
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
    ):
        super().__init__(
            (("✅  " + title) if title else None) if title else None,
            description,
            url,
            colour=SUCCESS,
        )


class ErrorEmbed(BaseEmbed):
    def __init__(
        self, title: str, description: str | None = None, url: str | None = None
    ):
        super().__init__(
            ("❌  " + title) if title else None, description, url, colour=DANGER
        )


class WarningEmbed(BaseEmbed):
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
    ):
        super().__init__(
            ("⚠️  " + title) if title else None, description, url, colour=WARNING
        )


class PrimaryEmbed(BaseEmbed):
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
    ):
        super().__init__(
            ("👾  " + title) if title else None, description, url, colour=PRIMARY
        )


class SecondaryEmbed(BaseEmbed):
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
    ):
        super().__init__(
            ("✨  " + title) if title else None, description, url, colour=SECONDARY
        )
