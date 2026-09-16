from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class BaseTool(ABC):
    """Base class for all tools that can be executed by the chat services."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The intent string this tool handles (must match UserIntent enum value)"""
        pass

    @abstractmethod
    def get_extraction_prompt(self, message: str, **kwargs) -> str:
        """
        Return English prompt for extracting parameters from user message.

        Args:
            message: The user's input message
            **kwargs: Tool-specific context (e.g., categories, partial data)

        Returns:
            str: Complete extraction prompt in English
        """
        pass

    @property
    @abstractmethod
    def schema(self) -> Dict[str, Any]:
        """The JSON schema to guide the LLM extraction"""
        pass


    @abstractmethod
    def execute(self, params: Dict[str, Any], user_id: int) -> Tuple[str, str]:
        """
        Execute the tool with the given parameters.

        Args:
            params: Validated parameters matching the schema
            user_id: ID of the user executing the tool

        Returns:
            tuple: (description_of_action, action_type)
        """
        pass