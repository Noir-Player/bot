from beanie import Document, Indexed
from pydantic import Field, BaseModel

from typing import Annotated


class WebhookModel(BaseModel):
    """
    Represents a webhook configuration in the database.
    This model is used to store webhook settings for the application.
    """

    id: int = Field(
        description="The ID of the webhook endpoint.",
    )

    name: str = Field(
        description="The name of the webhook.",
    )

    image_url: str | None = Field(
        default=True,
        pattern=r"https://.*",
        description="Image URL of the webhook.",
    )


class SetupModel(BaseModel):
    """
    Represents the setup document in the database.
    This document is used to store configuration settings for the application.
    """

    admin_role_id: int | None = Field(
        None,
        description="The ID of the role that has administrative privileges in this guild.",
    )

    dj_role_id: int | None = Field(
        None, description="The ID of the role that has DJ privileges in this guild."
    )

    channel_id: int | None = Field(
        None, description="The ID of the channel where the bot will operate."
    )

    volume_step: int = Field(
        default=25, description="The step size for volume adjustments in the bot."
    )

    avaible_equalizer: bool = Field(
        True, description="Flag indicating whether the equalizer is available for use."
    )

    webhook: WebhookModel | None = Field(
        None, description="Configuration for the webhook associated with this setup."
    )

    radio: bool = Field(False)


class SetupDocument(SetupModel, Document):
    guild_id: Annotated[int, Indexed(int, unique=True)] = Field(
        description="The ID of the guild (server) this setup belongs to.",
        alias="_id",
    )

    class Settings:
        keep_nulls = False
        name = "setups"
