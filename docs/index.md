# MaskSQL

----------------------------------------------------------------------------------------

[![code checks](https://github.com/VectorInstitute/masksql/actions/workflows/code_checks.yml/badge.svg)](https://github.com/VectorInstitute/masksql/actions/workflows/code_checks.yml)
[![unit tests](https://github.com/VectorInstitute/masksql/actions/workflows/unit_tests.yml/badge.svg)](https://github.com/VectorInstitute/masksql/actions/workflows/unit_tests.yml)
[![docs](https://github.com/VectorInstitute/masksql/actions/workflows/docs.yml/badge.svg)](https://github.com/VectorInstitute/masksql/actions/workflows/docs.yml)
[![codecov](https://codecov.io/github/VectorInstitute/masksql/graph/badge.svg?token=83MYFZ3UPA)](https://codecov.io/github/VectorInstitute/masksql)
![GitHub License](https://img.shields.io/github/license/VectorInstitute/masksql)

MaskSQL is a privacy-preserving framework for LLM-based text-to-SQL that uses schema masking and progressive unmasking to protect sensitive database information while maintaining high query accuracy.

## Table of Contents

- [Installation](#installation-and-setup-instructions)
- [Running MaskSQL](#running-masksql)
- [Documentation](#documentation)
- [Citation](#citation)

## Installation and Setup Instructions

### Prerequisites

- Python 3.11
- [uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) package manager

### Setup

Install dependencies and activate the virtual environment:

```sh
uv sync --dev
source .venv/bin/activate
```

### Download Dataset

Download and extract the dataset:

```sh
wget -O data.zip "https://www.dropbox.com/scl/fi/vtraf79vfi1x105veaflk/data.zip?rlkey=7yq6d46aer6h45pdihrc9rht1&st=zdac3rqx&dl=0"
unzip data.zip
```

Expected directory structure:

```
data/
├── databases/
├── 1_input.json
└── ...
```

### Configure Environment

Create a `.env` file from the template:

```sh
cp .env.example .env
```

**Required:**
- `OPENAI_API_KEY`: Your [OpenRouter](https://openrouter.ai/) API key

**Optional:**
- `LIMIT`: Number of dataset entries to process (e.g., `LIMIT=10`)
- `START`: Starting index in the dataset (default: 0)
- `LOG_LEVEL`: Logging verbosity (INFO, DEBUG, etc.)

### Download RESDSQL Models

MaskSQL uses RESDSQL for schema filtering, which requires pre-trained models:

```sh
# Download and extract models (if not already in data.zip)
cd resdsql
unzip -o ../data/resdsql/text2sql-t5-base.zip -d models
unzip -o ../data/resdsql/text2sql_schema_item_classifier.zip -d models
cd ..
```

The models will be extracted to `models/text2sql_schema_item_classifier/` and `models/text2sql-t5-base/`.

## Running MaskSQL

### Configuration

MaskSQL uses `configs/conf.yaml` by default. You can specify a different config file using the `--config` option:

```sh
python3 main.py --config path/to/config.yaml
```

**Key configuration options:**
- `data_dir`: Directory containing datasets and databases
- `resd`: Use RESDSQL for schema ranking (default: true)
- `policy`: Evaluation policy ("full", "partial", etc.)
- `slm`: Small language model for entity detection and linking
- `llm`: Large language model for SQL generation

### Run the Pipeline

Execute the MaskSQL pipeline:

```sh
python3 main.py
```

The pipeline will automatically:
1. Run RESDSQL for schema filtering (if `data/resd_output.json` doesn't exist)
2. Execute masking, SQL generation, and evaluation stages
3. Generate results in numbered output files (`2_LimitJson.json`, `3_RunResdsql.json`, etc.)

**Optional flags:**
- `--clean`: Remove intermediate files before running
- `--config`: Specify a custom config file

Example:

```sh
# Clean previous outputs and rerun
python3 main.py --clean

# Use custom config
python3 main.py --config configs/custom.yaml
```

**Note:** RESDSQL schema filtering runs only once and caches results in `data/resd_output.json`. To force regeneration, delete this file or set `FORCE=1` in your environment.

## Documentation

- [MaskSQL Framework](FRAMEWORK.md) - Overview of the framework architecture
- [Pipeline Stages](STAGES.md) - Detailed explanation of each pipeline stage

## Citation

If you use MaskSQL in your research, please cite our paper:

```bibtex
@article{abedini2025masksql,
  title={MaskSQL: Safeguarding Privacy for LLM-Based Text-to-SQL via Abstraction},
  author={Abedini, Sepideh and Mohapatra, Shubhankar and Emerson, DB and Shafieinejad, Masoumeh and Cresswell, Jesse C and He, Xi},
  journal={arXiv preprint arXiv:2509.23459},
  year={2025}
}
```

**Paper:** [https://arxiv.org/abs/2509.23459](https://arxiv.org/abs/2509.23459)
