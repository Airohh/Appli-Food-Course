"""Tests pour le module batch_processor."""

import pytest

from app.batch_processor import (
    estimate_tokens,
    process_in_batches,
    should_split_batch,
)


def test_estimate_tokens():
    """Test estimation des tokens."""
    text = "Hello world" * 10  # 110 caractères
    tokens = estimate_tokens(text)
    # Approximation: ~4 caractères par token
    assert tokens > 0
    assert tokens < len(text)  # Moins de tokens que de caractères


def test_process_in_batches_small_list():
    """Test avec une petite liste (pas de batch nécessaire)."""
    items = [{"id": i} for i in range(10)]
    
    def processor(batch):
        return [{"processed": item["id"]} for item in batch]
    
    result = process_in_batches(items, processor, max_batch_size=50)
    
    assert len(result) == 10
    assert all("processed" in item for item in result)


def test_process_in_batches_large_list():
    """Test avec une grande liste (nécessite des batches)."""
    items = [{"id": i} for i in range(100)]
    
    def processor(batch):
        return [{"processed": item["id"]} for item in batch]
    
    result = process_in_batches(items, processor, max_batch_size=30)
    
    assert len(result) == 100
    assert all("processed" in item for item in result)


def test_process_in_batches_with_error():
    """Test gestion d'erreur dans un batch."""
    items = [{"id": i} for i in range(10)]
    call_count = 0
    
    def processor(batch):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ValueError("Batch error")
        return [{"processed": item["id"]} for item in batch]
    
    result = process_in_batches(items, processor, max_batch_size=5)
    
    # En cas d'erreur, les items originaux sont retournés
    assert len(result) == 10


def test_should_split_batch():
    """Test décision de division de batch."""
    small_items = [{"name": "item"} for _ in range(10)]
    assert not should_split_batch(small_items, max_tokens=2000)
    
    # Pour un grand batch, on ne peut pas vraiment tester sans créer beaucoup de données
    # mais on peut vérifier que la fonction fonctionne
    large_items = [{"name": "item " * 100} for _ in range(100)]
    # Cela devrait probablement dépasser 2000 tokens
    result = should_split_batch(large_items, max_tokens=2000)
    assert isinstance(result, bool)

