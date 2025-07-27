"""
Pool entity `NodePool`
"""

from services.persiktunes import NodePool

instance = None


def get_instance():
    """Singleton getter"""
    global instance
    if instance is None:
        instance = NodePool()
    return instance
