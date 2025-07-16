def get_documents():
    """Get all documents for Beanie"""
    from . import (
        user,
        guild,
        track,
        playlist,
        history,
        session,
        settings,
    )

    return [
        user.User,
        guild.Guild,
        track.Track,
        playlist.Playlist,
        history.History,
        session.Session,
        settings.Settings,
    ]
