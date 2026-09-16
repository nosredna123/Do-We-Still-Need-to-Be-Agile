from src.utils.enums import UserIntent

def get_intent_schema() -> dict:
    """
    Returns the schema used to route user messages to specific tools.
    """
    valid_intents = [e.value for e in UserIntent]
    return {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "enum": valid_intents,
                "description": (
                    "Classify the user text into an intent. "
                    "'expense': spending money. "
                    "'income': receiving money. "
                    "'query': asking about history/data. "
                    "'chat': general conversation."
                ),
            }
        },
        "required": ["intent"],
    }