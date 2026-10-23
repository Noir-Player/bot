from typing import Annotated
from uuid import uuid4

from beanie import Document, Indexed
from pydantic import Field
from services.persiktunes.models import Playlist


class PlaylistDocument(Playlist, Document):
    """Model for Playlist document in Beanie"""

    user_id: int = Field(description="ID of the user who owns the playlist")

    public: bool = Field(default=False, description="Is the playlist public?")

    uuid: Annotated[str, Indexed(unique=True)] = Field(
        default_factory=lambda: uuid4().__str__(), description="UUID of the playlist"
    )

    class Settings:
        name = "playlists"
        keep_nulls = False
