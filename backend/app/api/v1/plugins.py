from fastapi import APIRouter

from app.core.responses import success_response
from app.plugins.registry import PluginRegistryService

router = APIRouter(prefix="/plugins", tags=["plugins"])

# Global registry instance
plugin_registry = PluginRegistryService()


@router.get("")
async def list_plugins() -> dict:
    """List all registered plugins."""
    plugins = plugin_registry.list_plugins()
    return success_response(
        {"plugins": [{"name": p.name, "version": p.version} for p in plugins]}
    )
