from __future__ import annotations

import threading
from queue import PriorityQueue
from typing import Any, Callable

from parser2gis.task_manager.models import TaskInfo


class TaskQueue:
    def __init__(self, max_concurrent: int = 3) -> None:
        self._max_concurrent = max_concurrent
        self._pending: PriorityQueue[tuple[int, int, TaskInfo]] = PriorityQueue()
        self._running: dict[int, threading.Thread] = {}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

    def enqueue(self, task: TaskInfo, priority: int = 0) -> None:
        self._queue.put((priority, task.id, task))

    def dequeue(self) -> TaskInfo | None:
        try:
            _, _, task = self._queue.get_nowait()
            return task
        except Exception:
            return None

    def start(self, worker: Callable[[TaskInfo], None]) -> None:
        self._stop_event.clear()
        thread = threading.Thread(target=self._run_loop, args=(worker,), daemon=True)
        thread.start()

    def _run_loop(self, worker: Callable[[TaskInfo], None]) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                if len(self._running) >= self._max_concurrent:
                    continue
            task = self.dequeue()
            if task is not None:
                with self._lock:
                    if task.id not in self._running:
                        t = threading.Thread(target=self._run_task, args=(task, worker), daemon=True)
                        self._running[task.id] = t
                        t.start()
            else:
                self._stop_event.wait(0.5)

    def _run_task(self, task: TaskInfo, worker: Callable[[TaskInfo], None]) -> None:
        try:
            worker(task)
        finally:
            with self._lock:
                self._running.pop(task.id, None)

    def stop(self) -> None:
        self._stop_event.set()

    @property
    def running_count(self) -> int:
        with self._lock:
            return len(self._running)

    @property
    def queued_count(self) -> int:
        return self._queue.qsize()