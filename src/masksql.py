"""Main module for the MaskSQL system.

This module provides the core functionality for the MaskSQL system,
which processes natural language questions and converts them to SQL queries.
"""

import os
import uuid

from src.config import MaskSqlConfig, OpenAIConfig
from src.data_models.masksql_input import MaskSqlInput
from src.data_models.masksql_output import MaskSqlOutput
from src.pipeline.add_schema import AddFilteredSchema
from src.pipeline.add_symb_schema import AddSymbolicSchema
from src.pipeline.add_symbolic_question import AddSymbolicQuestion
from src.pipeline.attack.add_inference_attack import AddInferenceAttack
from src.pipeline.base_processor.limit_list import LimitJson
from src.pipeline.base_processor.list_processor import JsonListProcessor
from src.pipeline.detect_values.detect_values import DetectValues
from src.pipeline.exec_acc import CalcExecAcc
from src.pipeline.exec_conc_sql import ExecuteConcreteSql
from src.pipeline.gen_sql.gen_masked_sql import GenerateSymbolicSql
from src.pipeline.init_data import InitData
from src.pipeline.link_schema.link_schema import (
    FilterSchemaLinksModel,
    LinkSchema,
)
from src.pipeline.link_values.link_values import FilterValueLinksModel, LinkValues
from src.pipeline.pipeline import Pipeline
from src.pipeline.rank_schema import RankSchemaResd
from src.pipeline.rank_schema_llm import RankSchemaItems
from src.pipeline.repair_sql.repair_sql import RepairSQL
from src.pipeline.repair_symb_sql.repair_symb_sql import RepairSymbolicSQL
from src.pipeline.resd.add_resd import AddResd
from src.pipeline.resd.run_resdsql import RunResdsql
from src.pipeline.results import Results
from src.pipeline.symb_table import AddSymbolTable
from src.pipeline.unmask import AddConcreteSql
from src.pipeline.util_processors.copy_transformer import CopyTransformer
from src.utils.json_io import read_json, write_json


CUDA_VISIBLE_DEVICES = os.environ.get("CUDA_VISIBLE_DEVICES", "0")


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
                conf.tables_path,
                conf.db_path,
                conf.resd_path,
                device=CUDA_VISIBLE_DEVICES,
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

    Parameters
    ----------
    name : str
        String identifier of the configuration, used as the name for subdirectory within
        the cache directory.
    data_dir : str
        Base directory for data files.
    cache_dir : str
        Base directory for cache files.
    policy : str
        Policy configuration for execution.
    slm : str
        Small language model identifier.
    llm : str
        Large language model identifier.
    resd : bool
        Flag to enable or disable RESD (RESidual Disambiguation) mode.
    openai : OpenAIConfig
        OpenAI API client configurations.

    Attributes
    ----------
        conf: Configuration object for the MaskSQL system
        pipeline: Processing pipeline that transforms inputs to outputs
    """

    conf: MaskSqlConfig
    pipeline: Pipeline

    def __init__(
        self,
        name: str,
        data_dir: str,
        cache_dir: str,
        policy: str,
        slm: str,
        llm: str,
        resd: bool,
        openai: OpenAIConfig,
    ) -> None:
        conf = MaskSqlConfig(
            name=name,
            data_dir=data_dir,
            cache_dir=cache_dir,
            policy=policy,
            slm=slm,
            llm=llm,
            resd=resd,
            openai=openai,
        )
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

    async def query_batch(self, batch_file: str) -> list[MaskSqlOutput]:
        """Process a batch of questions from a file.

        Args:
            batch_file: Path to a JSON file containing questions to process

        Returns
        -------
            List of processed outputs
        """
        input_data = read_json(batch_file, MaskSqlInput)
        return await self.pipeline.run(input_data)

    async def evaluate(self) -> list[MaskSqlOutput]:
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
        return MaskSQL(**conf.dict())
