"""
telemetry.py - Observer Pattern implementation for real-time pipeline telemetry.

Subject  : PipelineTelemetry  (polls queue sizes, notifies observers)
Observers: Any object implementing ITelemetryObserver (e.g. the dashboard)
"""

import time
import threading
from typing import List
from multiprocessing import Queue

from core.contracts import ITelemetryObserver


# 
#  Subject
#

class PipelineTelemetry:
    """
    Polls raw_queue and processed_queue sizes at a fixed interval and
    broadcasts snapshots to all registered observers.
    Runs in its own daemon thread so it never blocks the pipeline.
    """

    def __init__(self, raw_queue: Queue, processed_queue: Queue,
                 max_size: int, poll_interval: float = 0.25):
        self._raw_queue = raw_queue
        self._processed_queue = processed_queue
        self._max_size = max_size
        self._poll_interval = poll_interval
        self._observers: List[ITelemetryObserver] = []
        self._thread: threading.Thread = None
        self._running = False

        # Latest snapshot (observers may read this directly too)
        self.snapshot: dict = {
            "raw_queue_size": 0,
            "raw_queue_max": max_size,
            "processed_queue_size": 0,
            "processed_queue_max": max_size,
            "packets_verified": 0,
            "packets_dropped": 0,
            "packets_averaged": 0,
        }

        # Counters updated externally by workers via thread-safe increments
        self._verified = 0
        self._dropped = 0
        self._averaged = 0
        self._lock = threading.Lock()

    # Observer management 

    def subscribe(self, observer: ITelemetryObserver) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: ITelemetryObserver) -> None:
        self._observers.remove(observer)

    def _notify(self) -> None:
        for obs in self._observers:
            try:
                obs.on_telemetry_update(self.snapshot.copy())
            except Exception:
                pass

    #  Counter helpers (called by workers)

    def increment_verified(self):
        with self._lock:
            self._verified += 1

    def increment_dropped(self):
        with self._lock:
            self._dropped += 1

    def increment_averaged(self):
        with self._lock:
            self._averaged += 1

    #  Polling loop 

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _poll_loop(self) -> None:
        while self._running:
            try:
                rq = self._raw_queue.qsize()
            except NotImplementedError:
                rq = 0
            try:
                pq = self._processed_queue.qsize()
            except NotImplementedError:
                pq = 0

            with self._lock:
                v, d, a = self._verified, self._dropped, self._averaged

            self.snapshot = {
                "raw_queue_size": rq,
                "raw_queue_max": self._max_size,
                "processed_queue_size": pq,
                "processed_queue_max": self._max_size,
                "packets_verified": v,
                "packets_dropped": d,
                "packets_averaged": a,
            }
            self._notify()
            time.sleep(self._poll_interval)