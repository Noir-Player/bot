from pydantic import *
from pydantic.fields import Field
from typing import List, Dict, Optional
from classes.WebModels import Playlist, Track


class DiscoveryResponse(BaseModel):
    listen_again: Optional[List[Track]] = Field(None, description="Прослушайте еще раз")

    recommended_tracks: Optional[List[Track]] = Field(None, description="Рекомендованные треки на основе прослушанного (только spotify / youtube)")
    recommended_playlists: Optional[List[Playlist]] = Field(None, description="Рекомендованные плейлисты (spotify / youtube)")

    popular_playlists: List[Playlist] = Field(description="Популярные плейлисты комьюнити")
    random_track: Track = Field(description="Случайный трек. Возможно, вам понравится")

    related_to: Optional[Dict[Track, List[Track]]] = Field(None, description="Похоже на этот трек")