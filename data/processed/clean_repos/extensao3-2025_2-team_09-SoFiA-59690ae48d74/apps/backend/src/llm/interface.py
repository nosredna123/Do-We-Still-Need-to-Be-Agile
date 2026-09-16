from abc import ABC, abstractmethod
from typing import List, Dict, Any


class LLMMessage(Dict):
    role: str
    content: str


class LLMInterface(ABC):
    """
    An abstract interface for a self-contained LLM services
    that supports conversational history and structured data extraction.
    """

    @abstractmethod
    def get_chat_response(self, messages: List[LLMMessage]) -> str:
        """
        Processes a list of messages (the conversation history) and
        returns a complete, natural language answer.

        Args:
            messages: The full history of the conversation, including
                      system prompts and context data.

        Returns:
            A final, natural language string to be shown to the user.
        """
        pass

    @abstractmethod
    def extract_structured_data(
        self, prompt: str, output_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        A generic "tool use" function that processes a prompt to extract
        structured data according to a specified JSON schema.

        Args:
            prompt: The raw user input.
            output_schema: A JSON schema describing the desired output format.

        Returns:
            A dictionary matching the provided output_schema.
            Returns an empty dict if extraction fails.
        """
        pass
