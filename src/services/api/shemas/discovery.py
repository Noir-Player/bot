from typing import Dict, List, Literal, Optional

from pydantic import *
from pydantic.fields import Field

from services.database.models import Mix, Playlist, Track


class DiscoveryResponse(BaseModel):
    listen_again: Optional[List[Track]] = Field(None, description="Прослушайте еще раз")

    recommended_tracks: Optional[List[Track]] = Field(
        None,
        description="Рекомендованные треки на основе прослушанного (только spotify / youtube)",
    )
    recommended_playlists: Optional[List[Playlist]] = Field(
        None, description="Рекомендованные плейлисты (spotify / youtube)"
    )

    popular_playlists: List[Playlist] = Field(
        description="Популярные плейлисты комьюнити"
    )
    random_track: Track = Field(description="Случайный трек. Возможно, вам понравится")

    related_to: Optional[Dict[Track, List[Track]]] = Field(
        None, description="Похоже на этот трек"
    )


class Meta(BaseModel):
    query: str = Field(description="Запрос")
    type: Optional[
        Literal["spsearch", "ytsearch", "ytmsearch", "scsearch", "dzsearch"]
    ] = None
    only: Optional[Literal["track", "playlist", "mixe"]] = None


class DiscoverySearchResponse(BaseModel):
    tracks: List[Track] = Field([], description="Список найденных треков")

    playlists: Optional[list] = Field([], description="Список найденных плейлистов")

    user_playlists: Optional[List[Playlist]] = Field(
        [], description="Список плейлистов, созданных пользователями"
    )

    mixes: Optional[List[Mix]] = Field(
        [], description="Список миксов, найденных по первому треку"
    )

    meta: Meta
