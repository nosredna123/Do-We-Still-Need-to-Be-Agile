from .DummyLLM.dummy_llm import DummyLLM
from .RemoteLLM.remote_llm import RemoteLLM
from .interface import LLMInterface


def get_llm_instance(
    model_type: str, model_name: str = None, apiKey: str = None
) -> LLMInterface:
    """
    Factory function to create an instance of an LLM based on its type and an identifier.

    Args:
        model_type (str): The type of model, e.g., 'local', 'remote', 'dummy'.
        model_name (str, optional): The specific model name for LLMs,
        model_name (str, optional): The api key for Remote LLMs,

    Returns:
        LLMInterface: An instantiated LLM class.
    """

    if model_type == "remote":
        if not apiKey:
            raise ValueError("An API key is required for remote LLMs.")
        if model_name:
            return RemoteLLM(api_key=apiKey, model_name=model_name)
        return RemoteLLM(api_key=apiKey)

    elif model_type == "dummy":
        return DummyLLM()

    else:
        raise ValueError(f"Unknown model type specified: {model_type}")
