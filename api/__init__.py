from fastapi import FastAPI
import api.routers as routers

from uuid import UUID
from fastapi_sessions.backends.implementations import InMemoryBackend

from api.routers.helpers.session_verify import SessionData, BasicVerifier, HTTPException



class NoirAPI(FastAPI):
    def init_sessions(self):
        self._sessions = InMemoryBackend[UUID, SessionData]()
        self._verifier = BasicVerifier(
            identifier="general_verifier",
            auto_error=True,
            backend=self._sessions,
            auth_http_exception=HTTPException(status_code=403, detail="invalid session"),
        )


    @property
    def sessions(self) -> InMemoryBackend[UUID, SessionData]:
        return self._sessions
    
    @property
    def verifier(self) -> BasicVerifier:
        return self._verifier



def __init__(bot) -> NoirAPI:
    """Return pathed FastAPI obj"""
    api = NoirAPI(
        title="Noir Player API",
        description="Noir Player API app, works on sessions without JWT",
        version="0.1.0"
    )

    api.init_sessions()

    routers.include_modules(api, bot)

    return api
