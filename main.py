"""Main entry point for the MaskSQL pipeline."""

import argparse
import asyncio
import logging
import os
from pathlib import Path

from config import MaskSqlConfig
from src.pipe.add_schema import AddFilteredSchema
from src.pipe.add_symb_schema import AddSymbolicSchema
from src.pipe.attack import AddInferenceAttack
from src.pipe.copy_transformer import CopyTransformer
from src.pipe.det_mask import AddSymbolicQuestion
from src.pipe.detect_entities import DetectValues
from src.pipe.exec_acc import CalcExecAcc
from src.pipe.exec_conc_sql import ExecuteConcreteSql
from src.pipe.gen_masked_sql import GenerateSymbolicSql
from src.pipe.link_schema import LinkSchema
from src.pipe.pipeline import Pipeline
from src.pipe.processor.limit_list import LimitJson
from src.pipe.processor.list_processor import JsonListProcessor
from src.pipe.rank_schema import RankSchemaResd
from src.pipe.repair_sql import RepairSQL
from src.pipe.repair_symb_sql import RepairSymbolicSQL
from src.pipe.resdsql import AddResd
from src.pipe.results import Results
from src.pipe.run_resdsql import RunResdsql
from src.pipe.slm_sql import SlmSQL
from src.pipe.symb_table import AddSymbolTable
from src.pipe.unmask import AddConcreteSql
from src.pipe.value_links import LinkValues
from src.utils.logging import configure_logging


logger = logging.getLogger(__name__)


def clean_data_directory(data_dir: str) -> None:
    """Clean intermediate files from the data directory.

    Removes files matching the pattern [0-9]*_* but excludes files starting with 1_*.
    This is used to clean up intermediate pipeline output files while preserving
    the initial input files.

    Parameters
    ----------
    data_dir : str
        Path to the data directory to clean.
    """
    data_path = Path(data_dir)

    if not data_path.exists():
        logger.error(f"Data directory does not exist: {data_dir}")
        return

    if not data_path.is_dir():
        logger.error(f"Path is not a directory: {data_dir}")
        return

    # Find all files matching [0-9]*_* pattern
    files_to_delete = []
    for file_path in data_path.iterdir():
        if file_path.is_file():
            name = file_path.name
            # Check if filename starts with a digit and contains underscore
            if name[0].isdigit() and "_" in name and not name.startswith("1_"):
                files_to_delete.append(file_path)

    if not files_to_delete:
        logger.info(f"No files to clean in {data_dir}")
        return

    logger.info(f"Cleaning {len(files_to_delete)} files from {data_dir}")
    for file_path in files_to_delete:
        try:
            file_path.unlink()
            logger.debug(f"Deleted: {file_path.name}")
        except Exception as e:
            logger.error(f"Failed to delete {file_path.name}: {e}")

    logger.info("Cleanup complete")


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
    # Always use RESDSQL for schema ranking
    # RunResdsql will skip if output already exists (unless force=True)
    device = os.environ.get("TORCH_DEVICE", "cpu")
    rank_schema = [
        RunResdsql(
            conf.tables_path,
            conf.input_path,
            conf.db_path,
            conf.resd_path,
            device=device,
        ),
        AddResd(conf.resd_path),
        RankSchemaResd(conf.tables_path),
    ]
    return [
        LimitJson(),
        *rank_schema,
        # ResdItemCount(),
        AddFilteredSchema(conf.tables_path),
        AddSymbolTable(conf.tables_path),
        SlmSQL("slm_sql", model=conf.slm),
        DetectValues("values", model=conf.slm),
        LinkValues("value_links", model=conf.slm),
        CopyTransformer("value_links", "filtered_value_links"),
        LinkSchema("schema_links", model=conf.slm),
        CopyTransformer("schema_links", "filtered_schema_links"),
        AddSymbolicSchema(conf.tables_path),
        AddSymbolicQuestion(),
        GenerateSymbolicSql("symbolic", model=conf.llm),
        RepairSymbolicSQL("symbolic", model=conf.llm),
        AddConcreteSql(),
        ExecuteConcreteSql(conf.db_path),
        RepairSQL("pred_sql", model=conf.slm),
        CalcExecAcc(conf.db_path, conf.policy),
        AddInferenceAttack("attack", model=conf.llm),
        # PrintProps(['question', 'symbolic.question', 'attack'])
        Results(),
    ]


async def main() -> None:
    """Run the MaskSQL main pipeline."""
    parser = argparse.ArgumentParser(description="MaskSQL")
    parser.add_argument(
        "--data", type=str, required=False, help="Data directory", default="data"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean intermediate files from data directory",
    )
    args = parser.parse_args()
    configure_logging()

    # Handle clean operation
    if args.clean:
        clean_data_directory(args.data)

    # Run pipeline (always uses RESDSQL for schema ranking)
    conf = MaskSqlConfig(args.data, "full")
    pipeline_stages = create_pipeline_stages(conf)
    pipeline = Pipeline(pipeline_stages)
    await pipeline.run(conf.input_path)


if __name__ == "__main__":
    asyncio.run(main())
