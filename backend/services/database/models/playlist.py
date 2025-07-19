from services.persiktunes.models import Playlist
from pydantic import Field

from typing import Annotated

from beanie import Document, Indexed


class PlaylistDocument(Playlist, Document):
    """Model for Playlist document in Beanie"""

    user_id: Annotated[int, Indexed(unique=True)] = Field(
        description="ID of the user who owns the playlist"
    )

    class Settings:
        name = "playlists"
        keep_nulls = False
