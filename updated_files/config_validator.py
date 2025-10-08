"""
Configuration validation utilities for the CESAR ecosystem.

The functions in this module perform sanity checks on runtime
configuration dictionaries.  They raise ``ValueError`` with
descriptive messages when required fields are missing or invalid.
Using these helpers early in the boot sequence prevents ambiguous
runtime errors later on.

Currently provided utilities:

* ``validate_memory_config`` — verify that the memory provider
  configuration is complete.  Ensures that when Mem0 is requested
  (either exclusively or as part of a hybrid strategy) the API key
  is provided.

Additional validation helpers should be added here as the
configuration schema evolves.
"""

from __future__ import annotations

from typing import Dict, Any


def validate_memory_config(config: Dict[str, Any]) -> None:
    """Validate the memory configuration.

    This function checks that required fields are present for the
    selected memory provider.  It raises ``ValueError`` with a
    descriptive message if the configuration is invalid.

    Args:
        config: Configuration dictionary with ``mem0`` and ``cesar``
            subsections and an optional ``provider_preference`` field.

    Raises:
        ValueError: If the configuration is missing required fields.
    """
    provider_preference: str = config.get("provider_preference", "hybrid").lower()
    mem0_config: Dict[str, Any] = config.get("mem0", {})
    cesar_config: Dict[str, Any] = config.get("cesar", {})

    # If Mem0 is requested (alone or hybrid), require an API key
    if provider_preference in ("mem0", "hybrid"):
        api_key = mem0_config.get("api_key")
        if not api_key:
            raise ValueError(
                "Mem0 provider selected but 'mem0.api_key' is missing. "
                "Set an API key in the configuration or choose a provider "
                "that does not require Mem0."
            )

    # For CESAR Sheets provider, require a spreadsheet ID and credentials
    if provider_preference in ("cesar", "hybrid"):
        spreadsheet_id = cesar_config.get("memory_spreadsheet_id")
        credentials_path = cesar_config.get("google_credentials_path")
        if not spreadsheet_id or not credentials_path:
            raise ValueError(
                "CESAR provider selected but 'cesar.memory_spreadsheet_id' or "
                "'cesar.google_credentials_path' is missing.  Please supply "
                "both values."
            )