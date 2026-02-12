"""Client Notion avec retry et gestion d'erreurs."""

from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable, TypeVar

from notion_client import Client
from notion_client.errors import APIResponseError

from app.retry import retry_with_backoff
from integrations.notion.config import get_config

T = TypeVar("T")


def _is_retryable_notion_error(exc: Exception) -> bool:
    """Détermine si une erreur Notion est retryable (429, 5xx)."""
    if isinstance(exc, APIResponseError):
        status = getattr(exc, "code", None) or getattr(exc, "status", None)
        if status:
            # Rate limit (429) ou erreurs serveur (5xx)
            return status == 429 or (500 <= status < 600)
    # Erreurs réseau, timeouts, etc.
    return isinstance(exc, (ConnectionError, TimeoutError))


def retry_notion(
    max_attempts: int = 5,
    base_delay: float = 0.5,
    max_delay: float = 60.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Décorateur de retry spécialisé pour Notion (429, 5xx).
    
    Utilise un backoff exponentiel avec jitter pour éviter les thundering herds.
    """
    return retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=2.0,
        retryable_exceptions=(APIResponseError, ConnectionError, TimeoutError),
    )


def safe_notion_call(
    func: Callable[..., T],
    *args: Any,
    **kwargs: Any,
) -> T:
    """
    Appelle une fonction Notion avec retry automatique et logging.
    
    Usage:
        result = safe_notion_call(client.pages.create, parent={...}, properties={...})
    """
    @retry_notion(max_attempts=5, base_delay=0.5)
    def _wrapped() -> T:
        try:
            return func(*args, **kwargs)
        except APIResponseError as e:
            status = getattr(e, "code", None) or getattr(e, "status", None)
            if status == 429:
                # Rate limit : on attend un peu plus
                time.sleep(1.0)
            raise

    return _wrapped()


_client: Client | None = None


def get_client() -> Client:
    """
    Retourne le client Notion (singleton).
    
    Utilise la configuration chargée via get_config().
    """
    global _client
    if _client is None:
        config = get_config()
        if not config.api_key:
            raise RuntimeError(
                "Clé API Notion manquante. Configure NOTION_API_KEY ou NOTION_TOKEN."
            )
        _client = Client(auth=config.api_key)
    return _client

