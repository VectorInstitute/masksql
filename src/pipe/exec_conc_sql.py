"""Concurrent SQL execution utilities."""

from typing import Any

from pydantic import BaseModel

from src.pipe.processor.list_processor import JsonListProcessor
from src.pipe.sqlite_facade import SqliteFacade
from src.pipe.unmask import AddConcreteSql
from src.utils.logging import logger


class PreEvaluation(BaseModel):
    """
    Data model for preliminary SQL execution evaluation.

    Stores accuracy score, error messages, and predicted results
    from SQL query execution.
    """

    acc: float
    err: str
    pred_res: list[Any] | None


class ExecuteConcreteSql(
    JsonListProcessor[AddConcreteSql.Model, "ExecuteConcreteSql.Model"]
):
    """
    Execute concrete SQL queries and compare results with gold standard.

    Executes generated concrete SQL queries against the database and compares
    their results with expected gold standard query results.

    Parameters
    ----------
    database_dir : str
        Directory containing SQLite database files
    """

    class Model(AddConcreteSql.Model):
        """Data model for concrete SQL execution with preliminary evaluation results."""

        pre_eval: PreEvaluation

    def __init__(self, database_dir: str) -> None:
        super().__init__(self.Model, force=True)
        self.dbf = SqliteFacade(database_dir)

    async def _process_row(self, row: AddConcreteSql.Model) -> Model:
        """
        Calculate execution accuracy for a row.

        Parameters
        ----------
        row : AddConcreteSql.Model
            Data row with query, concrete_sql, and db_id

        Returns
        -------
        ExecuteConcreteSql.Model
            Row with pre_eval results added
        """
        gold = row.query
        pred = row.concrete_sql
        db_id = row.db_id
        try:
            gold_res, _ = self.dbf.exec_query_sync(db_id, gold)
            pred_res, pred_err = self.dbf.exec_query_sync(db_id, pred)
            acc = 1 if gold_res == pred_res else 0
            if pred_res is not None and len(pred_res) > 5:
                logger.debug(
                    f"Pred results was limited: original size = {len(pred_res)}"
                )
                pred_res = pred_res[:5]
            if pred_err is None:
                pred_err = ""
            # if pred_err is not None:
            #     err = pred_err
            # elif acc == 0:
            #     err = "The predicted SQL is executable but the execution result is
            #           different from the gold execution result"
            # else:
            #     err = None

            pre_eval = PreEvaluation(acc=acc, err=pred_err, pred_res=pred_res)

            return self.Model(**row.dict(), pre_eval=pre_eval)
        except Exception as e:
            print(e)
            raise e

    # async def run(self, input_file):
    #     output_file = self.get_output_file(input_file)
    #     if not self.force and os.path.exists(output_file):
    #         print(f"File exists: {output_file}, skipping.")
    #         return output_file
    #
    #     with open(input_file) as f:
    #         in_data = json.load(f)
    #
    #     output_rows = []
    #     for i, row in enumerate(
    #         tqdm.tqdm(in_data, desc=self.name, total=len(in_data))):
    #         exec_acc = await self.get_exec_acc(row)
    #         row['exec_acc'] = exec_acc
    #         if exec_acc == 0:
    #             output_rows.append(row)
    #
    #     with open(output_file, "w") as f:
    #         f.write(json.dumps(output_rows, indent=4))
    #     return output_file
