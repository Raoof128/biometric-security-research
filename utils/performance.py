"""
Performance optimization utilities.
Includes caching, memory management, and performance monitoring.
"""

import time
import psutil
import gc
from functools import lru_cache, wraps
from typing import Callable, Any, Optional, Dict
from collections import OrderedDict
import numpy as np

from utils.logger import get_logger

logger = get_logger(__name__)


class PerformanceMonitor:
    """
    Monitor system performance and resource usage
    """

    def __init__(self):
        """Initialize performance monitor"""
        self.process = psutil.Process()
        self.start_time = time.time()
        self.metrics = []

    def get_memory_usage(self) -> Dict[str, float]:
        """
        Get current memory usage

        Returns:
            dict: Memory usage statistics in MB
        """
        mem_info = self.process.memory_info()

        return {
            'rss_mb': mem_info.rss / (1024 * 1024),  # Resident Set Size
            'vms_mb': mem_info.vms / (1024 * 1024),  # Virtual Memory Size
            'percent': self.process.memory_percent()
        }

    def get_cpu_usage(self) -> float:
        """
        Get current CPU usage

        Returns:
            float: CPU usage percentage
        """
        return self.process.cpu_percent(interval=0.1)

    def log_performance_snapshot(self, label: str = ""):
        """
        Log current performance snapshot

        Args:
            label: Optional label for this snapshot
        """
        mem = self.get_memory_usage()
        cpu = self.get_cpu_usage()
        elapsed = time.time() - self.start_time

        snapshot = {
            'label': label,
            'elapsed_seconds': elapsed,
            'memory_mb': mem['rss_mb'],
            'cpu_percent': cpu
        }

        self.metrics.append(snapshot)

        logger.debug(
            f"Performance [{label}]: "
            f"Memory: {mem['rss_mb']:.1f}MB ({mem['percent']:.1f}%), "
            f"CPU: {cpu:.1f}%, "
            f"Elapsed: {elapsed:.2f}s"
        )

        return snapshot

    def check_memory_limit(self, limit_mb: int) -> bool:
        """
        Check if memory usage exceeds limit

        Args:
            limit_mb: Memory limit in MB

        Returns:
            bool: True if under limit
        """
        mem = self.get_memory_usage()
        if mem['rss_mb'] > limit_mb:
            logger.warning(
                f"Memory usage ({mem['rss_mb']:.1f}MB) exceeds limit ({limit_mb}MB)"
            )
            return False
        return True


class LRUCache:
    """
    LRU (Least Recently Used) cache with size limit
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize LRU cache

        Args:
            max_size: Maximum number of items to cache
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, key: Any) -> Optional[Any]:
        """
        Get item from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if key in self.cache:
            self.hits += 1
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]

        self.misses += 1
        return None

    def put(self, key: Any, value: Any):
        """
        Put item in cache

        Args:
            key: Cache key
            value: Value to cache
        """
        if key in self.cache:
            # Update existing item
            self.cache.move_to_end(key)
            self.cache[key] = value
        else:
            # Add new item
            self.cache[key] = value

            # Remove oldest if cache full
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)

    def clear(self):
        """Clear cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            dict: Cache stats
        """
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }


class EmbeddingCache:
    """
    Specialized cache for face/fingerprint embeddings
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize embedding cache

        Args:
            max_size: Maximum number of embeddings to cache
        """
        self.cache = LRUCache(max_size)
        logger.info(f"Embedding cache initialized with max_size={max_size}")

    def get_embedding(self, image_path: str) -> Optional[np.ndarray]:
        """
        Get cached embedding for image

        Args:
            image_path: Path to image

        Returns:
            numpy.ndarray: Cached embedding or None
        """
        import hashlib

        # Use file hash as key for consistency
        try:
            with open(image_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None

        return self.cache.get(file_hash)

    def put_embedding(self, image_path: str, embedding: np.ndarray):
        """
        Cache embedding for image

        Args:
            image_path: Path to image
            embedding: Embedding vector
        """
        import hashlib

        try:
            with open(image_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()

            self.cache.put(file_hash, embedding)
        except Exception as e:
            logger.warning(f"Failed to cache embedding: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()


def optimize_memory():
    """
    Optimize memory usage by forcing garbage collection
    """
    before = psutil.Process().memory_info().rss / (1024 * 1024)

    gc.collect()

    after = psutil.Process().memory_info().rss / (1024 * 1024)
    freed = before - after

    if freed > 1:  # Only log if significant memory freed
        logger.debug(f"Freed {freed:.1f}MB of memory")

    return freed


def batch_processor(batch_size: int = 10):
    """
    Decorator to process items in batches for better performance

    Args:
        batch_size: Number of items per batch

    Usage:
        @batch_processor(batch_size=5)
        def process_images(images):
            for img in images:
                # process img
                yield result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(items, *args, **kwargs):
            results = []
            total = len(items)

            for i in range(0, total, batch_size):
                batch = items[i:i + batch_size]
                batch_results = func(batch, *args, **kwargs)
                results.extend(batch_results)

                # Optimize memory after each batch
                if i > 0 and i % (batch_size * 5) == 0:
                    optimize_memory()

            return results

        return wrapper
    return decorator


def memoize_with_timeout(timeout_seconds: int = 300):
    """
    Memoization decorator with timeout

    Args:
        timeout_seconds: Cache timeout in seconds

    Usage:
        @memoize_with_timeout(timeout_seconds=60)
        def expensive_function(arg):
            return result
    """
    cache = {}
    cache_times = {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = (args, tuple(sorted(kwargs.items())))

            # Check if cached and not expired
            if key in cache:
                if time.time() - cache_times[key] < timeout_seconds:
                    return cache[key]
                else:
                    # Expired, remove from cache
                    del cache[key]
                    del cache_times[key]

            # Compute result
            result = func(*args, **kwargs)

            # Cache result
            cache[key] = result
            cache_times[key] = time.time()

            return result

        return wrapper
    return decorator


# Global instances
_performance_monitor = None
_embedding_cache = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def get_embedding_cache() -> EmbeddingCache:
    """Get global embedding cache instance"""
    global _embedding_cache
    if _embedding_cache is None:
        from config import get_config
        config = get_config().performance

        cache_size = 1000 if config.cache_embeddings else 0
        _embedding_cache = EmbeddingCache(max_size=cache_size)

    return _embedding_cache
