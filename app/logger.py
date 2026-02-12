# Logging vers fichier et console

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .config import DATA_DIR

# Dossier pour les logs
LOG_DIR = DATA_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Logger principal
logger = logging.getLogger("appli_food_course")
logger.setLevel(logging.INFO)

# Évite d'ajouter plusieurs fois les mêmes handlers
if not logger.handlers:
    # Log vers fichier
    file_handler = logging.FileHandler(
        LOG_DIR / "app.log",
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Log vers console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "[%(levelname)s] %(message)s",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)


def log_llm_call(
    function_name: str,
    model: str,
    prompt_version: Optional[str] = None,
    tokens_used: Optional[int] = None,
    cost_estimate: Optional[float] = None,
    success: bool = True,
    error: Optional[str] = None,
) -> None:
    # Log un appel LLM avec les infos importantes (tokens, coût, etc.)
    log_data: Dict[str, Any] = {
        "type": "llm_call",
        "function": function_name,
        "model": model,
        "success": success,
    }
    
    if prompt_version:
        log_data["prompt_version"] = prompt_version
    if tokens_used:
        log_data["tokens"] = tokens_used
    if cost_estimate:
        log_data["cost_usd"] = cost_estimate
    if error:
        log_data["error"] = error
    
    if success:
        logger.info(f"LLM call: {function_name} - Model: {model} - Tokens: {tokens_used} - Cost: ${cost_estimate:.6f}")
    else:
        logger.error(f"LLM call failed: {function_name} - Error: {error}")


def log_api_call(
    service: str,
    endpoint: str,
    success: bool = True,
    status_code: Optional[int] = None,
    error: Optional[str] = None,
) -> None:
    # Log un appel API (Spoonacular, Notion, etc.)
    if success:
        logger.info(f"API call: {service} - {endpoint} - Status: {status_code}")
    else:
        logger.error(f"API call failed: {service} - {endpoint} - Error: {error}")


def log_validation_error(
    function_name: str,
    errors: list[str],
    data_type: str = "courses",
) -> None:
    # Log les erreurs de validation
    error_count = len(errors)
    error_summary = "; ".join(errors[:3])  # Max 3 erreurs pour pas surcharger
    if error_count > 3:
        error_summary += f" ... et {error_count - 3} autres"
    
    logger.warning(
        f"Validation failed in {function_name} ({data_type}): {error_count} error(s) - {error_summary}"
    )


def log_retry(
    function_name: str,
    attempt: int,
    max_attempts: int,
    error: str,
    delay: float,
) -> None:
    # Log quand on réessaie après une erreur
    logger.warning(
        f"Retry {attempt}/{max_attempts} for {function_name}: {error} - Retrying in {delay:.1f}s"
    )

