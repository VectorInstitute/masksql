"""Data point model for representing database questions.

This module defines the basic data point structure used for
representing questions about databases in the system.
"""

from pydantic import BaseModel


class DataPoint(BaseModel):
    """Base class for representing a database question.

    This class represents a question about a specific database,
    providing the basic fields needed for database question answering.

    Attributes
    ----------
        db_id: Identifier of the database the question is about
        question: Natural language question text
    """

    db_id: str
    question: str
