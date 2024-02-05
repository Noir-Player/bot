from pydantic import *
from pydantic.fields import Field
from typing import List
from classes.WebModels import Playlist

class Meta(BaseModel):
    page: int = Field(description="Текущая страница")
    count: int = Field(description="Количество отображений на странице")
    

class PlaylistsResponse(BaseModel):
    data: List[Playlist]
    meta: Meta