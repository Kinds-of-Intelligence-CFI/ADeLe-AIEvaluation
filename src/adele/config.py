"""
Configuration management for ADeLe.

Handles API keys, default settings, and environment variables.
Supports .env files and explicit configuration.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AdeleConfig:
    """Configuration for ADeLe operations.

    API keys can be provided explicitly or loaded from environment variables.
    Environment variables take the following names:
        - OPENAI_API_KEY
        - AZURE_OPENAI_API_KEY
        - AZURE_OPENAI_ENDPOINT
        - HF_TOKEN (HuggingFace)
    """

    # Annotation settings
    annotator_model: str = "gpt-4o"
    max_completion_tokens: int = 1000

    # API keys (loaded from env if not provided)
    openai_api_key: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    hf_token: Optional[str] = None

    # Output
    output_dir: str = "./adele_results"

    def __post_init__(self):
        """Load API keys from environment if not explicitly set."""
        if self.openai_api_key is None:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.azure_openai_api_key is None:
            self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if self.azure_openai_endpoint is None:
            self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if self.hf_token is None:
            self.hf_token = os.getenv("HF_TOKEN")

    @property
    def has_openai(self) -> bool:
        return self.openai_api_key is not None

    @property
    def has_azure(self) -> bool:
        return (
            self.azure_openai_api_key is not None
            and self.azure_openai_endpoint is not None
        )
