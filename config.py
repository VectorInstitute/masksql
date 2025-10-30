"""Configuration management for MaskSQL.

This module defines the configuration dataclass used throughout the MaskSQL
project for managing paths, models, and runtime settings.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


# Load environment variables at module import time
load_dotenv()


@dataclass
class MaskSqlConfig:
    """Configuration settings for MaskSQL execution.

    Attributes
    ----------
    data_dir : str
        Base directory for data files.
    resd : bool
        Whether to use RESD mode.
    policy : str
        Policy configuration for execution.
    slm : str
        Small language model identifier (from SLM_MODEL env var).
    llm : str
        Large language model identifier (from LLM_MODEL env var).
    """

    data_dir: str
    resd: bool
    policy: str
    slm: str = os.environ["SLM_MODEL"]
    llm: str = os.environ["LLM_MODEL"]
    __input_file: str = "1_input.json"
    __db_dir: str = "databases"
    __tables_file: str = "tables.json"
    __resd_file: str = "resd_output.json"

    def get_abs_path(self, rel_path: str) -> str:
        """Convert a relative path to an absolute path within the data directory.

        Parameters
        ----------
        rel_path : str
            Relative path to convert.

        Returns
        -------
        str
            Absolute path within the data directory.
        """
        return os.path.join(self.data_dir, rel_path)

    @property
    def input_path(self) -> str:
        """Get the absolute path to the input JSON file."""
        return self.get_abs_path(self.__input_file)

    @property
    def tables_path(self) -> str:
        """Get the absolute path to the tables JSON file."""
        return self.get_abs_path(self.__tables_file)

    @property
    def resd_path(self) -> str:
        """Get the absolute path to the RESD output JSON file."""
        return self.get_abs_path(self.__resd_file)

    @property
    def db_path(self) -> str:
        """Get the absolute path to the databases directory."""
        return self.get_abs_path(self.__db_dir)
