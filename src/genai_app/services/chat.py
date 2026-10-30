from langchain_ollama import ChatOllama

from genai_app.config import Settings, get_settings
from genai_app.schemas.chat import ChatResponse


class InvalidModelResponseError(Exception):
    """Ollama returned no usable text."""


class ChatService:
    def __init__(self, settings: Settings) -> None:
        self.model_name = settings.ollama_model
        self.llm = ChatOllama(
            base_url=str(settings.ollama_base_url),
            model=self.model_name,
            temperature=0,
            reasoning=False,
            num_predict=512,
            client_kwargs={
                "timeout": settings.ollama_timeout_seconds,
                "trust_env": False,
            },
        )

    async def chat(self, prompt: str) -> ChatResponse:
        message = await self.llm.ainvoke(prompt)
        if not isinstance(message.content, str) or not message.content.strip():
            raise InvalidModelResponseError("Model returned no usable text")
        return ChatResponse(model=self.model_name, response=message.content)


def get_chat_service() -> ChatService:
    return ChatService(get_settings())
