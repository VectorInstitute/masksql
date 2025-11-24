"""Main module for the MaskSQL system.

This module provides the core functionality for the MaskSQL system,
which processes natural language questions and converts them to SQL queries.
"""

import os
import uuid
from typing import List

from src.config import MaskSqlConfig
from src.models.masksql_input import MaskSqlInput
from src.models.masksql_output import MaskSqlOutput
from src.pipe.add_schema import AddFilteredSchema
from src.pipe.add_symb_schema import AddSymbolicSchema
from src.pipe.attack import AddInferenceAttack
from src.pipe.copy_transformer import CopyTransformer
from src.pipe.det_mask import AddSymbolicQuestion
from src.pipe.detect_entities import DetectValues
from src.pipe.exec_acc import CalcExecAcc
from src.pipe.exec_conc_sql import ExecuteConcreteSql
from src.pipe.gen_masked_sql import GenerateSymbolicSql
from src.pipe.link_schema import FilterSchemaLinksModel, LinkSchema
from src.pipe.pipeline import Pipeline
from src.pipe.processor.limit_list import LimitJson
from src.pipe.processor.list_processor import JsonListProcessor
from src.pipe.rank_schema import RankSchemaResd
from src.pipe.rank_schema_llm import RankSchemaItems
from src.pipe.repair_sql import RepairSQL
from src.pipe.repair_symb_sql import RepairSymbolicSQL
from src.pipe.resdsql import AddResd
from src.pipe.results import Results
from src.pipe.run_resdsql import RunResdsql
from src.pipe.symb_table import AddSymbolTable
from src.pipe.unmask import AddConcreteSql
from src.pipe.util_processors import InitData
from src.pipe.value_links import FilterValueLinksModel, LinkValues
from src.utils.json_io import read_json, write_json


TORCH_DEVICE = os.environ.get("TORCH_DEVICE", "cpu")


def create_pipeline_stages(conf: MaskSqlConfig) -> list[JsonListProcessor]:
    """Create the pipeline stages for MaskSQL processing.

    Parameters
    ----------
    conf : MaskSqlConfig
        Configuration object containing pipeline settings.

    Returns
    -------
    list
        List of pipeline stage objects to execute.
    """
    rank_schema: list[JsonListProcessor] = []
    if conf.resd:
        rank_schema = [
            RunResdsql(
                conf.tables_path, conf.db_path, conf.resd_path, device=TORCH_DEVICE
            ),
            AddResd(conf.resd_path),
            RankSchemaResd(conf.tables_path),
        ]
    else:
        rank_schema = [RankSchemaItems(conf.tables_path, conf.openai, model=conf.slm)]
    return [
        LimitJson(),
        InitData(),
        *rank_schema,
        # ResdItemCount(),
        AddFilteredSchema(conf.tables_path),
        AddSymbolTable(conf.tables_path),
        # SlmSQL("slm_sql", conf.openai, model=conf.slm),
        DetectValues(conf.openai, model=conf.slm),
        LinkValues(conf.openai, model=conf.slm),
        CopyTransformer("value_links", "filtered_value_links", FilterValueLinksModel),
        LinkSchema(conf.openai, model=conf.slm),
        CopyTransformer(
            "schema_links", "filtered_schema_links", FilterSchemaLinksModel
        ),
        AddSymbolicSchema(conf.tables_path),
        AddSymbolicQuestion(),
        GenerateSymbolicSql(conf.openai, model=conf.llm),
        RepairSymbolicSQL(conf.openai, model=conf.llm),
        AddConcreteSql(),
        ExecuteConcreteSql(conf.db_path),
        RepairSQL(conf.openai, model=conf.slm),
        CalcExecAcc(conf.db_path, conf.policy),
        AddInferenceAttack(conf.openai, model=conf.llm),
        # # PrintProps(['question', 'symbolic.question', 'attack'])
        Results(),
    ]


class MaskSQL:
    """Main class for the MaskSQL system.

    This class provides the interface for processing natural language questions
    and converting them to SQL queries using a pipeline of processing stages.

    Attributes
    ----------
        conf: Configuration object for the MaskSQL system
        pipeline: Processing pipeline that transforms inputs to outputs
    """

    conf: MaskSqlConfig
    pipeline: Pipeline

    def __init__(self, conf: MaskSqlConfig) -> None:
        self.conf = conf
        pipeline_stages = create_pipeline_stages(conf)
        self.pipeline = Pipeline(conf.name, conf.cache_dir, pipeline_stages)

    async def query(self, db_id: str, question: str) -> MaskSqlOutput:
        """Process a single natural language question.

        Args:
            db_id: Database identifier
            question: Natural language question to process

        Returns
        -------
            Processed output containing the SQL query and other information
        """
        data = MaskSqlInput(
            idx=str(uuid.uuid4()),
            db_id=db_id,
            question=question,
            query="",
            annotated_links={},
        )
        results = await self.pipeline.run([data])
        return results[0]

    async def query_batch(self, batch_file: str) -> List[MaskSqlOutput]:
        """Process a batch of questions from a file.

        Args:
            batch_file: Path to a JSON file containing questions to process

        Returns
        -------
            List of processed outputs
        """
        input_data = read_json(batch_file, MaskSqlInput)
        return await self.pipeline.run(input_data)

    async def evaluate(self) -> List[MaskSqlOutput]:
        """Evaluate the system on a dataset and save results.

        Reads input data from the configured input path, processes it,
        and writes the results to the configured output path.

        Returns
        -------
            List of processed outputs
        """
        input_data = read_json(self.conf.input_path, MaskSqlInput)
        results = await self.pipeline.run(input_data)
        write_json(self.conf.output_path, results)
        return results

    @staticmethod
    def from_config(config_path: str) -> "MaskSQL":
        """Create a MaskSQL instance from a configuration file.

        Args:
            config_path: Path to a YAML configuration file

        Returns
        -------
            Configured MaskSQL instance
        """
        conf = MaskSqlConfig.from_yaml(config_path)
        return MaskSQL(conf)
