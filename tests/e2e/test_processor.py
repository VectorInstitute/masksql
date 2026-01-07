"""Tests for the JsonListProcessor class functionality.

This module tests the list base_processor functionality, including caching behavior
and proper processing of data items.
"""

import os
import shutil
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from src.data_models.base_object import BaseObject
from src.pipeline.base_processor.list_processor import JsonListProcessor, T, U
from src.utils.json_io import read_json, write_json_raw


class DataModel(BaseObject):
    """Simple data model for testing base_processor functionality.

    Attributes
    ----------
    a : int
        An integer value to be processed by the test base_processor.
    """

    a: int


DataModelList = list[DataModel]


class PlusPlusProcessor(JsonListProcessor[DataModel, DataModel]):
    """Test base_processor that increments the 'a' attribute of each DataModel.

    This base_processor is used to test the JsonListProcessor functionality,
    particularly its caching behavior when processing the same data multiple times.
    """

    def __init__(self):
        super().__init__(DataModel)

    async def _process_row(self, row: T) -> U:
        row.a += 1
        return row


TEST_DIR = Path(__file__).parent
TEST_DATA_DIR = os.path.join(TEST_DIR, "test_data")


@pytest.mark.asyncio
async def test_processor():
    cache_dir = os.path.join(TEST_DATA_DIR, "cache", "processor_test")
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)

    write_json_raw("test.json", [{"idx": "i1", "a": 1}])
    data = read_json("test.json", DataModel)
    p = PlusPlusProcessor()
    p.set_cache_file(cache_dir, 1)
    method = p._process_row
    p._process_row = AsyncMock(wraps=method)

    result = await p.run(data)
    assert result[0].a == 2

    result = await p.run(data)
    assert result[0].a == 2
    # p._process_row_internal.assert_called_once()
