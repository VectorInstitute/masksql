"""Base processor for LLM-based value detection."""

import os
from abc import abstractmethod
from json import JSONDecodeError
from typing import Any

from loguru import logger

from src.pipe.llm_util import send_prompt
from src.pipe.processor.list_transformer import JsonListTransformer
from src.pipe.utils import Timer


class PromptProcessor(JsonListTransformer):
    """
    Base processor for LLM-based prompt processing.

    This abstract class provides common functionality for processors that use
    LLM prompts to transform data rows, including prompt logging and statistics
    tracking.

    Parameters
    ----------
    prop_name : str
        Name of the property to store the processed output in
    model : str, optional
        LLM model identifier, defaults to DEFAULT_MODEL environment variable
    force : bool, optional
        Whether to force reprocessing, by default False
    include_stats : bool, optional
        Whether to track latency and token statistics, by default True
    """

    def __init__(
        self,
        prop_name: str,
        model: str = os.environ["DEFAULT_MODEL"],
        force: bool = False,
        include_stats: bool = True,
    ) -> None:
        super().__init__(force)
        self.model = model
        self.prop_name = prop_name
        self.prompt_file = "/dev/null"
        self.response_file = "/dev/null"
        self.include_stats = include_stats

    async def _prompt_llm(self, row: dict[str, Any], prompt: str) -> tuple[Any, str]:
        try:
            res, toks = await send_prompt(prompt, model=self.model)
        except JSONDecodeError as e:
            logger.error(f"Sending prompt failed: {e}")
            return "", "0"
        except Exception as e:
            logger.error(f"Sending prompt failed: {e}")
            raise e
        processed_res = self._process_output(row, res)
        return processed_res, toks

    @abstractmethod
    def _process_output(self, row: dict[str, Any], output: str) -> Any:
        pass

    @abstractmethod
    def _get_prompt(self, row: dict[str, Any]) -> str:
        pass

    async def _process_row(self, row: dict[str, Any]) -> dict[str, Any]:
        prompt = self._get_prompt(row)
        with open(self.prompt_file, "a") as f:
            f.write(f"######################\n {prompt}\n")
        timer = Timer.start()
        res, toks = await self._prompt_llm(row, prompt)
        with open(self.response_file, "a") as f:
            f.write(f"######################\n {res}\n")

        if self.include_stats:
            if "total_latency" not in row:
                row["total_latency"] = 0
            latency = timer.lap()
            row["total_latency"] += latency

            if "total_toks" not in row:
                row["total_toks"] = 0
            row["total_toks"] += int(toks)

        if self.prop_name in row and not isinstance(row[self.prop_name], str):
            row[self.prop_name].update(res)
        else:
            row[self.prop_name] = res
        return row

    async def run(self, input_file: str) -> str:
        """
        Run the processor and log prompts/responses.

        Parameters
        ----------
        input_file : str
            Path to input JSON file

        Returns
        -------
        str
            Path to output file
        """
        os.makedirs("logs", exist_ok=True)
        self.prompt_file = f"logs/{self.name}.prompt.txt"
        self.response_file = f"logs/{self.name}.response.txt"
        open(self.prompt_file, "w").close()
        open(self.response_file, "w").close()
        return await super().run(input_file)
