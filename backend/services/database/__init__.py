def get_documents():
    """Get all documents for Beanie"""
    from .models import setup

    return [
        setup.SetupDocument,
    ]
