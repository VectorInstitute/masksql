"""Input model for the MaskSQL system.

This module defines the input data structure for the MaskSQL system,
representing a natural language question to be converted to SQL.
"""

from typing import Any, Dict

from src.models.base_object import BaseObject


class MaskSqlInput(BaseObject):
    """Input data for the MaskSQL system.

    This class represents an input to the MaskSQL system, containing
    a natural language question about a database and optional annotations.

    Attributes
    ----------
        db_id: Identifier of the database the question is about
        question: Natural language question text
        query: Optional SQL query (may be empty for new inputs)
        annotated_links: Dictionary of annotations for the question
    """

    db_id: str
    question: str
    query: str
    annotated_links: Dict[str, Any]
