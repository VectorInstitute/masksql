"""Result model for the MaskSQL system.

This module defines the result data structure for the MaskSQL system,
representing the outcome of processing a database question.
"""

from src.models.data_point import DataPoint


class MaskSqlResult(DataPoint):
    """Result of processing a database question.

    This class represents the result of processing a database question,
    containing the predicted SQL query.

    Attributes
    ----------
        db_id: Identifier of the database the question is about
        question: Natural language question text
        pred_sql: Predicted SQL query for the question
    """

    pred_sql: str
