"""
Router module for deciding between cloud and sovereign (local) LLM routing.

This module handles the routing logic and LLM API invocations for both
cloud (OpenAI) and local (Ollama) models.
"""

import logging
import time
from typing import Tuple

import requests

from .config import config
from .models import PIIDetection

logger = logging.getLogger(__name__)


class LLMRouter:
    """
    Routes prompts to either cloud AI (OpenAI) or local LLM (Ollama)
    based on PII sensitivity score.
    """

    def __init__(self):
        """Initialize the LLM router with configuration."""
        self.openai_api_key = config.openai_api_key or ""
        self.openai_base_url = config.openai_base_url
        self.openai_model = config.openai_model
        self.openai_timeout = config.openai_timeout
        self.openai_max_tokens = config.openai_max_tokens

        self.ollama_base_url = config.ollama_base_url
        self.ollama_model = config.ollama_model
        self.ollama_timeout = config.ollama_timeout

        self.pii_threshold = config.pii_threshold

        logger.info(
            f"Router initialized: threshold={self.pii_threshold}, "
            f"openai_model={self.openai_model}, ollama_model={self.ollama_model}"
        )

    def route_and_infer(
        self, prompt: str, pii_detections: list[PIIDetection], pii_score: float
    ) -> Tuple[str, str, float]:
        """
        Route prompt and get inference result.

        Args:
            prompt: User prompt
            pii_detections: List of detected PII
            pii_score: Overall PII sensitivity score

        Returns:
            Tuple of (response_text, route_used, processing_time_ms)

        Raises:
            ValueError: If prompt is empty or invalid
        """
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string")

        if not isinstance(pii_score, (int, float)) or pii_score < 0 or pii_score > 1:
            raise ValueError(f"PII score must be between 0.0 and 1.0, got {pii_score}")

        start_time = time.time()

        # Routing decision
        if pii_score >= self.pii_threshold or len(pii_detections) > 0:
            # Route to sovereign (local) LLM
            route = "sovereign"
            response = self._call_ollama(prompt)
        else:
            # Route to cloud LLM
            route = "cloud"
            response = self._call_openai(prompt)

        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        return response, route, processing_time

    def _call_openai(self, prompt: str) -> str:
        """
        Call OpenAI API for inference.

        Args:
            prompt: User prompt text

        Returns:
            AI-generated response text or error message
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not configured")
            return "[ERROR] OpenAI API key not configured. Falling back to local model."

        try:
            logger.debug(f"Calling OpenAI API with model: {self.openai_model}")

            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.openai_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.openai_max_tokens,
                "temperature": 0.7,
            }

            response = requests.post(
                f"{self.openai_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.openai_timeout,
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                logger.debug(f"OpenAI API call successful, response length: {len(content)}")
                return content
            else:
                error_msg = f"OpenAI API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return f"[ERROR] {error_msg}"

        except requests.exceptions.Timeout:
            error_msg = f"OpenAI API timeout after {self.openai_timeout}s"
            logger.error(error_msg)
            return f"[ERROR] {error_msg}"
        except requests.exceptions.RequestException as e:
            error_msg = f"OpenAI API request failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"[ERROR] {error_msg}"
        except Exception as e:
            error_msg = f"OpenAI API call failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"[ERROR] {error_msg}"

    def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama local LLM for inference.

        Args:
            prompt: User prompt text

        Returns:
            AI-generated response text or error message
        """
        try:
            logger.debug(f"Calling Ollama API with model: {self.ollama_model}")

            payload = {"model": self.ollama_model, "prompt": prompt, "stream": False}

            response = requests.post(
                f"{self.ollama_base_url}/api/generate", json=payload, timeout=self.ollama_timeout
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "[ERROR] No response from Ollama")
                logger.debug(f"Ollama API call successful, response length: {len(content)}")
                return content
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return f"[ERROR] {error_msg}"

        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to Ollama. Ensure Ollama is running and accessible."
            logger.error(error_msg)
            return f"[ERROR] {error_msg}"
        except requests.exceptions.Timeout:
            error_msg = f"Ollama API timeout after {self.ollama_timeout}s"
            logger.error(error_msg)
            return f"[ERROR] {error_msg}"
        except requests.exceptions.RequestException as e:
            error_msg = f"Ollama API request failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"[ERROR] {error_msg}"
        except Exception as e:
            error_msg = f"Ollama API call failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return f"[ERROR] {error_msg}"

    def get_model_name(self, route: str) -> str:
        """Get the model name used for a given route."""
        if route == "cloud":
            return self.openai_model
        else:
            return f"{self.ollama_model} (local)"
