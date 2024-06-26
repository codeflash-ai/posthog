import typing
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class PostHogWorkflow(ABC):
    """Base class for Temporal Workflows that can be executed in PostHog."""

    @classmethod
    def get_name(cls) -> str:
        """Get this workflow's name."""
        return getattr(cls, "__temporal_workflow_definition").name

    @classmethod
    def is_named(cls, name: str) -> bool:
        """Check if this workflow's name matches name.

        All temporal workflows have the __temporal_workflow_definition attribute
        injected into them by the defn decorator. We use it to access the name and
        avoid having to define it twice. If this changes in the future, we can
        update this method instead of changing every single workflow.
        """
        return cls.get_name() == name

    @staticmethod
    @abstractmethod
    def parse_inputs(inputs: List[str]) -> Dict[str, Any]:
        """Parse inputs from the management command CLI.

        This method converts a list of string inputs from the CLI into a
        structured dictionary that can be used within the workflow.

        Parameters
        ----------
        inputs : list of str
            String inputs provided via the CLI.

        Returns
        -------
        dict of str to Any
            Structured dictionary representation of parsed inputs.
        """
        raise NotImplementedError
