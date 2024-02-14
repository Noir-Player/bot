from pydantic import BaseModel, Field
from typing import Union, List, Optional, Dict

base_id = Field(le=10000000000000000000000)
base_name = Field(max_length=40)
base_url = Field(max_length=200)

# LOW LEVEL MODELS


class _Metric(BaseModel):
    rating: float
    views: int


class _Author(BaseModel):
    name: str = Field(max_length=40)
    id: int = base_id


class _Integer(BaseModel):
    source: str = Field()


class _Webhook(BaseModel):
    id: int = base_id
    name: Optional[str] = Field('', max_length=40)
    icon: Optional[str] = Field('', max_length=200)


class _Ban(BaseModel):
    reason: str
    timestamp: int

# BASE MODELS


class Track(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(max_length=100)
    thumbnail: Optional[str] = Field('', max_length=200)

    url: str = Field(max_length=200)

    id: str = Field(max_length=100)
    length: Union[int, float] = Field(default=0, le=10000000000)

    playlist: Optional[str] = Field('', max_length=50)

    type: str = Field(max_length=50)


class Playlist(BaseModel):
    title: str = Field(min_length=2, max_length=40)
    thumbnail: Optional[str] = Field('', max_length=200)
    description: Optional[str] = Field('', max_length=1000)

    public: bool = False

    tracks: Optional[List[Track]] = []

    metric: Optional[_Metric] = {}

    author: _Author

    forked: Optional[Union[List[int], int]] = []

    integer: Optional[_Integer] = {}

    uuid: Optional[str] = Field('', min_length=20, max_length=40)


class Mix(BaseModel):
    title: Optional[str] = Field('Ваш микс', min_length=2, max_length=40)
    thumbnail: Optional[str] = Field('', max_length=200)
    description: Optional[str] = Field('', max_length=1000)

    related_to: Track

    tracks: List[Track]


class Setup(BaseModel):
    radio: Optional[bool] = False
    role: Optional[int] = Field(None, le=10000000000000000000000)
    color: Optional[str] = Field(None, min_length=4, max_length=7)
    channel: Optional[int] = Field(None, le=10000000000000000000000)
    volume_step: Optional[int] = Field(25, ge=1, le=400)
    disable_eq: Optional[bool] = False
    webhook: Optional[_Webhook] = {}

    id: int = base_id


class User(BaseModel):
    name: str = Field(max_length=40)
    description: Optional[str] = Field('', max_length=1000)
    role: Optional[str] = Field('', max_length=40)
    permissions: Optional[int] = Field(0, ge=0, le=9)
    playlist_limit: Optional[int] = Field(5, ge=0)
    theme: Optional[str] = Field('night', min_length=2, max_length=10)
    ban: Optional[_Ban] = {}

    id: int = base_id


class Metric(BaseModel):
    last_track: Optional[List[Track]] = []
    last_playlists: Optional[List[str]] = []
    liked_genres: Optional[List[str]] = []
    spotify_params: Optional[Dict[str, float]] = []
    liked_artists: Optional[Dict[str, str]] = []

    id: int = base_id

# REQUEST MODELS


class AddTrackRequest(BaseModel):
    query: str = Field(max_length=100)


class MoveTrackRequest(BaseModel):
    url: str = Field(max_length=100)
    pos: int = Field(ge=0, le=1000)


class MergePlaylistsRequest(BaseModel):
    uuid1: str = Field(min_length=20, max_length=40)
    uuid2: str = Field(min_length=20, max_length=40)


class AddToLibraryRequest(BaseModel):
    uuid: str = Field(min_length=20, max_length=40)


class RemoveTrackRequest(BaseModel):
    url: str = Field(max_length=100)


class CreateWebhookRequest(BaseModel):
    name: str = base_name
    channel: int = base_id
