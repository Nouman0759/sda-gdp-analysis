"""
inputs.py - Generic CSV Input Module.
"""

import csv
import time
import os
from core.contracts import IInputModule, RawPacket

REQUIRED_INTERNALS = {"entity_name", "time_period", "metric_value", "security_hash"}

TYPE_CASTERS = {
    "string": str,
    "integer": int,
    "float": float,
    "bool": lambda v: v.lower() in ("true", "1", "yes"),
}


def _build_schema(schema_mapping):
    schema = []
    for col in schema_mapping.get("columns", []):
        caster = TYPE_CASTERS.get(col.get("data_type", "string"), str)
        schema.append({
            "source": col["source_name"],
            "internal": col["internal_mapping"],
            "cast": caster,
        })
    return schema


def _map_row(row, schema):
    mapped = {}
    for col_spec in schema:
        raw_val = row.get(col_spec["source"], "")
        try:
            mapped[col_spec["internal"]] = col_spec["cast"](raw_val)
        except (ValueError, TypeError) as e:
            raise ValueError(
                "Cast failed for column '{}' -> '{}': {}".format(
                    col_spec["source"], col_spec["internal"], e
                )
            )
    return mapped


class CSVInputModule(IInputModule):

    def __init__(self, config, telemetry_counters=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        raw_path = config["dataset_path"]
        self._dataset_path = os.path.join(project_root, raw_path)

        print("[Input] Looking for dataset at: {}".format(self._dataset_path))
        print("[Input] File exists: {}".format(os.path.exists(self._dataset_path)))

        self._delay = config["pipeline_dynamics"]["input_delay_seconds"]
        self._schema = _build_schema(config["schema_mapping"])
        self._telemetry_counters = telemetry_counters

    def run(self, raw_queue, stop_event):
        serial = 0
        try:
            with open(self._dataset_path, newline="", encoding="utf-8") as f:
                raw_lines = f.readlines()[:3]
                print("[Input] DEBUG raw first 3 lines:")
                for line in raw_lines:
                    print(repr(line))

            with open(self._dataset_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                print("[Input] DEBUG fieldnames: {}".format(reader.fieldnames))

                row_count = 0
                for row in reader:
                    row_count += 1
                    if row_count <= 2:
                        print("[Input] DEBUG row {}: {}".format(row_count, dict(row)))

                    try:
                        mapped = _map_row(row, self._schema)
                    except ValueError as e:
                        print("[Input] Skipping malformed row: {}".format(e))
                        continue

                    missing = REQUIRED_INTERNALS - mapped.keys()
                    if missing:
                        print("[Input] Row missing required fields {}, skipping.".format(missing))
                        continue

                    extra = {k: v for k, v in mapped.items()
                             if k not in REQUIRED_INTERNALS}

                    packet = RawPacket(
                        serial=serial,
                        entity_name=mapped["entity_name"],
                        time_period=mapped["time_period"],
                        metric_value=mapped["metric_value"],
                        security_hash=mapped["security_hash"],
                        extra_fields=extra,
                    )

                    raw_queue.put(packet)
                    serial += 1

                    # Increment raw queue size counter
                    if self._telemetry_counters is not None:
                        try:
                            self._telemetry_counters['raw_queue_size'] = (
                                self._telemetry_counters.get('raw_queue_size', 0) + 1
                            )
                        except Exception:
                            pass

                    print("[Input] DEBUG sent packet serial={}".format(serial))
                    time.sleep(self._delay)

                    if stop_event.is_set():
                        print("[Input] DEBUG stop_event was set, breaking")
                        break

                print("[Input] DEBUG total rows seen by DictReader: {}".format(row_count))

        except FileNotFoundError:
            print("[Input] ERROR: Dataset not found at '{}'".format(self._dataset_path))
        except Exception as e:
            import traceback
            print("[Input] Unexpected error: {}".format(e))
            traceback.print_exc()
        finally:
            raw_queue.put(None)
            print("[Input] Done. Sent {} packets.".format(serial))