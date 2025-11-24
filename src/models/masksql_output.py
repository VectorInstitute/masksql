"""Output model for the MaskSQL system.

This module defines the output data structure for the MaskSQL system,
representing the result of processing a natural language question.
"""

from src.models.base_object import BaseObject
from src.pipe.exec_acc import EvaluationData


class MaskSqlOutput(BaseObject):
    """Output data from the MaskSQL system.

    This class represents the result of processing a natural language question,
    containing the original question and the generated SQL query.

    Attributes
    ----------
        db_id: Identifier of the database the question is about
        question: Original natural language question text
        query: Generated SQL query
    """

    db_id: str
    question: str
    eva: EvaluationData
