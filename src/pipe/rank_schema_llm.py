"""LLM-based schema ranking."""

from typing import Any, List

from src.config import OpenAIConfig
from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.llm_util import extract_object
from src.pipe.rank_schema import RankSchemaResd
from src.pipe.rank_schema_prompts.v1 import RANK_SCHEMA_ITEMS_V1
from src.pipe.schema_repo import DatabaseSchemaRepo
from src.pipe.util_processors import InitData


class RankSchemaItems(PromptProcessor[InitData.Model, RankSchemaResd.Model]):
    """
    Rank schema items using language model.

    Parameters
    ----------
    prop_name : str
        Property name for output
    openai_config: OpenAIConfig
        OpenAI client configuration
    tables_path : str
        Path to tables JSON file
    model : str
        Model identifier to use
    """

    def __init__(
        self, tables_path: str, openai_config: OpenAIConfig, model: str
    ) -> None:
        super().__init__(RankSchemaResd.Model, openai_config=openai_config, model=model)
        self.schema_repo = DatabaseSchemaRepo(tables_path)

    def _get_result_data(
        self, row: InitData.Model, llm_output: List[str]
    ) -> RankSchemaResd.Model:
        return RankSchemaResd.Model(schema_items=llm_output, **row.dict())

    def _process_output(self, row: InitData.Model, output: str) -> Any:
        return extract_object(output)

    def extract_schema_items(self, row: InitData.Model) -> list[str]:
        """
        Extract all schema items from database.

        Parameters
        ----------
        row : dict
            Data row with database ID

        Returns
        -------
        list
            List of schema item strings
        """
        db_id = row.db_id
        schema = self.schema_repo.dbs[db_id]
        schema_items = []

        for table_name, columns in schema.tables.items():
            schema_items.append(f"TABLE:{table_name}")
            for col_name, _col_data in columns.items():
                schema_items.append(f"COLUMN:{table_name}.{col_name}")
        return schema_items

    def _get_prompt(self, row: InitData.Model) -> str:
        question = row.question
        schema_items = self.extract_schema_items(row)
        return RANK_SCHEMA_ITEMS_V1.format(question=question, schema_items=schema_items)
