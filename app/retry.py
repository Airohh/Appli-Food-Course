# Retry automatique avec délai qui augmente progressivement

from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    # Réessaie automatiquement si ça plante, avec un délai qui double à chaque fois
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as exc:
                    last_exception = exc
                    
                    if attempt == max_attempts:
                        # Plus de tentatives, on abandonne
                        raise
                    
                    # Délai qui augmente : 1s, 2s, 4s, etc.
                    delay = min(
                        base_delay * (exponential_base ** (attempt - 1)),
                        max_delay
                    )
                    
                    print(
                        f"   [RETRY] Tentative {attempt}/{max_attempts} échouée: {exc}"
                        f" - Réessaie dans {delay:.1f}s"
                    )
                    
                    time.sleep(delay)
            
            # Normalement on arrive jamais ici
            if last_exception:
                raise last_exception
            raise RuntimeError("Bug dans le retry")
        
        return wrapper
    return decorator


def retry_openai(
    max_attempts: int = 3,
    base_delay: float = 1.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    # Retry pour OpenAI, gère les rate limits et timeouts
    from openai import APIError, APITimeoutError, RateLimitError
    
    return retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=60.0,
        exponential_base=2.0,
        retryable_exceptions=(APIError, APITimeoutError, RateLimitError, ConnectionError),
    )


def retry_http(
    max_attempts: int = 3,
    base_delay: float = 1.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    # Retry pour les appels HTTP (Spoonacular, etc.), gère les erreurs réseau
    import requests
    
    return retry_with_backoff(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=30.0,
        exponential_base=2.0,
        retryable_exceptions=(
            requests.exceptions.RequestException,
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
        ),
    )

