"""List transformation base classes."""

import os
from abc import ABC

from src.data_models.base_object import BaseObject
from src.pipeline.base_processor.list_processor import JsonListProcessor


FORCE = int(os.environ.get("FORCE", "0")) > 0


class JsonListTransformer(JsonListProcessor[BaseObject, BaseObject], ABC):
    """
    Base class for transforming lists of JSON objects.

    Extends JsonListProcessor to provide a foundation for processors
    that transform one type of object into another of the same type.
    """

    pass
