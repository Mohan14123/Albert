import importlib
import logging

from app.plugins.registry import PluginRegistryService

logger = logging.getLogger(__name__)


def load_plugins(registry: PluginRegistryService, plugin_modules: list[str]) -> None:
    for module_name in plugin_modules:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "setup"):
                module.setup(registry)
                logger.info("Loaded plugin module: %s", module_name)
            else:
                logger.warning("Plugin module %s missing 'setup' function", module_name)
        except Exception as e:
            logger.exception("Failed to load plugin module %s: %s", module_name, e)
