# MaskSQL

# Table of Contents

- [Installation](#installation-and-setup-instruction)
- [Run MaskSQL](#run-masksql)
- [MaskSql Framework](Framework.md)
- [MaskSQL Pipeline Stages](Stages.md)

## Installation and Setup Instructions

### System Requirements

The development environment (tested on python 3.11) can be set up using
[uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation). Hence, make sure it is
installed and then run:

```sh
uv sync --dev
source .venv/bin/activate
```

### Download Dataset

Download [this zip file](https://www.dropbox.com/scl/fi/vtraf79vfi1x105veaflk/data.zip?rlkey=7yq6d46aer6h45pdihrc9rht1&st=zdac3rqx&dl=0")
and extract it to the `data` directory:

```sh
wget -O data.zip "https://www.dropbox.com/scl/fi/vtraf79vfi1x105veaflk/data.zip?rlkey=7yq6d46aer6h45pdihrc9rht1&st=zdac3rqx&dl=0"
unzip data.zip
```

Your data directory should look like this:

```sh
data/
├── databases/
├── 1_input.json
.
.
.
```

### Set Environment Variables

```sh
cp .env.example .env
```

The only required variable to set is `OPENAI_API_KEY`.
By default, we are using [OpenRouter](https://openrouter.ai/), so you need to set the api key
for OpenRouter.

You may also change the `LIMIT` variable to modify the number of entries to be read from the dataset.
`START` specifies the start index for reading from the dataset.

For instance, set `LIMIT=10` to run the pipeline for a dataset of size 10.

`SLM_MODEL` and `LLM_MODEL` specify the ID of small/large language models to be used in the pipeline.
These IDs should be set based on the LM provider being used.
For instance, since we are using OpenRouter, model identifiers should be specified accordingly, e.g.,
`openai/gpt-4.1` for GPT-4.1.

### Run RESDSQL
To run MaskSQL, first we need to filter the schema items
using RESDSQL.
Follow these [instructions](./Resd.md) to run the RESDSQL
and generated the file needed for the MaskSQL pipeline.
Then, you need to run the MaskSQL with the `--resd` option.

### Run MaskSQL

Then you can run MaskSQL pipline as follows:
```sh
python3 main.py --resd
```

MaskSQL saves the intermediate results to files for later user.
So, in order to run the pipeline from scratch you need to clean the data directory:
```sh
./clean.sh data
```
