from pydantic import *
from pydantic.fields import Field
from typing import Optional
from classes.WebModels import Stars, Track

class Meta(BaseModel):
    page: int = Field(description="Текущая страница")
    count: int = Field(description="Количество отображений на странице")
    

class StarsResponse(BaseModel):
    data: Optional[Stars] = None
    meta: Meta

class StarsTrackResponse(BaseModel):
    data: Optional[Track] = None