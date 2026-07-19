from typing import Any

from app.plugins.base import BasePlugin


class PluginRegistryService:
    def __init__(self) -> None:
        self._plugins: dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin) -> None:
        self._plugins[plugin.name] = plugin

    def get_plugin(self, name: str) -> BasePlugin | None:
        return self._plugins.get(name)

    def list_plugins(self) -> list[BasePlugin]:
        return list(self._plugins.values())

    async def execute_action(
        self, plugin_name: str, action: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin {plugin_name} not found")
        return await plugin.execute(action, payload)
