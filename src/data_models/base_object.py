"""Base object model for all entities in the system.

This module defines the base object class that all other model classes
in the system inherit from, providing common functionality.
"""

from pydantic import BaseModel


class BaseObject(BaseModel):
    """Base class for all objects in the system.

    This class provides a common base for all objects in the system,
    ensuring they all have a unique identifier.

    Attributes
    ----------
        idx: Unique identifier for the object
    """

    idx: str
