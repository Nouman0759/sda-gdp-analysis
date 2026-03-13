"""
main.py - Central Orchestrator
"""

import json
import multiprocessing
import os
import sys
import time

from core.engine import CoreWorker, Aggregator
from core.telemetry import PipelineTelemetry
from plugins.inputs import CSVInputModule
from plugins.outputs import Dashboard


def _run_input(config, raw_queue, stop_event, telemetry_counters):
    module = CSVInputModule(config, telemetry_counters)
    module.run(raw_queue, stop_event)


def _run_core_worker(worker_id, config, raw_queue, intermediate_queue,
                     telemetry_counters, stop_event):
    worker = CoreWorker(worker_id, config)
    worker.run(raw_queue, intermediate_queue, telemetry_counters, stop_event)
    intermediate_queue.put(None)


def _run_aggregator(config, num_workers, intermediate_queue, processed_queue,
                    telemetry_counters, stop_event):
    agg = Aggregator(config, num_workers)
    agg.run(intermediate_queue, processed_queue,
            telemetry_counters, stop_event, None, None)


def main():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if not os.path.exists(config_path):
        print("[Main] ERROR: config.json not found at {}".format(config_path))
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    dynamics = config["pipeline_dynamics"]
    max_queue_size = dynamics["stream_queue_max_size"]
    num_workers = dynamics["core_parallelism"]

    print("[Main] Config loaded. Workers={}, QueueMax={}".format(num_workers, max_queue_size))

    manager = multiprocessing.Manager()
    telemetry_counters = manager.dict({
        "verified": 0,
        "dropped": 0,
        "averaged": 0,
        "raw_queue_size": 0,
        "processed_queue_size": 0,
    })

    raw_queue = multiprocessing.Queue(maxsize=max_queue_size)
    intermediate_queue = multiprocessing.Queue(maxsize=max_queue_size * num_workers)
    processed_queue = multiprocessing.Queue(maxsize=max_queue_size)
    stop_event = multiprocessing.Event()

    telemetry = PipelineTelemetry(
        raw_queue=raw_queue,
        processed_queue=processed_queue,
        max_size=max_queue_size,
        poll_interval=0.3,
    )

    def _patched_poll():
        while telemetry._running:
            telemetry.snapshot = {
                "raw_queue_size": telemetry_counters.get("raw_queue_size", 0),
                "raw_queue_max": max_queue_size,
                "processed_queue_size": telemetry_counters.get("processed_queue_size", 0),
                "processed_queue_max": max_queue_size,
                "packets_verified": telemetry_counters.get("verified", 0),
                "packets_dropped": telemetry_counters.get("dropped", 0),
                "packets_averaged": telemetry_counters.get("averaged", 0),
            }
            telemetry._notify()
            time.sleep(telemetry._poll_interval)

    telemetry._poll_loop = _patched_poll
    telemetry.start()

    input_proc = multiprocessing.Process(
        target=_run_input,
        args=(config, raw_queue, stop_event, telemetry_counters),
        name="InputProducer", daemon=True,
    )

    worker_procs = [
        multiprocessing.Process(
            target=_run_core_worker,
            args=(wid, config, raw_queue, intermediate_queue,
                  telemetry_counters, stop_event),
            name="CoreWorker-{}".format(wid), daemon=True,
        )
        for wid in range(num_workers)
    ]

    agg_proc = multiprocessing.Process(
        target=_run_aggregator,
        args=(config, num_workers, intermediate_queue, processed_queue,
              telemetry_counters, stop_event),
        name="Aggregator", daemon=True,
    )

    print("[Main] Starting pipeline processes...")
    input_proc.start()
    for p in worker_procs:
        p.start()
    agg_proc.start()

    time.sleep(2)

    print("[Main] All processes running. Launching dashboard (close window to stop).")

    dashboard = Dashboard(config)
    try:
        dashboard.run(processed_queue, telemetry, stop_event)
    except KeyboardInterrupt:
        print("\n[Main] Shutting down...")
    finally:
        stop_event.set()
        telemetry.stop()
        input_proc.join(timeout=3)
        for p in worker_procs:
            p.join(timeout=3)
        agg_proc.join(timeout=3)
        for p in [input_proc, *worker_procs, agg_proc]:
            if p.is_alive():
                p.terminate()
        manager.shutdown()
        print("[Main] Pipeline shutdown complete.")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()