"""Utilities for working with language models."""

import ast
import json
import os
import re
from typing import Tuple

from loguru import logger
from openai import AsyncClient


VLM_ARCH = os.environ.get("VLM_ARCH")
MAX_COMPLETION_TOKENS = os.environ.get("MAX_COMPLETION_TOKENS")

wrappers = {
    "mistral": lambda prompt: f"<s>[INST] {prompt} [/INST]",
    "gemma": lambda prompt: f"<bos><start_of_turn>user\n{prompt}<end_of_turn>\n<start_of_turn>model\n",
    "llama": lambda prompt: f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{prompt}\n<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
}


def wrap_prompt(prompt):
    """
    Wrap prompt with architecture-specific formatting.

    Parameters
    ----------
    prompt : str
        Raw prompt text

    Returns
    -------
    str
        Formatted prompt for specific model architecture
    """
    if VLM_ARCH in wrappers:
        print("Wrapping prompt for", VLM_ARCH)
        return wrappers[VLM_ARCH](prompt)
    return prompt


async def send_prompt(prompt, model=None) -> Tuple[str, str]:
    """
    Send prompt to language model and get response.

    Parameters
    ----------
    prompt : str
        Prompt text to send
    model : str, optional
        Model identifier to use

    Returns
    -------
    Tuple[str, str]
        Response content and token usage
    """
    if model is None:
        model = os.getenv("OPENAI_MODEL")
    if model == "vlm":
        prompt = wrap_prompt(prompt)
    client = AsyncClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        organization=os.getenv("OPENAI_GROUP_ID"),
        project=os.getenv("OPENAI_PROJ_ID"),
        timeout=int(os.getenv("OPENAI_TIMEOUT", "60")),
    )
    logger.debug("#" * 150)
    logger.debug(f"Prompt:\n{prompt}")
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_completion_tokens=MAX_COMPLETION_TOKENS,
    )
    if response.choices is None:
        print(prompt)
        raise Exception(f"LM prompt failed: {response.model_extra}")
    usage = 0
    if response.usage:
        usage = response.usage.total_tokens
    content = response.choices[0].message.content
    logger.debug(f"Response:\n*****\n{content}\n*****\n")
    return content, usage


def extract_json(text: str):
    """
    Extract JSON object from text with code blocks.

    Parameters
    ----------
    text : str
        Text containing JSON object

    Returns
    -------
    dict or None
        Parsed JSON object or None if extraction fails
    """
    try:
        if "```json" in text:
            res = re.findall(r"```json([\s\S]*?)```", text)
            json_res = json.loads(res[0])
        elif "```" in text:
            res = re.findall(r"```([\s\S]*?)```", text)
            json_res = json.loads(res[0])
        else:
            json_res = json.loads(text)
        return json_res
    except Exception as e:
        logger.warning(f"Failed to extract json from: {text}, error={e}")
        return None


def eval_literal(text: str):
    """
    Evaluate text as Python literal.

    Parameters
    ----------
    text : str
        Text containing Python literal

    Returns
    -------
    object or None
        Evaluated Python object or None if evaluation fails
    """
    try:
        return ast.literal_eval(text)
    except Exception as e:
        logger.warning(f"Failed eval literal: {text}, error={e}")
        return None


def extract_object(text: str):
    """
    Extract Python object from text using JSON or literal evaluation.

    Parameters
    ----------
    text : str
        Text containing object representation

    Returns
    -------
    object or None
        Extracted object or None if extraction fails
    """
    obj = extract_json(text)
    if obj is None:
        obj = eval_literal(text)
    if obj is None:
        logger.error(f"Failed to extract object: {text}")
        obj = None
    return obj
