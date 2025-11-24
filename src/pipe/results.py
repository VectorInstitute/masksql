"""Results management utilities."""

from typing import Any

import pandas as pd
from rich.table import Table

from src.pipe.attack import AddInferenceAttack
from src.pipe.processor.list_processor import JsonListProcessor
from src.utils.logging import console


class Results(JsonListProcessor[AddInferenceAttack.Model, AddInferenceAttack.Model]):
    """Collect and aggregate evaluation results."""

    def __init__(self) -> None:
        super().__init__(AddInferenceAttack.Model, force=True)
        self.stat_rows: list[dict[str, Any]] = []
        self.ea = 0
        self.pre_ea = 0
        self.time = 0
        self.toks = 0
        self.count = 0
        self.ri_score = 0
        self.total_leaks = 0
        self.total_masks = 0
        self.a_count = 0
        self.recall_scores: list[float] = []

    async def _process_row(
        self, row: AddInferenceAttack.Model
    ) -> AddInferenceAttack.Model:
        stat = {}
        # if "eval" in row:
        ea = row.eval.acc
        # ea = row["eval"]["acc"]
        stat["EA"] = ea
        # if "total_latency" in row:
        stat["Tokens"] = row.total_toks
        stat["Latency"] = row.total_latency
        # if "pre_eval" in row:
        stat["pre_acc"] = row.pre_eval.acc
        self.count += 1
        self.stat_rows.append(stat)
        # if "attack" in row and "annotated_links" in row:
        masked_terms = row.symbolic.masked_terms
        attack = row.attack
        a_links = row.annotated_links

        ri_terms = 0
        num_masks = len(masked_terms)
        for term in masked_terms:
            if term.lower() in attack.lower():
                ri_terms += 1
        ris = ri_terms / num_masks if num_masks > 0 else 0
        stat["ris"] = 1 - ris

        mask_covering = 0
        a_masks = len(a_links)
        for a_term, _a_item in a_links.items():
            a_term_lower = a_term.lower()
            for term in masked_terms:
                term_lower = term.lower()
                if a_term_lower in term_lower:
                    mask_covering += 1
                    break
        if a_masks == 0:
            mcs: float = 1
        else:
            mcs = mask_covering / a_masks
            self.recall_scores.append(mcs)
        stat["mcs"] = mcs
        stat["a_masks"] = a_masks

        return row

    def _post_run(self) -> None:
        df = pd.DataFrame(self.stat_rows)
        stats = df.mean()

        # Create results table
        console.print("\n")
        results_table = Table(
            title="[bold cyan]Evaluation Results[/bold cyan]",
            show_header=True,
            header_style="bold magenta",
            border_style="green",
        )
        results_table.add_column("Metric", style="cyan", width=20)
        results_table.add_column("Value", style="yellow", justify="right", width=15)

        # Add each metric to the table
        for metric, value in stats.items():
            formatted_value = f"{value:.6f}" if isinstance(value, float) else str(value)
            results_table.add_row(str(metric), formatted_value)

        console.print(results_table)
        console.print(f"\n[dim]Total samples processed: {self.count}[/dim]\n")
