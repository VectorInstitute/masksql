"""Transformers for copying and modifying data fields."""

from typing import Type

from src.pipeline.base_processor.list_processor import JsonListProcessor, T, U


class CopyTransformer(JsonListProcessor[T, U]):
    """
    Transformer for copying values from one field to another.

    Parameters
    ----------
    src : str
        Source field path.
    dst : str
        Destination field path.
    """

    def __init__(self, src: str, dst: str, cls: Type[U]) -> None:
        super().__init__(cls, force=True)
        self.src = src
        self.dst = dst

    async def _process_row(self, row: T) -> U:
        data = {**row.dict(), self.dst: getattr(row, self.src)}
        return self.cls.model_validate(data)
