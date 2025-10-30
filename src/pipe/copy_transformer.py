"""Transformers for copying and modifying data fields."""

import json
import os
from typing import Any

from src.pipe.processor.list_transformer import JsonListTransformer


class CopyTransformer(JsonListTransformer):
    """
    Transformer for copying values from one field to another.

    Parameters
    ----------
    src : str
        Source field path.
    dst : str
        Destination field path.
    """

    def __init__(self, src: str, dst: str) -> None:
        super().__init__(force=True)
        self.src = src
        self.dst = dst

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        src_value = self.get_prop(row, self.src)
        self.set_prop(row, self.dst, src_value)
        return row


class DeleteProp(JsonListTransformer):
    """
    Transformer for deleting a property from data rows.

    Parameters
    ----------
    prop : str
        Property name to delete.
    """

    def __init__(self, prop: str) -> None:
        super().__init__(force=True)
        self.prop = prop

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        del row[self.prop]
        return row


class CopyFromPrevStage(JsonListTransformer):
    """
    Transformer for copying values from a previous pipeline stage.

    Parameters
    ----------
    stage : str
        Name of the previous stage to copy from.
    src : str
        Source field to copy.
    """

    def __init__(self, stage: str, src: str) -> None:
        super().__init__(force=True)
        self.stage = stage
        self.src = src

    def get_prev_stage(self, input_file: str) -> list[dict[str, Any]]:
        """
        Load data from previous pipeline stage.

        Parameters
        ----------
        input_file : str
            Path to current input file

        Returns
        -------
        list
            Data from previous stage
        """
        dir_path = os.path.dirname(input_file)
        prev_stage_file_path = os.path.join(dir_path, f"{self.stage}.json")
        return super()._get_input_data(prev_stage_file_path)

    async def run(self, input_file: str) -> str:
        """
        Run the transformer and copy values from previous stage.

        Parameters
        ----------
        input_file : str
            Path to input file

        Returns
        -------
        str
            Path to output file
        """
        output_file = await super().run(input_file)

        with open(output_file) as f:
            data = json.load(f)

        prev_stage = self.get_prev_stage(input_file)

        updated_rows = []
        for i, row in enumerate(data):
            row[self.src] = prev_stage[i][self.src]
            updated_rows.append(row)

        with open(output_file, "w") as f:
            f.write(json.dumps(updated_rows, indent=4))
        return output_file

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        return row


class AddGoldValues(JsonListTransformer):
    """
    Transformer for extracting gold value links as a list.

    Extracts keys from gold_value_links and stores them in a 'values' field.
    """

    def __init__(self) -> None:
        super().__init__(force=True)

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        value_links = row["gold_value_links"]
        keys = list(value_links.keys())
        row["values"] = keys
        return row
