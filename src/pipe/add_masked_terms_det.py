"""Module for deterministic masking of terms in natural language questions."""

from typing import Any

from loguru import logger

from src.pipe.processor.list_transformer import JsonListTransformer
from src.pipe.utils import replace_str


class AddMaskedTermsDeterministic(JsonListTransformer):
    """
    Deterministic processor for masking terms in natural language questions.

    This class performs rule-based masking of schema and value references in questions,
    replacing them with symbolic representations based on schema and value links.
    """

    def __init__(self) -> None:
        super().__init__(force=True)

    def get_symbol(
        self, schema_items: list[str] | str, symbol_table: dict[str, str]
    ) -> str:
        """
        Get symbolic representation for schema items.

        Parameters
        ----------
        schema_items : list[str] | str
            Schema item(s) to get symbols for.
        symbol_table : dict[str, str]
            Mapping from schema items to their symbolic representations.

        Returns
        -------
        str
            Comma-separated symbolic representations.
        """
        if not isinstance(schema_items, list):
            schema_items = [schema_items]
        symbols: list[str | None] = []
        for schema_item in schema_items:
            schema_item_parts = schema_item.split(":")
            schema_item_name = schema_item_parts[1]
            symbol = symbol_table.get(schema_item_name)
            symbols.append(symbol)
        return ",".join(str(s) for s in symbols if s is not None)

    def symbolize_term(
        self,
        question: str,
        question_term: str,
        schema_items: str,
        symbol_table: dict[str, str],
    ) -> str:
        """
        Replace a question term with its symbolic representation.

        Parameters
        ----------
        question : str
            The question text to modify.
        question_term : str
            The term in the question to replace.
        schema_items : str
            Schema item(s) corresponding to the term.
        symbol_table : Dict[str, str]
            Mapping from schema items to symbols.

        Returns
        -------
        str
            Question with term replaced by symbol.
        """
        symbol = self.get_symbol(schema_items, symbol_table)
        return replace_str(question, question_term, symbol)

    def symbolize_value(
        self,
        question: str,
        question_term: str,
        column_ref: str,
        updated_schema_links: dict[str, str],
        filtered_value_links: dict[str, str],
        symbol_table: dict[str, str],
    ) -> str:
        """
        Replace a value term with its symbolic representation.

        Parameters
        ----------
        question : str
            The question text to modify.
        question_term : str
            The value term in the question to replace.
        column_ref : str
            Reference to the column containing this value.
        updated_schema_links : Dict[str, str]
            Updated schema links mapping.
        filtered_value_links : Dict[str, str]
            Filtered value links mapping.
        symbol_table : Dict[str, str]
            Mapping from schema items to symbols.

        Returns
        -------
        str
            Question with value replaced by symbol and evidence added.
        """
        value_symbol = f"[V{self.vid}]"
        if (
            column_ref in filtered_value_links.values()
            or f"COLUMN:{column_ref}" in updated_schema_links.values()
        ):
            column_symbol = symbol_table[column_ref]
        else:
            column_symbol = column_ref
        self.vid += 1
        evidence = f"{value_symbol} is a value of the column {column_symbol}"
        self.value_dict[value_symbol] = question_term
        symbolic_question = replace_str(question, question_term, value_symbol)
        return f"{symbolic_question}; {evidence}"

    def add_tables_of_columns(
        self, schema_links: dict[str, str], filtered_schema_links: dict[str, str]
    ) -> dict[str, str]:
        """
        Add table references for columns in filtered schema links.

        Parameters
        ----------
        schema_links : Dict[str, str]
            All schema links from question terms to schema items.
        filtered_schema_links : Dict[str, str]
            Subset of schema links to use.

        Returns
        -------
        Dict[str, str]
            Updated schema links with tables included.
        """
        updated_schema_links = filtered_schema_links.copy()
        tables = set()
        for schema_items in filtered_schema_links.values():
            if schema_items is None:
                logger.error(f"Invalid schema item: {schema_items}")
                continue
            items = (
                [schema_items] if not isinstance(schema_items, list) else schema_items
            )
            for schema_item in items:
                if schema_item.startswith("COLUMN"):
                    col_ref = schema_item.split(":")[1]
                    table_name = col_ref.split(".")[0]
                    tables.add(table_name)

        for question_term, schema_items in schema_links.items():
            items = (
                [schema_items] if not isinstance(schema_items, list) else schema_items
            )
            for schema_item in items:
                if schema_item.startswith("TABLE"):
                    assert len(schema_items) == 1
                    table_name = schema_item.split(":")[1]
                    if table_name in tables:
                        updated_schema_links[question_term] = schema_item
        return updated_schema_links

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        self.vid: int = 1
        self.value_dict: dict[str, str] = {}
        filtered_schema_links = row["filtered_schema_links"]
        schema_links = row["schema_links"]
        question = row["question"]
        symbol_table = row["symbolic"]["to_symbol"]
        updated_schema_links = self.add_tables_of_columns(
            schema_links, filtered_schema_links
        )
        masked_terms = []

        symbolic_question = question
        masked = 0

        value_links = row["value_links"]
        filtered_value_links = row["filtered_value_links"]

        if isinstance(value_links, (list, str)):
            logger.error(f"Invalid value links: {value_links}")
            value_links = {}

        if isinstance(filtered_value_links, (list, str)):
            logger.error(f"Invalid value links: {filtered_value_links}")
            filtered_value_links = {}

        for question_term, schema_item in value_links.items():
            try:
                symbolic_question = self.symbolize_value(
                    symbolic_question,
                    question_term,
                    schema_item,
                    updated_schema_links,
                    filtered_value_links,
                    symbol_table,
                )
                masked_terms.append(question_term)
                masked += 1
            except Exception as e:
                logger.error(
                    f"Failed to mask {question_term}:{schema_item}, error={e} "
                )

        for question_term, schema_items in updated_schema_links.items():
            try:
                symbolic_question = self.symbolize_term(
                    symbolic_question, question_term, schema_items, symbol_table
                )
                masked_terms.append(question_term)
                masked += 1
            except Exception as e:
                logger.error(
                    f"Failed to mask {question_term}:{schema_items}, error={e} "
                )
        row["symbolic"].update({"masked_terms": masked_terms})
        return row
