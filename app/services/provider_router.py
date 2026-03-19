from app.core.config import get_settings
from app.core.exceptions import ProviderError
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.base import BaseProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.mock_provider import MockProvider
from app.providers.openai_provider import OpenAIProvider


class ProviderRouter:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.providers: dict[str, BaseProvider] = {
            "mock": MockProvider(),
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "gemini": GeminiProvider(),
        }

    def resolve(self, requested_provider: str | None = None) -> BaseProvider:
        name = requested_provider or self.settings.default_provider
        provider = self.providers.get(name)
        if not provider:
            raise ProviderError(f"Unknown provider: {name}")
        return provider

    def resolve_chain(self, requested_provider: str | None = None) -> list[BaseProvider]:
        requested_name = requested_provider or self.settings.default_provider
        if requested_name not in self.providers:
            raise ProviderError(f"Unknown provider: {requested_name}")

        ordered_names: list[str] = [requested_name]
        for fallback_name in self.settings.fallback_order:
            if fallback_name in self.providers and fallback_name not in ordered_names:
                ordered_names.append(fallback_name)

        return [self.providers[name] for name in ordered_names]

    def list_providers(self) -> list[str]:
        return list(self.providers.keys())
