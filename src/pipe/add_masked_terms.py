"""Module for identifying and adding masked terms to questions."""

from typing import Any

from src.pipe.attack_prompts.add_masked_terms import ADD_MASKED_TERMS_PROMPT_V1
from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.llm_util import extract_object
from src.utils.logging import logger


class AddMaskedTerms(PromptProcessor):
    """
    Processor for identifying and extracting masked terms from questions.

    This class uses LLM prompts to identify terms in natural language questions
    that should be masked, comparing the original and symbolic representations.
    """

    def _process_output(self, row: dict[str, Any], output: str) -> list[str]:
        output_obj = extract_object(output)
        if output_obj is None:
            return []
        masked_terms = list(output_obj.keys())
        q = row["question"]
        filtered_terms = []
        for m in masked_terms:
            if m.lower() in q.lower():
                filtered_terms.append(m)
            else:
                logger.error(f"{m} not in question: {q}")
        return masked_terms

    def _get_prompt(self, row: dict[str, Any]) -> str:
        question = row["question"]
        symbolic_question = row["symbolic"]["question"]
        return ADD_MASKED_TERMS_PROMPT_V1.format(
            question=question, masked_question=symbolic_question
        )
