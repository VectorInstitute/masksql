"""Privacy score calculation processor."""

from typing import Any

import spacy

from src.pipe.processor.printer import DataPrinter


nlp = spacy.load("en_core_web_sm")


def tokenize(text: str) -> list[str]:
    """
    Tokenize text using spaCy.

    Parameters
    ----------
    text : str
        Text to tokenize

    Returns
    -------
    list
        List of token strings without stop words or punctuation
    """
    doc = nlp(text)
    return [token.text for token in doc if not token.is_stop and not token.is_punct]


class PrivacyScore(DataPrinter):
    """Calculate privacy leakage scores from inference attacks."""

    def __init__(self) -> None:
        super().__init__()
        self.score = 0
        self.leaked = 0
        self.total_masked = 0
        self.count = 0

    def _post_run(self) -> None:
        print(f"Leakage: {self.score / self.count}")
        print(f"Leaks: {self.leaked}/{self.total_masked}")

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        schema_links = row["filtered_schema_links"]
        value_links = row["filtered_value_links"]
        guess = row["attack"]
        masked_terms = list(value_links.keys()) + list((schema_links.keys()))
        leaked = 0
        for term in masked_terms:
            if term.lower() in guess.lower():
                leaked += 1

        total_masks = len(masked_terms)
        self.count += 1
        self.leaked += leaked
        # self.score += leaked / total_masks
        self.total_masked += total_masks
        # self.leakage += float(leakage_score / len(masked_terms))

        # privacy_cover = 0
        # gold_terms = list(gold_links.keys())
        # for term in gold_terms:
        #     if term.lower() in guess.lower():
        #         privacy_cover += 1

        # self.cover += privacy_cover / len(gold_terms)
        # self.total += 1
        return row
        # print("-" * 20)
        # print(f"Leakage: {leakage_score}/{len(masked_terms)}")
        # print(f"Cover: {privacy_cover}/{len(gold_terms)}")
        # print("Orig:  ", question)
        # if "raw" in row['symbolic']:
        #     symbolic_question = row['symbolic']['raw']
        # else:
        #     symbolic_question = row['symbolic']['question']
        # print("Masked:", symbolic_question)
        # print("Attack:", guess)
        # print("Values  :", value_links.keys())
        # print("Schemas  :", schema_links.keys())
        # print("Question Toks:", tokenize(question))
        # print("Attack Toks:", tokenize(guess))
        # print("Gold Links:", gold_links)
        # print("-" * 20)
        # return row
