# SPDX-License-Identifier: Apache-2.0
"""Configuration management using environment variables."""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class Config(BaseModel):
    """Application configuration loaded from environment variables.

    Follows 12-factor app principle: configuration via environment.
    """

    # CESSDA API Configuration
    api_base_url: str = Field(
        default="https://datacatalogue.cessda.eu/api",
        description="Base URL for CESSDA Data Catalogue API"
    )

    api_timeout: int = Field(
        default=30,
        description="API request timeout in seconds"
    )

    api_max_retries: int = Field(
        default=3,
        description="Maximum number of API request retries"
    )

    # Logging Configuration
    log_level: str = Field(
        default="WARN",
        description="Default logging level (WARN per CESSDA guidelines)"
    )

    # Default search parameters
    default_metadata_language: str = Field(
        default="en",
        description="Default language for metadata (ISO 639-1 code)"
    )

    default_search_limit: int = Field(
        default=10,
        description="Default number of search results to return"
    )

    max_search_limit: int = Field(
        default=200,
        description="Maximum allowed search results per request"
    )

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.

        Environment variables:
            CESSDA_API_BASE_URL: Base URL for API
            CESSDA_API_TIMEOUT: Request timeout in seconds
            CESSDA_API_MAX_RETRIES: Max retry attempts
            CESSDA_LOG_LEVEL: Logging level
            CESSDA_DEFAULT_LANGUAGE: Default metadata language
            CESSDA_DEFAULT_LIMIT: Default search result limit
            CESSDA_MAX_LIMIT: Maximum search result limit
        """
        return cls(
            api_base_url=os.getenv("CESSDA_API_BASE_URL", cls.model_fields["api_base_url"].default),
            api_timeout=int(os.getenv("CESSDA_API_TIMEOUT", str(cls.model_fields["api_timeout"].default))),
            api_max_retries=int(os.getenv("CESSDA_API_MAX_RETRIES", str(cls.model_fields["api_max_retries"].default))),
            log_level=os.getenv("CESSDA_LOG_LEVEL", cls.model_fields["log_level"].default),
            default_metadata_language=os.getenv("CESSDA_DEFAULT_LANGUAGE", cls.model_fields["default_metadata_language"].default),
            default_search_limit=int(os.getenv("CESSDA_DEFAULT_LIMIT", str(cls.model_fields["default_search_limit"].default))),
            max_search_limit=int(os.getenv("CESSDA_MAX_LIMIT", str(cls.model_fields["max_search_limit"].default))),
        )


# Global config instance
config = Config.from_env()
