"""Property printing utilities."""

from typing import Any

from src.pipeline.base_processor.list_processor import JsonListProcessor


class PrintProps(JsonListProcessor[Any, Any]):
    """
    Print specific properties from each row.

    Parameters
    ----------
    props : list[str]
        List of property paths to print
    """

    def __init__(self, props: list[str]) -> None:
        super().__init__(Any)
        self.props = props

    def get_prop(self, row: Any, prop: str) -> Any:
        """Get a property from a row by path."""
        parts = prop.split(".")
        value = row
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return f"Property {prop} not found"
        return value

    async def _process_row(self, row: Any) -> Any:
        # if row['pre_eval']['acc'] == 0 and row['eval']['acc'] == 1:
        print("Entry: " + "-" * 20)
        for prop in self.props:
            print(f"{prop}:\n {self.get_prop(row, prop)}")
        return row
