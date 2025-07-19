from services.persiktunes.models import Playlist, LavalinkPlaylistInfo
from pydantic import Field

from typing import Annotated

from beanie import Document, Indexed


class StarInfo(LavalinkPlaylistInfo):
    name: str = "Starred music"


class StarDocument(Playlist, Document):
    """Model for Star document in Beanie"""

    info = StarInfo()

    user_id: Annotated[int, Indexed(unique=True)] = Field(
        description="ID of the user who owns the unique playlist, called star"
    )

    class Settings:
        name = "stars"
        keep_nulls = False
