from typing import Dict, Optional, List
from app.repositories.models import ChatPrompt
from threading import Lock

class PromptCacheService:
    _instance = None
    _lock = Lock()
    _cache: Dict[str, ChatPrompt]

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._cache = {}
            return cls._instance

    def get(self, prompt_id: str) -> Optional[ChatPrompt]:
        return self._cache.get(prompt_id)

    def set(self, prompt: ChatPrompt) -> None:
        self._cache[prompt.id] = prompt

    def delete(self, prompt_id: str) -> None:
        self._cache.pop(prompt_id, None)

    def clear(self) -> None:
        self._cache.clear()

    def get_all(self) -> List[ChatPrompt]:
        return list(self._cache.values())

    def refresh_prompt(self, prompt: ChatPrompt) -> None:
        self.set(prompt)