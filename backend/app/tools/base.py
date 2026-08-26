from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any


class Tool(ABC):
    name: str

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class ToolRegistry:
    def __init__(self, tools: Iterable[Tool] = ()) -> None:
        self._tools: dict[str, Tool] = {}
        for tool in tools:
            self.register(tool)

    def register(self, tool: Tool) -> None:
        if not tool.name.strip():
            raise ValueError("Tool name must not be empty")
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name!r} is already registered")
        self._tools[tool.name] = tool

    def names(self) -> tuple[str, ...]:
        return tuple(self._tools)

    def scope(self, allowed_names: Iterable[str]) -> "ScopedToolRegistry":
        allowed = tuple(allowed_names)
        missing = [name for name in allowed if name not in self._tools]
        if missing:
            raise LookupError(f"Tools were not found: {', '.join(missing)}")
        return ScopedToolRegistry({name: self._tools[name] for name in allowed})


class ScopedToolRegistry:
    def __init__(self, tools: dict[str, Tool]) -> None:
        self._tools = tools

    def names(self) -> tuple[str, ...]:
        return tuple(self._tools)

    def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        tool = self._tools.get(name)
        if tool is None:
            raise PermissionError(f"Tool {name!r} is not available in this scope")
        return tool.execute(arguments)
