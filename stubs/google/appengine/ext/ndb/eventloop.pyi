import threading
from typing import Any

class _Clock:
    def now(self): ...
    def sleep(self, seconds) -> None: ...

class EventLoop:
    clock: Any
    current: Any
    idlers: Any
    inactive: int
    queue: Any
    rpcs: Any
    def __init__(self, clock: Any | None = ...) -> None: ...
    def clear(self) -> None: ...
    def insort_event_right(self, event, lo: int = ..., hi: Any | None = ...) -> None: ...
    def queue_call(self, delay, callback, *args, **kwds) -> None: ...
    def queue_rpc(self, rpc, callback: Any | None = ..., *args, **kwds) -> None: ...
    def add_idle(self, callback, *args, **kwds) -> None: ...
    def run_idle(self): ...
    def run0(self): ...
    def run1(self): ...
    def run(self) -> None: ...

class _State(threading.local):
    event_loop: Any

def get_event_loop(): ...
def queue_call(*args, **kwds) -> None: ...
def queue_rpc(rpc, callback: Any | None = ..., *args, **kwds) -> None: ...
def add_idle(callback, *args, **kwds) -> None: ...
def run() -> None: ...
def run1(): ...
def run0(): ...