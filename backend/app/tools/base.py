from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    name: str

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
