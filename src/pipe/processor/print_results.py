"""Results printing processor."""

from src.pipe.attack import AddInferenceAttack
from src.pipe.processor.list_processor import JsonListProcessor


def print_color(text: str, color: str = "green") -> None:
    """
    Print text with ANSI color codes.

    Parameters
    ----------
    text : str
        Text to print
    color : str, optional
        Color name (red, green, blue), default green
    """
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "blue": "\033[94m",
    }
    reset = "\033[0m"
    color_code = colors.get(color.lower(), "")
    print(f"{color_code}{text}{reset}")


class PrintResults(
    JsonListProcessor[AddInferenceAttack.Model, AddInferenceAttack.Model]
):
    """Print execution accuracy and privacy metrics."""

    def __init__(self) -> None:
        super().__init__(AddInferenceAttack.Model)
        self.score = 0.0
        self.pre_score = 0
        self.total = 0
        self.total_toks = 0
        self.total_gold_masks = 0
        self.masks = 0
        self.leakage = 0
        self.total_masks = 0

    def _post_run(self) -> None:
        print(f"PreScore: {self.pre_score}/{self.total}")
        print(f"Accuracy: {self.score}/{self.total}")
        print(f"Masked: {self.masks}/{self.total_gold_masks}")
        print(f"Leak: {self.leakage}/{self.total_masks}")
        # print(f"Toks: {self.total_toks}/{self.total}")

    async def _process_row(
        self, row: AddInferenceAttack.Model
    ) -> AddInferenceAttack.Model:
        self.total += 1
        # self.total_toks += row['total_toks']
        exec_acc = row.eval.acc
        if exec_acc == 0:
            print(f"#{row.idx}")
            print(f"Q: {row.question}")

        self.score += exec_acc
        # pre_score = row['pre_eval']['acc']
        # self.pre_score += pre_score

        # Uncomment and modify as needed for additional functionality
        # masked_terms = row["symbolic"]["masked_terms"]
        # gold_links = row["gold_links"]
        # masks = 0
        # for q_term, _schema_item in gold_links.items():
        #     for p_term in masked_terms:
        #         if similar(p_term, q_term):
        #             masks += 1
        #
        # self.total_masks += len(masked_terms)
        # self.masks += masks
        # self.total_gold_masks += len(gold_links.keys())
        #
        # if "attack" in row:
        #     guess = row["attack"]
        #     leakage = 0
        #     leak_terms = []
        #     for term in masked_terms:
        #         if term.lower() in guess.lower():
        #             leakage += 1
        #             leak_terms.append(term)
        #     self.leakage += leakage

        # Additional debugging output can be added here if needed
        # print(f"MASKED: {row['symbolic']['masked']}")
        # if "symbolic" in row:
        #     print(f"Masked Question: {row['symbolic']['question']}")
        # print_color(f"Question: {row['question']}", "green")
        # print_color(f"Gold: {row['query']}", "green")
        # print(f"Pred: {row['pred_sql']}")
        # print(f"Conc: {row['concrete_sql']}")
        # print(f"Masked SQL: {row['symbolic']['sql']}")
        # print(f"Schema Items: {row['schema_items']}")
        # print(f"Schema Links: {row['schema_links']}")
        # print(f"Filtered Schema Links: {row['filtered_schema_links']}")
        # print(f"Value Links: {row['value_links']}")
        # print(f"Filtered Value Links: {row['filtered_value_links']}")
        # print("\n")
        # print("RESULTS: ")
        # if row['eval']['acc'] == 0:
        #     print_color(f"GOLD RES: {row['eval']['gold']}", "green")
        #     print_color(f"PRED RES: {row['eval']['pred']}", "red")
        #     print_color(f"PRED ERR: {row['eval']['pred_err']}", "red")
        # print("\n")
        # print("#" * 10)
        # print(f"Schema:\n {row['schema']}")
        # print("#" * 10)
        # print("#" * 10)
        # print(f"Symbolic Schema:\n {row['symbolic']['schema']}")
        # print("#" * 10)

        return row
