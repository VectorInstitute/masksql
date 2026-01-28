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

### Docker Installation

Setup the env variables:
```shell
cp .env.example .env
```
> Fill in the required variables

Run the MaskSQL using the published Docker image:
```shell
docker compose run --rm masksql python main.py
```
#### Build the Docker image

Build the Docker image locally:
```shell
docker compose -f docker-compose.local.yaml build
```

#### Interactive shell

You can run the MaskSQL container and then have a shell access to
the container:
```shell
docker compose up -d
# Or
docker compose -f docker-compose.local.yaml up -d
```
After the container started successfully you can have a shell access:

```shell
docker compose exec -it masksql bash
# Or
docker compose -f docker-compose.local.yaml exec -it masksql bash
```

### Native Installation

#### Requirements

- Python 3.11
- [uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) package manager

#### Setup Environment

Install dependencies and activate the virtual environment:

```sh
uv sync --dev
source .venv/bin/activate
```

#### Download Dataset

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

#### Configure Environment

Create a `.env` file from the template:

```sh
cp .env.example .env
```

**Required:**
- `OPENAI_API_KEY`: Your [OpenRouter](https://openrouter.ai/) API key

**Optional:**
- `LIMIT`: Number of dataset entries to process (e.g., `LIMIT=10`)
- `START`: Starting index in the dataset (default: 0)

## Running MaskSQL

### Configuration

To configure the MaskSQL, uses the `configs/conf.yaml` file by default.
You can pass in arbitrary config files using the `--config` option of
the CLI interface.


### 1. Run RESDSQL (Schema Filtering)

MaskSQL requires RESDSQL for initial schema filtering. Follow the [RESDSQL setup instructions](./Resd.md) to generate the required files.

### 2. Run the Pipeline

Execute the MaskSQL pipeline:

```sh
python3 main.py
```

or to clean previous outputs and rerun:

```sh
python3 main.py --clean
```

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
