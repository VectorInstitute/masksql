"""Tests for the Pipeline class functionality.

This module tests the pipeline processing functionality by creating a simple
pipeline with two processors and verifying the expected output.
"""

import os
import shutil
from pathlib import Path

import pytest

from src.models.base_object import BaseObject
from src.pipe.pipeline import Pipeline
from src.pipe.processor.list_processor import JsonListProcessor, T, U
from src.utils.json_io import read_json, write_json_raw


TEST_DIR = Path(__file__).parent
TEST_DATA_DIR = os.path.join(TEST_DIR, "test_data")


class DataModel(BaseObject):
    """Simple data model for testing pipeline processing.

    Attributes
    ----------
    a : int
        An integer value to be processed by the pipeline.
    """

    a: int


DataModelList = list[DataModel]


class Plus2(JsonListProcessor[DataModel, DataModel]):
    """Processor that adds 2 to the 'a' attribute of each DataModel.

    This processor is used in the pipeline test to demonstrate
    sequential processing of data.
    """

    def __init__(self):
        super().__init__(DataModel)

    async def _process_row(self, row: T) -> U:
        row.a += 2
        return row


class Times5(JsonListProcessor[DataModel, DataModel]):
    """Processor that multiplies the 'a' attribute of each DataModel by 5.

    This processor is used in the pipeline test to demonstrate
    sequential processing of data after the Plus2 processor.
    """

    def __init__(self):
        super().__init__(DataModel)

    async def _process_row(self, row: T) -> U:
        row.a *= 5
        return row


@pytest.mark.asyncio
async def test_pipeline():
    cache_dir = os.path.join(TEST_DATA_DIR, "cache", "pipeline_test")
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)

    pipeline = Pipeline(
        "test_pipeline", os.path.join(TEST_DIR, "cache"), [Plus2(), Times5()]
    )
    write_json_raw("test.json", [{"idx": "i1", "a": 1}])
    data = read_json("test.json", DataModel)

    result = await pipeline.run(data)

    assert result[0].a == 15
