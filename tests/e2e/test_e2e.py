"""End-to-end tests for MaskSQL pipeline using VCR to record HTTP requests."""

import os
from pathlib import Path

import vcr

from src.config import MaskSqlConfig
from src.masksql import MaskSQL


os.environ["START"] = "0"
os.environ["LIMIT"] = "1"
os.environ["OPENAI_API_KEY"] = ""

import pytest
from dotenv import load_dotenv

from src.utils.logging import configure_logging


TEST_DIR = Path(__file__).parent

TEST_DATA_DIR = os.path.join(TEST_DIR, "test_data")

test_vcr = vcr.VCR(
    cassette_library_dir=os.path.join(TEST_DATA_DIR, "cassettes"),
    record_mode="none",
    match_on=["body"],
    record_on_exception=False,
)


@pytest.mark.asyncio
@test_vcr.use_cassette
async def test_e2e():
    load_dotenv()
    configure_logging()
    conf = MaskSqlConfig(
        name="e2e_test",
        cache_dir=os.path.join(TEST_DATA_DIR, "cache"),
        data_dir=TEST_DATA_DIR,
        resd=True,
        policy="full",
        slm="qwen/qwen-2.5-7b-instruct",
        llm="openai/gpt-4.1",
    )
    mask_sql = MaskSQL(conf)
    result_data = await mask_sql.evaluate()
    assert result_data[0].eval.acc == 1
