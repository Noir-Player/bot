def get_documents():
    """Get all documents for Beanie"""
    from .models import setup
    from .models import star
    from .models import playlist

    return [setup.SetupDocument, star.StarDocument, playlist.PlaylistDocument]
