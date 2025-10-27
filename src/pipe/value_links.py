"""Value link data structures and utilities."""

from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.llm_util import extract_object
from src.pipe.value_linking_prompts.v1 import VALUE_LINKING_PROMPT_V1


class LinkValues(PromptProcessor):
    """
    Link detected values in questions to database columns.

    Uses an LLM to determine which database columns each detected value
    in the question should be associated with.
    """

    def _process_output(self, row, output):
        obj = extract_object(output)
        if obj is None:
            return {}
        return obj

    def _get_prompt(self, row):
        schema_items = row["schema_items"]
        question = row["question"]
        values = row["values"]
        # slm_sql = row['slm_sql']
        columns = [x.split(":")[1] for x in schema_items]
        return VALUE_LINKING_PROMPT_V1.format(
            question=question, values=values, columns=columns
        )
