"""Property printing utilities."""

from typing import Any

from src.pipe.processor.list_processor import JsonListProcessor


class PrintProps(JsonListProcessor):
    """
    Print specific properties from each row.

    Parameters
    ----------
    props : list[str]
        List of property paths to print
    """

    def __init__(self, props: list[str]) -> None:
        super().__init__()
        self.props = props

    async def _process_row(self, row: Any) -> Any:
        # if row['pre_eval']['acc'] == 0 and row['eval']['acc'] == 1:
        print("Entry: " + "-" * 20)
        for prop in self.props:
            print(f"{prop}:\n {self.get_prop(row, prop)}")
        return row
