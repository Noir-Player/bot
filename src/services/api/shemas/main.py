from pydantic import *
from pydantic.fields import Field


class StatusResponse(BaseModel):
    guilds: int = Field(description= "Количество серверов")
    players: int = Field(description= "Количество плееров")
    uptime: int = Field(description= "Аптайм")
    ping: float = Field(description= "Задержка сервера")