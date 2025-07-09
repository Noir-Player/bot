from datetime import datetime

from disnake import Embed

from ..colors import *


class BaseEmbed(Embed):
    """Base embed class for all embeds in the bot"""

    def __init__(
        self,
        title: str = None,
        description: str = None,
        url: str = None,
        colour: str = None,
    ):

        type = "rich"
        timestamp = datetime.timestamp(datetime.now())
        colour = int(colour.replace("#", ""), base=16)

        super().__init__(
            title=title,
            type=type,
            description=description,
            url=url,
            timestamp=timestamp,
            colour=colour,
        )


class SuccessEmbed(BaseEmbed):
    def __init__(self, title: str = None, description: str = None, url: str = None):
        super().__init__(" | " + title, description, url, colour=SUCCESS)


class ErrorEmbed(BaseEmbed):
    def __init__(self, title: str, description: str = None, url: str = None):
        super().__init__(" | " + title, description, url, colour=DANGER)


class WarningEmbed(BaseEmbed):
    def __init__(self, title: str = None, description: str = None, url: str = None):
        super().__init__(" | " + title, description, url, colour=WARNING)


class PrimaryEmbed(BaseEmbed):
    def __init__(self, title: str = None, description: str = None, url: str = None):
        super().__init__(" | " + title, description, url, colour=PRIMARY)


class SecondaryEmbed(BaseEmbed):
    def __init__(self, title: str = None, description: str = None, url: str = None):
        super().__init__(" | " + title, description, url, colour=SECONDARY)
