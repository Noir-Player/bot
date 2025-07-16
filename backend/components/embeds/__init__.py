from datetime import datetime

from disnake import Embed

from ..colors import *


class BaseEmbed(Embed):
    """Base embed class for all embeds in the bot"""

    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
        colour: str | None = None,
    ):

        type = "rich"
        timestamp = datetime.timestamp(datetime.now())
        colour_int = int(colour.replace("#", ""), base=16) if colour else None

        super().__init__(
            title=title,
            type=type,
            description=description,
            url=url,
            timestamp=timestamp,  # type: ignore
            colour=colour_int,
        )


class SuccessEmbed(BaseEmbed):
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
    ):
        super().__init__(
            ((" | " + title) if title else None) if title else None,
            description,
            url,
            colour=SUCCESS,
        )


class ErrorEmbed(BaseEmbed):
    def __init__(
        self, title: str, description: str | None = None, url: str | None = None
    ):
        super().__init__(
            (" | " + title) if title else None, description, url, colour=DANGER
        )


class WarningEmbed(BaseEmbed):
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
    ):
        super().__init__(
            (" | " + title) if title else None, description, url, colour=WARNING
        )


class PrimaryEmbed(BaseEmbed):
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
    ):
        super().__init__(
            (" | " + title) if title else None, description, url, colour=PRIMARY
        )


class SecondaryEmbed(BaseEmbed):
    def __init__(
        self,
        title: str | None = None,
        description: str | None = None,
        url: str | None = None,
    ):
        super().__init__(
            (" | " + title) if title else None, description, url, colour=SECONDARY
        )
