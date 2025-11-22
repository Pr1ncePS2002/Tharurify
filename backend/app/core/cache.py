from functools import lru_cache
import time
from typing import Any, Dict, Optional

# Simple in-process TTL cache; can be replaced with Redis backend transparently
class TTLCache:
    def __init__(self, ttl_seconds: int = 300, max_items: int = 256):
        self.ttl = ttl_seconds
        self.max_items = max_items
        self.store: Dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self.store.get(key)
        if not entry:
            return None
        ts, value = entry
        if time.time() - ts > self.ttl:
            self.store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any):
        if len(self.store) >= self.max_items:
            # naive eviction: remove oldest
            oldest_key = min(self.store.items(), key=lambda kv: kv[1][0])[0]
            self.store.pop(oldest_key, None)
        self.store[key] = (time.time(), value)

resume_cache = TTLCache(ttl_seconds=900, max_items=128)
