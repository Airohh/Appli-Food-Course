# Traite les grandes listes par petits morceaux pour pas dépasser les limites de tokens

from __future__ import annotations

from typing import Any, Callable, Dict, List, TypeVar

T = TypeVar("T")


def process_in_batches(
    items: List[Dict[str, Any]],
    processor: Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]],
    max_batch_size: int = 50,
    max_tokens_estimate: int = 2000,
) -> List[Dict[str, Any]]:
    # Divise une grosse liste en petits morceaux et les traite un par un
    if not items:
        return []
    
    if len(items) <= max_batch_size:
        # Pas assez d'items, on traite tout d'un coup
        return processor(items)
    
    # On divise en petits morceaux
    results: List[Dict[str, Any]] = []
    total_batches = (len(items) + max_batch_size - 1) // max_batch_size
    
    for batch_idx in range(0, len(items), max_batch_size):
        batch = items[batch_idx : batch_idx + max_batch_size]
        batch_num = (batch_idx // max_batch_size) + 1
        
        print(f"   [BATCH] Traitement batch {batch_num}/{total_batches} ({len(batch)} items)...")
        
        try:
            processed_batch = processor(batch)
            results.extend(processed_batch)
        except Exception as exc:
            print(f"   [ERROR] Erreur dans le batch {batch_num}: {exc}")
            # Si ça plante, on garde les items originaux
            results.extend(batch)
    
    return results


def estimate_tokens(text: str) -> int:
    # Estime le nombre de tokens (approximation: ~4 caractères = 1 token)
    return len(text) // 4


def should_split_batch(items: List[Dict[str, Any]], max_tokens: int = 2000) -> bool:
    # Vérifie si un batch est trop gros et doit être divisé
    import json
    
    json_str = json.dumps(items, ensure_ascii=False)
    estimated_tokens = estimate_tokens(json_str)
    
    return estimated_tokens > max_tokens

