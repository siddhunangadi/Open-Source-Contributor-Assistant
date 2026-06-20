import os
from typing import Type

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_mistralai import ChatMistralAI

load_dotenv()


class LLMService:
    """
    Centralized LLM service used throughout the application.
    """

    _llm = None

    @classmethod
    def get_llm(cls) -> ChatMistralAI:
        """
        Returns a singleton LLM instance.
        """

        if cls._llm is None:
            cls._llm = ChatMistralAI(
                model="mistral-small-2506",
                api_key=os.getenv("MISTRAL_API_KEY"),
                temperature=0,
            )

        return cls._llm

    @classmethod
    def get_structured_llm(
        cls,
        schema: Type[BaseModel]
    ):
        """
        Returns an LLM configured for structured output.
        """

        return cls.get_llm().with_structured_output(schema)