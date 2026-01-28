"""Deterministic masking of terms in questions."""

import logging

from src.pipeline.add_symb_schema import AddSymbolicSchema, SymbolicSchema
from src.pipeline.base_processor.list_processor import JsonListProcessor
from src.utils.strings import replace_str


logger = logging.getLogger(__name__)


class SymbolicQuestion(SymbolicSchema):
    """
    Data model for questions with symbolic representations.

    Extends SymbolicSchema with question-specific fields for tracking
    masked terms and their replacements.
    """

    question: str
    to_value: dict[str, str]
    masked: int
    masked_terms: list[str]


class AddSymbolicQuestion(
    JsonListProcessor[AddSymbolicSchema.Model, "AddSymbolicQuestion.Model"]
):
    """
    Add symbolic representations to questions by replacing schema and value terms.

    Replaces database schema terms (tables, columns) and values in questions with
    symbolic placeholders (e.g., [T1], [C2], [V3]) for privacy-preserving SQL
    generation.
    """

    class Model(AddSymbolicSchema.Model):
        """Data model for symbolic question processing with symbolic field."""

        symbolic: SymbolicQuestion

    def __init__(self) -> None:
        super().__init__(self.Model, force=True)

    def get_symbol(
        self, schema_items: list[str] | str, symbol_table: dict[str, str]
    ) -> str:
        """
        Get symbolic representation for schema items.

        Parameters
        ----------
        schema_items : list[str] | str
            Schema item(s) to look up in the symbol table
        symbol_table : dict[str, str]
            Mapping from schema items to their symbols

        Returns
        -------
        str
            Comma-separated symbols for the schema items
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
        Replace a schema term in the question with its symbolic representation.

        Parameters
        ----------
        question : str
            The question text
        question_term : str
            The term in the question to symbolize
        schema_items : str
            The schema items associated with this term
        symbol_table : dict[str, str]
            Mapping from schema items to their symbols

        Returns
        -------
        str
            Question with the term replaced by its symbol
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
        Replace a value in the question with a symbolic representation.

        Parameters
        ----------
        question : str
            The question text
        question_term : str
            The value term in the question to symbolize
        column_ref : str
            Reference to the column this value belongs to
        updated_schema_links : dict[str, str]
            Mapping of question terms to schema items
        filtered_value_links : dict[str, str]
            Mapping of filtered value links
        symbol_table : dict[str, str]
            Mapping from schema items to their symbols

        Returns
        -------
        str
            Question with value replaced and evidence annotation added
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
        Add table references for columns that are used in the schema links.

        Parameters
        ----------
        schema_links : dict[str, str]
            All schema links from question terms to schema items
        filtered_schema_links : dict[str, str]
            Filtered subset of schema links

        Returns
        -------
        dict[str, str]
            Updated schema links with table references added
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
                    assert len(items) == 1
                    table_name = schema_item.split(":")[1]
                    if table_name in tables:
                        updated_schema_links[question_term] = schema_item
        return updated_schema_links

    async def _process_row(
        self, row: "AddSymbolicSchema.Model"
    ) -> "AddSymbolicQuestion.Model":
        self.vid: int = 1
        self.value_dict: dict[str, str] = {}
        filtered_schema_links = row.filtered_schema_links
        schema_links = row.schema_links
        question = row.question
        symbol_table = row.symbolic.to_symbol
        updated_schema_links = self.add_tables_of_columns(
            schema_links, filtered_schema_links
        )
        masked_terms = []

        symbolic_question = question
        masked = 0

        value_links = row.value_links
        filtered_value_links = row.filtered_value_links

        if isinstance(value_links, (list, str)):
            logger.error(f"Invalid value links: {value_links}")
            value_links = {}

        if isinstance(filtered_value_links, (list, str)):
            logger.error(f"Invalid value links: {filtered_value_links}")
            filtered_value_links = {}

        sorted_value_terms = sorted(value_links.keys(), key=len, reverse=True)
        sorted_schema_terms = sorted(updated_schema_links.keys(), key=len, reverse=True)

        for question_term in sorted_value_terms:
            schema_item = value_links[question_term]
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
                logger.warning(
                    f"[yellow]⚠  Mask failed[/yellow] [dim]{question_term}[/dim] → {e}"
                )

        for question_term in sorted_schema_terms:
            schema_items = updated_schema_links[question_term]
            try:
                symbolic_question = self.symbolize_term(
                    symbolic_question, question_term, schema_items, symbol_table
                )
                masked_terms.append(question_term)
                masked += 1
            except Exception as e:
                logger.warning(
                    f"[yellow]⚠  Mask failed[/yellow] [dim]{question_term}[/dim] → {e}"
                )

        symbolic = SymbolicQuestion(
            **row.symbolic.dict(),
            question=symbolic_question,
            to_value=self.value_dict,
            masked=masked,
            masked_terms=masked_terms,
        )

        return self.Model(**row.dict(exclude={"symbolic"}), symbolic=symbolic)
