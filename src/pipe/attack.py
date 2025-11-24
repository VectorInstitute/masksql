"""Attack processors for testing model robustness."""

from typing import Any

from src.config import OpenAIConfig
from src.pipe.attack_prompts.attack_raw_v1 import ATTACK_PROMPT_RAW_V1
from src.pipe.attack_prompts.attack_v2 import ATTACK_PROMPT_V2
from src.pipe.detect_values_prompts.prompt_processor import PromptProcessor
from src.pipe.exec_acc import CalcExecAcc
from src.pipe.repair_sql import RepairSQL


# TODO[X]: ask to infer all tokens not only in question evidence is being ignored
class AddInferenceAttack(
    PromptProcessor[CalcExecAcc.Model, "AddInferenceAttack.Model"]
):
    """
    Processor for testing inference attacks on masked data.

    Tests model robustness by attempting to infer original values from
    symbolic representations.
    """

    class Model(CalcExecAcc.Model):
        """Data model with attack inference results.

        This model extends CalcExecAcc.Model by adding the results of
        an inference attack attempt on the masked data.

        Attributes
        ----------
            attack: Result of the inference attack attempt
        """

        attack: str

    def __init__(self, openai_config: OpenAIConfig, model: str) -> None:
        super().__init__(self.Model, openai_config, model)

    def _get_result_data(self, row: RepairSQL.Model, llm_output: Any) -> Model:
        return self.Model(attack=llm_output, **row.dict())

    def _process_output(self, row: RepairSQL.Model, output: str) -> str:
        return output

    def _get_prompt(self, row: RepairSQL.Model) -> str:
        symbolic_question = row.symbolic.question
        symbolic_schema = row.symbolic.db_schema
        return ATTACK_PROMPT_V2.format(
            question=symbolic_question, schema=symbolic_schema
        )


class AttackRaw(PromptProcessor):
    """
    Processor for testing attacks on raw symbolic data.

    Tests inference attacks on raw symbolic representations without schema context.
    """

    def _process_output(self, row: dict[str, Any], output: str) -> str:
        return output

    def _get_prompt(self, row: dict[str, Any]) -> str:
        symbolic_raw = row["symbolic"]["raw"]
        return ATTACK_PROMPT_RAW_V1.format(symbolic_raw=symbolic_raw)
