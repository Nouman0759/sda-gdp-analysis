"""
engine.py - Core processing engine.

Functional Core  : pure functions (signature verification, sliding window)
Imperative Shell : CoreWorker process, Aggregator process
"""

import hashlib
import heapq
import time
from collections import deque
from typing import List, Tuple, Optional

from core.contracts import RawPacket, ProcessedPacket


# ══════════════════════════════════════════════
#  FUNCTIONAL CORE  (pure, stateless functions)
# ══════════════════════════════════════════════

def compute_signature(metric_value, secret_key, iterations=100000):
    msg = str(metric_value).encode()
    key = secret_key.encode()
    dk = hashlib.pbkdf2_hmac("sha256", msg, key, iterations)
    return dk.hex()


def verify_packet(packet, secret_key, iterations=100000):
    expected = compute_signature(packet.metric_value, secret_key, iterations)
    return expected == packet.security_hash


def sliding_window_average(window, new_value, window_size):
    new_window = deque(window, maxlen=window_size)
    new_window.append(new_value)
    avg = sum(new_window) / len(new_window)
    return new_window, avg


# ══════════════════════════════════════════════
#  IMPERATIVE SHELL - Core Worker
# ══════════════════════════════════════════════

class CoreWorker:

    def __init__(self, worker_id, config):
        self.worker_id = worker_id
        proc_cfg = config.get("processing", {})
        stateless = proc_cfg.get("stateless_tasks", {})
        self.secret_key = stateless.get("secret_key", "")
        self.iterations = stateless.get("iterations", 100000)

    def run(self, raw_queue, intermediate_queue, telemetry_counters, stop_event):
        while not stop_event.is_set():
            try:
                packet = raw_queue.get(timeout=1.0)
            except Exception:
                continue

            if packet is None:
                raw_queue.put(None)
                break

            # Decrement raw queue size counter
            try:
                telemetry_counters['raw_queue_size'] = max(
                    0, telemetry_counters.get('raw_queue_size', 0) - 1
                )
            except Exception:
                pass

            # Functional Core call
            is_valid = verify_packet(packet, self.secret_key, self.iterations)

            if is_valid:
                proc = ProcessedPacket(
                    serial=packet.serial,
                    entity_name=packet.entity_name,
                    time_period=packet.time_period,
                    metric_value=packet.metric_value,
                    verified=True,
                )
                intermediate_queue.put((packet.serial, proc))

                # Increment processed queue size counter
                try:
                    telemetry_counters['processed_queue_size'] = (
                        telemetry_counters.get('processed_queue_size', 0) + 1
                    )
                except Exception:
                    pass

                try:
                    telemetry_counters['verified'] += 1
                except Exception:
                    pass

                time.sleep(0.3)  # slow down so telemetry bars are visible

            else:
                try:
                    telemetry_counters['dropped'] += 1
                except Exception:
                    pass


# ══════════════════════════════════════════════
#  IMPERATIVE SHELL - Aggregator
# ══════════════════════════════════════════════

class Aggregator:

    def __init__(self, config, num_workers):
        stateful = config.get("processing", {}).get("stateful_tasks", {})
        self.window_size = stateful.get("running_average_window_size", 10)
        self.num_workers = num_workers

    def run(self, intermediate_queue, processed_queue,
            telemetry_counters, stop_event, total_packets_event,
            total_packets_value):

        heap = []
        next_serial = 0
        window = deque(maxlen=self.window_size)
        finished_workers = 0

        while True:
            try:
                item = intermediate_queue.get(timeout=1.0)
            except Exception:
                if stop_event.is_set():
                    break
                continue

            if item is None:
                finished_workers += 1
                if finished_workers >= self.num_workers:
                    break
                continue

            serial, packet = item

            # Decrement processed queue size counter
            try:
                telemetry_counters['processed_queue_size'] = max(
                    0, telemetry_counters.get('processed_queue_size', 0) - 1
                )
            except Exception:
                pass

            heapq.heappush(heap, (serial, packet))

            while heap and heap[0][0] == next_serial:
                _, ordered_packet = heapq.heappop(heap)

                # Functional Core call
                window, avg = sliding_window_average(
                    window, ordered_packet.metric_value, self.window_size
                )

                ordered_packet.computed_metric = avg
                processed_queue.put(ordered_packet)
                next_serial += 1

                try:
                    telemetry_counters['averaged'] += 1
                except Exception:
                    pass

        # Drain remaining
        while heap:
            _, ordered_packet = heapq.heappop(heap)
            window, avg = sliding_window_average(
                window, ordered_packet.metric_value, self.window_size
            )
            ordered_packet.computed_metric = avg
            processed_queue.put(ordered_packet)
            try:
                telemetry_counters['averaged'] += 1
            except Exception:
                pass

        processed_queue.put(None)