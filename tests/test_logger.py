"""Tests pour le module logger."""

import logging
from io import StringIO
from unittest.mock import patch

import pytest

from app.logger import log_api_call, log_llm_call, log_retry, log_validation_error, logger


def test_log_llm_call_success():
    """Test logging d'un appel LLM réussi."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.INFO)
    test_logger = logging.getLogger("test_llm")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)
    
    with patch('app.logger.logger', test_logger):
        log_llm_call(
            function_name="test_function",
            model="gpt-4o-mini",
            prompt_version="v1.0",
            tokens_used=100,
            cost_estimate=0.0001,
            success=True,
        )
    
    output = stream.getvalue()
    assert "LLM call" in output
    assert "test_function" in output
    assert "gpt-4o-mini" in output


def test_log_llm_call_failure():
    """Test logging d'un appel LLM échoué."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.ERROR)
    test_logger = logging.getLogger("test_llm_error")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.ERROR)
    
    with patch('app.logger.logger', test_logger):
        log_llm_call(
            function_name="test_function",
            model="gpt-4o-mini",
            success=False,
            error="API timeout",
        )
    
    output = stream.getvalue()
    assert "LLM call failed" in output
    assert "test_function" in output
    assert "API timeout" in output


def test_log_api_call_success():
    """Test logging d'un appel API réussi."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.INFO)
    test_logger = logging.getLogger("test_api")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)
    
    with patch('app.logger.logger', test_logger):
        log_api_call(
            service="Spoonacular",
            endpoint="/recipes/complexSearch",
            success=True,
            status_code=200,
        )
    
    output = stream.getvalue()
    assert "API call" in output
    assert "Spoonacular" in output
    assert "200" in output


def test_log_api_call_failure():
    """Test logging d'un appel API échoué."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.ERROR)
    test_logger = logging.getLogger("test_api_error")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.ERROR)
    
    with patch('app.logger.logger', test_logger):
        log_api_call(
            service="Spoonacular",
            endpoint="/recipes/complexSearch",
            success=False,
            status_code=402,
            error="Quota exceeded",
        )
    
    output = stream.getvalue()
    assert "API call failed" in output
    assert "Spoonacular" in output
    assert "Quota exceeded" in output


def test_log_validation_error():
    """Test logging d'erreurs de validation."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.WARNING)
    test_logger = logging.getLogger("test_validation")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.WARNING)
    
    with patch('app.logger.logger', test_logger):
        log_validation_error(
            function_name="test_function",
            errors=["Error 1", "Error 2", "Error 3"],
            data_type="courses",
        )
    
    output = stream.getvalue()
    assert "Validation failed" in output
    assert "test_function" in output
    assert "courses" in output
    assert "3 error(s)" in output


def test_log_validation_error_many():
    """Test logging avec beaucoup d'erreurs (troncature)."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.WARNING)
    test_logger = logging.getLogger("test_validation_many")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.WARNING)
    
    errors = [f"Error {i}" for i in range(10)]
    
    with patch('app.logger.logger', test_logger):
        log_validation_error(
            function_name="test_function",
            errors=errors,
            data_type="courses",
        )
    
    output = stream.getvalue()
    assert "10 error(s)" in output
    assert "... et 7 autres" in output  # 10 - 3 premiers = 7


def test_log_retry():
    """Test logging d'une tentative de retry."""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.WARNING)
    test_logger = logging.getLogger("test_retry")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.WARNING)
    
    with patch('app.logger.logger', test_logger):
        log_retry(
            function_name="test_function",
            attempt=2,
            max_attempts=3,
            error="Timeout",
            delay=2.5,
        )
    
    output = stream.getvalue()
    assert "Retry 2/3" in output
    assert "test_function" in output
    assert "Timeout" in output
    assert "2.5" in output

