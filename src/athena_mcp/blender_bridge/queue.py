from __future__ import annotations

from queue import Empty, SimpleQueue
from typing import Callable, Optional

_queue: SimpleQueue[Callable[[], None]] = SimpleQueue()


def push(task: Callable[[], None]) -> None:
    _queue.put(task)


def pop() -> Optional[Callable[[], None]]:
    try:
        return _queue.get_nowait()
    except Empty:
        return None


def size() -> int:
    return _queue.qsize()
