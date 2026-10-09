"""
IMS Redis / In-Memory Caching Engine
Provides sub-millisecond caching for heavy FFT spectra and model inference outputs.
"""

import time
import sys
import os
import hashlib
from typing import Any, Optional, Dict

# Ensure src module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class InMemoryCacheManager:
    """
    Implements high-speed key-value cache with LRU eviction and Time-To-Live (TTL).
    """

    def __init__(self, max_capacity: int = 100, default_ttl_sec: float = 300.0):
        self.capacity = max_capacity
        self.ttl = default_ttl_sec
        self.cache: Dict[str, Dict[str, Any]] = {}

    def _generate_key(self, signal_data: Any) -> str:
        """Generates deterministic MD5 hash key for caching signal arrays."""
        if hasattr(signal_data, "tobytes"):
            raw_bytes = signal_data.tobytes()
        else:
            raw_bytes = str(signal_data).encode("utf-8")
        return hashlib.md5(raw_bytes).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """Retrieves cached item if valid and not expired."""
        if key in self.cache:
            entry = self.cache[key]
            if (time.time() - entry["timestamp"]) < entry["ttl"]:
                entry["hits"] += 1
                return entry["data"]
            else:
                del self.cache[key] # Expired
        return None

    def set(self, key: str, value: Any, ttl_sec: Optional[float] = None):
        """Caches an item with TTL."""
        if len(self.cache) >= self.capacity:
            # LRU Eviction: remove oldest item
            oldest_key = min(self.cache, key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]

        self.cache[key] = {
            "data": value,
            "timestamp": time.time(),
            "ttl": ttl_sec if ttl_sec is not None else self.ttl,
            "hits": 0
        }

if __name__ == "__main__":
    cache = InMemoryCacheManager(max_capacity=5, default_ttl_sec=10)
    
    # Cache FFT spectrum calculation
    fake_fft = {"freqs": [10, 20, 30], "amps": [0.1, 0.5, 0.2]}
    key = cache._generate_key("signal_snapshot_001")
    
    cache.set(key, fake_fft)
    cached_val = cache.get(key)
    
    print(f"[SUCCESS] In-Memory Cache Hit: {cached_val is not None}")
    print(f"[CACHE ENTRY] Data: {cached_val}")
