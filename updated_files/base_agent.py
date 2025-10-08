"""
Base class for all CESAR agents.

This module defines the ``BaseAgent`` abstract base class.  All concrete
agents in the CESAR ecosystem should inherit from ``BaseAgent`` to
formalise the interface for memory management and task processing.
By deriving from ``BaseAgent`` you ensure that each agent exposes a
consistent API and can be safely upgraded when the memory system is
enhanced.  Agents that do not inherit from ``BaseAgent`` will cause
the integration layer to raise an error during upgrades.

Key responsibilities enforced by this class:

* A ``memory_manager`` attribute that provides ``store_memory`` and
  ``retrieve_memory`` methods.  The type is intentionally generic
  because concrete implementations may wrap different back‑ends
  (e.g., Mem0, Google Sheets, hybrid providers).
* An asynchronous ``process_task`` method that accepts a task
  dictionary and returns a result dictionary.  This method is used
  by the task orchestrator to delegate work to the agent.
* An asynchronous ``initialize`` method for performing any agent‑level
  startup work.  It should return ``True`` on success and ``False``
  on failure.

Implementations should override these methods and may add
additional functionality as needed.
"""

from __future__ import annotations

import abc
from typing import Any, Dict


class BaseAgent(abc.ABC):
    """Abstract base class for CESAR agents."""

    #: Name of the agent.  Implementations should override this
    #: attribute to provide a human‑readable identifier.
    name: str = "unnamed_agent"

    def __init__(self) -> None:
        # The memory_manager must be set by subclasses during
        # initialization.  It is declared here for static checkers.
        self.memory_manager: Any = None

    @abc.abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent.

        Agents should perform any setup work here, such as
        connecting to external services or allocating resources.

        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return a result.

        Args:
            task: A dictionary describing the task to perform.  The
                structure of this dictionary is agent‑specific and
                should be documented by the concrete agent.

        Returns:
            Dict[str, Any]: A dictionary containing the result of
                processing the task.
        """
        raise NotImplementedError

    # Optional hook: agents may override this to perform cleanup
    async def shutdown(self) -> None:
        """Shutdown the agent and release resources."""
        # Default implementation does nothing.
        return None