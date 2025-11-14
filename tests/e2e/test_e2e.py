"""End-to-end tests for MaskSQL pipeline using VCR to record HTTP requests."""

import os
from pathlib import Path

import vcr

from src.config import MaskSqlConfig


os.environ["START"] = "0"
os.environ["LIMIT"] = "1"
os.environ["FORCE"] = "1"
os.environ["OPENAI_API_KEY"] = ""

import pytest
from dotenv import load_dotenv

from main import create_pipeline_stages
from src.pipe.pipeline import Pipeline
from src.utils.json_io import read_json
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
        data_dir=TEST_DATA_DIR,
        resd=True,
        policy="full",
        slm="qwen/qwen-2.5-7b-instruct",
        llm="openai/gpt-4.1",
    )
    pipeline_stages = create_pipeline_stages(conf)
    pipeline = Pipeline(pipeline_stages)
    result_file, _, _ = await pipeline.run(conf.input_path)
    result_data = read_json(result_file)
    assert result_data[0]["eval"]["acc"] == 1
