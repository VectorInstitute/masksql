"""Question masking utilities."""

import asyncio
import json
import re

from RESDSQL.llm_util import send_prompt


DATA_DIR = "data"

PROMPT = """
You are a database expert. Given a natural language question and database schema information,
mask all sensitive table and column names with symbolic names like [T1], [C1], [V1], etc.

Question: {question}
Schema Items: {sitems}
Schema Links: {slinks}

Return the masked question in a code block.
"""


async def gen():
    """Generate masked questions from RESDSQL test data."""
    with open("resdsql_test.json") as f:
        data = json.load(f)

    masked_data = []
    with (
        open("out/mask_prompts.txt", "w") as prompts_file,
        open("out/mask_res.txt", "w") as responses_file,
    ):
        for _i, row in enumerate(data):
            slinks = row["schema_links"]
            sitems = row["tc_original"]
            question = row["question"]
            prompt = PROMPT.format(question=question, sitems=sitems, slinks=slinks)
            res = await send_prompt(prompt)
            masked = re.findall(r"```([\s\S]*?)```", res)
            final_answer = masked[0]
            final_answer = final_answer.strip()
            prompts_file.write(prompt + "\n")
            responses_file.write(res + "\n")
            row["masked_question"] = final_answer
            masked_data.append(row)

    with open("out/masked_input.json", "w") as f:
        f.write(json.dumps(masked_data, indent=4))


async def main():
    """Execute masking generation."""
    await gen()


if __name__ == "__main__":
    asyncio.run(main())
