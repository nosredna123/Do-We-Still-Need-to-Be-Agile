from typing import List, Dict, Any
from src.llm.interface import LLMInterface, LLMMessage


class DummyLLM(LLMInterface):
    """
    A placeholder LLM that conforms to the new agentic interface.
    """

    def get_chat_response(self, messages: List[LLMMessage]) -> str:
        """
        Returns a canned response, useful for testing the services logic.
        """
        last_message = messages[-1]["content"] if messages else ""
        return f"This is a dummy response to your message: '{last_message}'"

    def extract_structured_data(
        self, prompt: str, output_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Returns a dummy dictionary, simulating a failed extraction.
        This forces the services to handle the "no intent" case.
        """
        return {}
