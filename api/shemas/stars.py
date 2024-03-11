from pydantic import *
from pydantic.fields import Field
from typing import Optional, Union
from classes.WebModels import Stars, Track, Playlist

class Meta(BaseModel):
    page: int = Field(description="Текущая страница")
    count: int = Field(description="Количество отображений на странице")

class MetaAdd(BaseModel):
    index: int = Field(description="Позиция трека в звездочках")
    

class StarsResponse(BaseModel):
    data: Optional[Stars] = None
    meta: Meta

class StarsTrackResponse(BaseModel):
    data: Optional[Track] = None

class StarsTrackAddResponse(BaseModel):
    data: Union[Playlist, Track]
    meta: MetaAdd