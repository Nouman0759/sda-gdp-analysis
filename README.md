
## 10. `readme.txt`
```
============================================================
  Generic Concurrent Real-Time Pipeline — Phase 3
  SDA Spring 2026
============================================================

MAIN FILE
---------
  main.py   ← Run this file to start the pipeline

HOW TO RUN
----------
  1. Place your CSV dataset in the data/ folder.
  2. Edit config.json to point to your dataset and map your columns.
  3. Install dependencies:
       pip install matplotlib
  4. Run:
       python main.py

FILE STRUCTURE
--------------
  main.py               ← Central orchestrator (start here)
  config.json           ← Drives everything: schema, keys, parallelism
  readme.txt            ← This file

  core/
    __init__.py
    contracts.py        ← Abstract types: RawPacket, ProcessedPacket, interfaces
    engine.py           ← Functional Core (pure fns) + Imperative Shell (workers)
    telemetry.py        ← Observer Pattern: PipelineTelemetry subject

  plugins/
    __init__.py
    inputs.py           ← Generic CSV reader (schema-driven, fully generic)
    outputs.py          ← Matplotlib dashboard (Observer + IOutputModule)

  data/
    climate_data.csv    ← Place your dataset here

CONFIG.JSON KEYS
----------------
  dataset_path                            → path to CSV (relative to main.py)
  pipeline_dynamics.input_delay_seconds   → throttle input speed
  pipeline_dynamics.core_parallelism      → number of parallel Core workers
  pipeline_dynamics.stream_queue_max_size → bounded queue capacity
  schema_mapping.columns                  → map CSV headers → internal fields
    source_name       → exact CSV column header
    internal_mapping  → one of: entity_name, time_period,
                                metric_value, security_hash
    data_type         → string | integer | float | bool
  processing.stateless_tasks.secret_key        → PBKDF2 secret key
  processing.stateless_tasks.iterations        → hash iterations (default 100000)
  processing.stateful_tasks.running_average_window_size → sliding window size
  visualizations.telemetry    → toggle queue health bars
  visualizations.data_charts  → configure live chart titles and axes

FOR UNSEEN DATASETS
-------------------
  Only change config.json:
    1. Update "dataset_path" to point to your new CSV.
    2. Update "schema_mapping.columns" to match new column headers.
    3. Update "secret_key" if provided by the evaluator.
  Zero code changes needed.

ARCHITECTURE
------------
  Producer-Consumer : Input → Raw Queue → Core Workers → Intermediate Queue
                      → Aggregator → Processed Queue → Dashboard
  Scatter-Gather    : N workers in parallel; Aggregator resequences via
                      min-heap by serial number before averaging
  Functional Core   : compute_signature(), verify_packet(),
                      sliding_window_average() are pure functions
  Imperative Shell  : CoreWorker and Aggregator handle all I/O and state
  Observer Pattern  : PipelineTelemetry (Subject) notifies Dashboard (Observer)
  Backpressure      : bounded Queue.put() blocks Input when Core is slow
  Telemetry Colors  : Green (<40% full), Orange (40–75%), Red (>75%)

DEPENDENCIES
------------
  Python 3.9+
  matplotlib   (pip install matplotlib)
  Standard library only otherwise.
============================================================