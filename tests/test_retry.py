"""Tests pour le module retry."""

import time
from unittest.mock import patch

import pytest

from app.retry import retry_openai, retry_with_backoff


def test_retry_success():
    """Test que retry ne fait rien si la fonction réussit."""
    call_count = 0
    
    @retry_with_backoff(max_attempts=3, base_delay=0.01)
    def success_func():
        nonlocal call_count
        call_count += 1
        return "success"
    
    result = success_func()
    assert result == "success"
    assert call_count == 1  # Appelé une seule fois


def test_retry_failure_then_success():
    """Test que retry réessaie en cas d'échec puis réussit."""
    call_count = 0
    
    @retry_with_backoff(max_attempts=3, base_delay=0.01)
    def flaky_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError("Temporary error")
        return "success"
    
    result = flaky_func()
    assert result == "success"
    assert call_count == 2  # Appelé 2 fois


def test_retry_max_attempts():
    """Test que retry échoue après max_attempts."""
    call_count = 0
    
    @retry_with_backoff(max_attempts=3, base_delay=0.01)
    def always_fail():
        nonlocal call_count
        call_count += 1
        raise ValueError("Always fails")
    
    with pytest.raises(ValueError, match="Always fails"):
        always_fail()
    
    assert call_count == 3  # Appelé 3 fois (max_attempts)


def test_retry_backoff_delay():
    """Test que le délai augmente avec backoff exponentiel."""
    delays = []
    
    def mock_sleep(delay):
        delays.append(delay)
    
    call_count = 0
    
    @retry_with_backoff(max_attempts=3, base_delay=0.1, exponential_base=2.0)
    def flaky_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("Error")
        return "success"
    
    with patch('time.sleep', mock_sleep):
        result = flaky_func()
    
    assert result == "success"
    # Vérifier que les délais augmentent: 0.1, 0.2 (0.1 * 2^1)
    assert len(delays) == 2
    assert delays[0] == 0.1
    assert delays[1] == 0.2

