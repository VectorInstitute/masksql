"""SQL execution accuracy calculation."""

from typing import Any

from pydantic import BaseModel

from src.pipe.processor.list_processor import JsonListProcessor
from src.pipe.repair_sql import RepairSQL
from src.pipe.sqlite_facade import SqliteFacade


class EvaluationData(BaseModel):
    """
    Data model for SQL execution evaluation results.

    Stores accuracy score and comparison data between gold standard
    and predicted SQL query results.
    """

    acc: float
    gold: list[Any] | None
    pred: list[Any] | None
    pred_err: str | None


class CalcExecAcc(JsonListProcessor[RepairSQL.Model, "CalcExecAcc.Model"]):
    """
    Calculate execution accuracy by comparing SQL query results.

    Executes both gold standard and predicted SQL queries and compares their
    results to determine accuracy.

    Parameters
    ----------
    database_dir : str
        Directory containing SQLite database files
    policy : str
        Policy identifier for tracking failures
    """

    class Model(RepairSQL.Model):
        """Data model for execution accuracy calculation with evaluation results."""

        eval: EvaluationData

    def __init__(self, database_dir: str, policy: str) -> None:
        super().__init__(self.Model, force=True)
        self.dbf = SqliteFacade(database_dir)
        self.count = 0
        self.policy = policy
        self.failures_arr: list[Any] = []

    async def _process_row(self, row: "RepairSQL.Model") -> "CalcExecAcc.Model":
        gold = row.query
        pred = row.pred_sql
        db_id = row.db_id
        self.count += 1
        try:
            gold_res, _ = self.dbf.exec_query_sync(db_id, gold)
            pred_res, err = self.dbf.exec_query_sync(db_id, pred)
            if gold_res == pred_res:
                acc = 1
            else:
                acc = 0
                self.failures_arr.append(row.idx)

            eval_data = EvaluationData(
                acc=acc,
                gold=gold_res,
                pred=pred_res,
                pred_err=err if err is not None else "",
            )

            return self.Model(**row.dict(), eval=eval_data)
        except Exception as e:
            print(e)
            raise e

    # def _post_run(self):
    #     self.failures(self.failures_arr)
    #
    # def failures(self, arr):
    #     path= f"data/{self.policy}/EA_failures.json"
    #     write_json(path,arr)
