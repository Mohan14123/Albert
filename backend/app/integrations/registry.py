from app.integrations.base import BaseIntegration

_registry: dict[str, type[BaseIntegration]] = {}


def register_provider(name: str):
    def wrapper(cls: type[BaseIntegration]):
        _registry[name] = cls
        return cls

    return wrapper


def get_provider(name: str) -> BaseIntegration:
    if name not in _registry:
        raise ValueError(f"Provider {name} not found")
    return _registry[name]()
