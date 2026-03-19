from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    name: str = "base"

    @abstractmethod
    async def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
