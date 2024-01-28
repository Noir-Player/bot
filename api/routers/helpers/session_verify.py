from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi import HTTPException

from uuid import UUID

from pydantic import BaseModel
from typing import Any



cookie = SessionCookie(
    cookie_name="session",
    identifier="session_data",
    auto_error=True,
    secret_key="9c11198a2f8ba23ef6ccf7f7bc7b3588",
    cookie_params=CookieParameters(max_age = 30 * 24),
)
"Session cookie object"


class DiscordProfileData(BaseModel):
    """Discord Api Profile Model"""
    accent_color: int | None = None
    avatar: str | None = None
    avatar_decoration_data: Any | None = None
    banner: str | None = None
    banner_color: str
    discriminator: str
    flags: int | None = None
    global_name: str
    id: str
    locale: str | None = None
    mfa_enabled: bool
    premium_type: int | None = None
    public_flags: int | None = None
    username: str
    verified: bool | None = None
    email: str | None = None


class SessionData(BaseModel):
    user: DiscordProfileData | None = None
    connections: Any | None = None
    theme: str = "dark"
    player: int | None = None
    oauth2_token: str | None = None



class BasicVerifier(SessionVerifier[UUID, SessionData]):
    def __init__(
        self,
        *,
        identifier: str,
        auto_error: bool,
        backend: InMemoryBackend[UUID, SessionData],
        auth_http_exception: HTTPException,
    ):
        self._identifier = identifier
        self._auto_error = auto_error
        self._backend = backend
        self._auth_http_exception = auth_http_exception

    @property
    def identifier(self):
        return self._identifier

    @property
    def backend(self):
        return self._backend

    @property
    def auto_error(self):
        return self._auto_error

    @property
    def auth_http_exception(self):
        return self._auth_http_exception

    def verify_session(self, model: SessionData) -> bool:
        """If the session exists, it is valid"""
        return True