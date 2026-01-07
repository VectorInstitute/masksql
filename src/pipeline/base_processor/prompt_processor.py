"""Base base_processor for LLM-based value detection."""

import uuid
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Any, Generic, Type, TypeVar

from loguru import logger

from src.config import OpenAIConfig
from src.pipeline.base_processor.list_processor import JsonListProcessor
from src.pipeline.init_data import InitData
from src.utils.llm_util import send_prompt
from src.utils.timer import Timer


T = TypeVar("T", bound=InitData.Model)
U = TypeVar("U", bound=InitData.Model)


class PromptProcessor(JsonListProcessor[T, U], ABC, Generic[T, U]):
    """
    Base base_processor for LLM-based prompts processing.

    This abstract class provides common functionality for processors that use
    LLM prompts to transform data rows, including prompts logging and statistics
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
        cls: Type[U],
        openai_config: OpenAIConfig,
        model: str,
        force: bool = False,
        include_stats: bool = True,
    ) -> None:
        super().__init__(cls)
        self.openai_config = openai_config
        self.model = model
        self.include_stats = include_stats
        self.prompt_logger = logger.bind(type="prompt", name=self.name)

    async def _prompt_llm(self, row: T, prompt: str) -> tuple[Any, str]:
        prompt_logger = self.prompt_logger.bind(prompt_id=uuid.uuid4())
        try:
            prompt_logger.bind(is_req=True).debug(prompt)
            res, toks = await send_prompt(prompt, self.openai_config, model=self.model)
            prompt_logger.bind(is_req=False).debug(res)
        except JSONDecodeError as e:
            logger.error(f"Sending prompts failed: {e}")
            return "", "0"
        except Exception as e:
            logger.error(f"Sending prompts failed: {e}")
            raise e
        processed_res = self._process_output(row, res)
        return processed_res, toks

    @abstractmethod
    def _process_output(self, row: T, output: str) -> Any:
        pass

    @abstractmethod
    def _get_prompt(self, row: T) -> str:
        pass

    @abstractmethod
    def _get_result_data(self, row: T, llm_output: Any) -> U:
        pass

    async def _process_row(self, row: T) -> U:
        prompt = self._get_prompt(row)
        timer = Timer.start()
        res, toks = await self._prompt_llm(row, prompt)
        result_data = self._get_result_data(row, res)
        if self.include_stats:
            latency = timer.lap()
            new_latency = row.total_latency + latency
            new_toks = row.total_toks + int(toks)
            result_data = result_data.model_copy(
                update={"total_latency": new_latency, "total_toks": new_toks}
            )
        return result_data
