from typing import Callable, Dict, Any


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._descriptions: Dict[str, str] = {}

    def register(self, name: str, description: str):
        """Decorator để đăng ký tool."""
        def decorator(func: Callable):
            self._tools[name] = func
            self._descriptions[name] = description
            return func
        return decorator

    async def execute(self, name: str, **kwargs) -> Any:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found. Available: {list(self._tools.keys())}")
        return await self._tools[name](**kwargs)

    def get_tool_descriptions(self) -> str:
        """Trả về descriptions dạng string cho planner prompt."""
        lines = []
        for name, desc in self._descriptions.items():
            lines.append(f"- {name}: {desc}")
        return "\n".join(lines)

    @property
    def available_tools(self) -> list[str]:
        return list(self._tools.keys())


tool_registry = ToolRegistry()  # Singleton