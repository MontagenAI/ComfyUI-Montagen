import time
import threading
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional


class MontagenCacheManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """
        Ensure only one instance of MontagenCacheManager is created.
        """
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(MontagenCacheManager, cls).__new__(cls)
                    cls._instance.__init_once__(*args, **kwargs)
        return cls._instance

    def __init_once__(
        self,
        expire_time: int = 3600,
        cleanup_interval: int = 60,
        lock_timeout: float = 0.5,
    ):
        """
        Initialize the cache manager.

        :param expire_time: Cache item expiration time in seconds
        :param cleanup_interval: Interval in seconds between cleanups
        :param lock_timeout: Maximum time in seconds that clear_expired can hold the lock
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.expire_time = expire_time
        self.lock = threading.RLock()
        self.events: Dict[str, List[Callable]] = defaultdict(list)
        self.cleanup_interval = cleanup_interval
        self.lock_timeout = lock_timeout
        self._cleanup_thread = None
        self._stop_event = threading.Event()
        self._lock_held = False
        self.start_background_cleanup()

    def add(self, key: str, value: Any):
        """
        Add a new cache item.

        :param key: Cache item key
        :param value: Cache item value
        """
        with self.lock:
            self.cache[key] = {"value": value, "last_access": time.time()}
            self.emit("add", key, value)

    def update(self, key: str, update_callback: Callable[[str, Any], Any]):
        """
        Update a cache item.

        :param key: Cache item key
        :param update_callback: Update callback function
        """
        with self.lock:
            if key in self.cache:
                self.cache[key]["value"] = update_callback(
                    key, self.cache[key]["value"]
                )
                self.cache[key]["last_access"] = time.time()
                self.emit("update", key, self.cache[key]["value"])

    def get(self, key: str) -> Optional[Any]:
        """
        Get a cache item by key.

        :param key: Cache item key
        :return: Cache item value, or None if it does not exist or has expired
        """
        with self.lock:
            if key in self.cache:
                if time.time() - self.cache[key]["last_access"] < self.expire_time:
                    self.cache[key]["last_access"] = time.time()
                    self.emit("access", key, self.cache[key]["value"])
                    return self.cache[key]["value"]
                else:
                    self.delete(key)
                    self.emit("expire", key)
        return None

    def delete(self, key: str):
        """
        Delete a cache item.

        :param key: Cache item key
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.emit("delete", key)

    def clear_expired(self, stopped: Callable[[], bool] = None):
        """
        Clear all expired cache items.
        """
        lock_acquired = self.lock.acquire(blocking=False)
        if not lock_acquired:
            return

        self._lock_held = True
        try:
            start_time = time.time()
            current_time = time.time()
            keys_to_delete = [
                key
                for key, item in self.cache.items()
                if current_time - item["last_access"] >= self.expire_time
            ]
            for key in keys_to_delete:
                if time.time() - start_time > self.lock_timeout:
                    break
                if stopped and stopped():
                    break
                del self.cache[key]
                self.emit("expire", key)
        finally:
            self.lock.release()
            self._lock_held = False

    def on(self, event: str, callback: Callable):
        """
        Add an event listener.

        :param event: Event name
        :param callback: Callback function
        """
        self.events[event].append(callback)

    def off(self, event: str, callback: Callable):
        """
        Remove an event listener.

        :param event: Event name
        :param callback: Callback function to remove
        """
        with self.lock:
            if event in self.events:
                self.events[event] = [cb for cb in self.events[event] if cb != callback]

    def emit(self, event: str, *args, **kwargs):
        """
        Trigger an event.

        :param event: Event name
        :param args: Positional arguments for the callback function
        :param kwargs: Keyword arguments for the callback function
        """
        for callback in self.events[event]:
            callback(*args, **kwargs)

    def get_all(self) -> Dict[str, Any]:
        """
        Get all cache items.

        :return: Dictionary of all cache items
        """
        with self.lock:
            return {key: item["value"] for key, item in self.cache.items()}

    def start_background_cleanup(self):
        """
        Start a background thread to clean up expired cache items at regular intervals.
        """

        def cleanup_task():
            while not self._stop_event.is_set():
                if self._stop_event.wait(self.cleanup_interval):
                    break
                self.clear_expired(lambda: self._stop_event.is_set())

        self._cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        self._cleanup_thread.start()

    def stop(self):
        """
        Stop the background cleanup thread.
        """
        self._stop_event.set()
        if self._cleanup_thread:
            self._cleanup_thread.join()
