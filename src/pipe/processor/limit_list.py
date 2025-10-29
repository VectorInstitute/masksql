"""List length limiting processor."""

import json
import os

from src.pipe.processor.list_transformer import JsonListTransformer


START = int(os.environ.get("START", "0"))
LIMIT = int(os.environ.get("LIMIT", "10"))


class LimitJson(JsonListTransformer):
    """Limit JSON list to subset based on START and LIMIT environment variables."""

    async def run(self, input_file):
        """
        Limit input list to subset.

        Parameters
        ----------
        input_file : str
            Path to input JSON file

        Returns
        -------
        str
            Path to limited output file
        """
        output_file = self.get_output_file(input_file)

        with open(input_file) as f:
            in_data = json.load(f)

        out_data = in_data[START : START + LIMIT]

        out_rows = []
        for row in out_data:
            out_rows.append(row)

        with open(output_file, "w") as f:
            f.write(json.dumps(out_rows, indent=4))
        return output_file

    async def _process_row(self, row):
        return row


class FilterList(JsonListTransformer):
    """
    Filter JSON list based on predicate function.

    Parameters
    ----------
    predicate : callable, optional
        Function to test each row, default returns all rows
    """

    def __init__(self, predicate=lambda r: r):
        super().__init__()
        self.predicate = predicate

    async def run(self, input_file):
        """
        Filter input file based on predicate.

        Parameters
        ----------
        input_file : str
            Path to input JSON file

        Returns
        -------
        str
            Path to filtered output file
        """
        output_file = self.get_output_file(input_file)

        with open(input_file) as f:
            in_data = json.load(f)

        out_data = []
        for row in in_data:
            if self.predicate(row):
                out_data.append(row)

        with open(output_file, "w") as f:
            f.write(json.dumps(out_data, indent=4))
        return output_file

    async def _process_row(self, row):
        return row
