"""Base list processing utilities."""

import json
from abc import ABC, abstractmethod
from typing import Dict

from src.pipe.async_utils import apply_async


class JsonListProcessor(ABC):
    """Base class for JSON list processing operations."""

    @abstractmethod
    async def _process_row(self, row: Dict) -> Dict:
        pass

    def get_prop(self, row, prop):
        """
        Get nested property from row using dot notation.

        Parameters
        ----------
        row : dict
            Data row
        prop : str
            Property path in dot notation

        Returns
        -------
        any
            Property value
        """
        props = prop.split(".")
        d = row
        for p in props:
            d = d[p]
        return d

    def set_prop(self, row, prop, value):
        """
        Set nested property in row using dot notation.

        Parameters
        ----------
        row : dict
            Data row
        prop : str
            Property path in dot notation
        value : any
            Value to set

        Returns
        -------
        dict
            Modified row
        """
        props = prop.split(".")
        d = row
        for p in props[:-1]:
            d = d[p]
        d[props[-1]] = value
        return row

    @property
    def name(self):
        """
        Get processor name.

        Returns
        -------
        str
            Class name of processor
        """
        return self.__class__.__name__

    def _pre_run(self):  # noqa: B027
        """Override to add pre-processing logic before run."""

    def _post_run(self):  # noqa: B027
        """Override to add post-processing logic after run."""

    def _get_input_data(self, input_file):
        with open(input_file) as f:
            return json.load(f)

    async def run(self, input_file):
        """
        Process input file and return output.

        Parameters
        ----------
        input_file : str
            Path to input JSON file

        Returns
        -------
        list
            Processed data rows
        """
        self._pre_run()

        in_data = self._get_input_data(input_file)

        output = await apply_async(self._process_row, in_data, self.name)

        self._post_run()

        return output
