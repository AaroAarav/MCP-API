from cachetools import TTLCache
from typing import Any, Optional, Dict
import hashlib
import json

class CacheManager:
    def __init__(self):
        # We will use a dictionary of TTLCaches to support different TTLs per endpoint category
        self.caches: Dict[str, TTLCache] = {
            "30s": TTLCache(maxsize=1000, ttl=30),
            "10s": TTLCache(maxsize=1000, ttl=10),
            "60s": TTLCache(maxsize=1000, ttl=60),
            "120s": TTLCache(maxsize=1000, ttl=120),
            "300s": TTLCache(maxsize=1000, ttl=300),
            "3600s": TTLCache(maxsize=100, ttl=3600),
        }

    def _generate_key(self, endpoint: str, params: dict) -> str:
        # Create a deterministic string from the parameters
        param_str = json.dumps(params, sort_keys=True)
        # Hash it to save space
        hash_val = hashlib.md5(param_str.encode()).hexdigest()
        return f"{endpoint}:{hash_val}"

    def get(self, ttl_category: str, endpoint: str, params: dict) -> Optional[Any]:
        if ttl_category not in self.caches:
            return None
        key = self._generate_key(endpoint, params)
        return self.caches[ttl_category].get(key)

    def set(self, ttl_category: str, endpoint: str, params: dict, value: Any) -> None:
        if ttl_category in self.caches:
            key = self._generate_key(endpoint, params)
            self.caches[ttl_category][key] = value

    def invalidate(self, ttl_category: str, endpoint: str, params: dict) -> None:
        if ttl_category in self.caches:
            key = self._generate_key(endpoint, params)
            if key in self.caches[ttl_category]:
                del self.caches[ttl_category][key]

    def clear(self, ttl_category: str) -> None:
        if ttl_category in self.caches:
            self.caches[ttl_category].clear()

cache_manager = CacheManager()
