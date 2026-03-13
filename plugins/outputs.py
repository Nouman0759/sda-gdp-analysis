"""
outputs.py - Real-Time Dashboard
"""

import threading
import matplotlib.pyplot as plt
from collections import deque

from core.contracts import IOutputModule, ITelemetryObserver, ProcessedPacket


def _queue_color(size, max_size):
    if max_size == 0:
        return "green"
    ratio = size / max_size
    if ratio < 0.4:
        return "green"
    elif ratio < 0.75:
        return "orange"
    else:
        return "red"


def _queue_label(size, max_size):
    if max_size == 0:
        return "Unknown"
    ratio = size / max_size
    if ratio < 0.4:
        return "Flowing"
    elif ratio < 0.75:
        return "Filling"
    else:
        return "Backpressure"


class Dashboard(IOutputModule, ITelemetryObserver):

    def __init__(self, config):
        viz = config.get("visualizations", {})
        self._telemetry_cfg = viz.get("telemetry", {})
        self._chart_cfgs = viz.get("data_charts", [])
        self._max_points = 200

        self._x_values = deque(maxlen=self._max_points)
        self._y_metric = deque(maxlen=self._max_points)
        self._y_average = deque(maxlen=self._max_points)

        self._snapshot = {}
        self._snap_lock = threading.Lock()
        self._pipeline_done = False

        self._line_cfg = {}
        self._avg_cfg = {}
        for c in self._chart_cfgs:
            if c["type"] == "real_time_line_graph_values":
                self._line_cfg = c
            elif c["type"] == "real_time_line_graph_average":
                self._avg_cfg = c

    def on_telemetry_update(self, snapshot):
        with self._snap_lock:
            self._snapshot = snapshot

    def _consume(self, processed_queue, stop_event):
        while True:
            try:
                item = processed_queue.get(timeout=1.0)
            except Exception:
                # Keep trying even if stop_event is set
                # until we get the None sentinel
                if self._pipeline_done:
                    break
                continue

            if item is None:
                self._pipeline_done = True
                print("[Dashboard] All packets received. Window stays open until you close it.")
                break

            packet = item
            self._x_values.append(packet.time_period)
            self._y_metric.append(packet.metric_value)
            if packet.computed_metric is not None:
                self._y_average.append(packet.computed_metric)

    def run(self, processed_queue, telemetry, stop_event):
        telemetry.subscribe(self)

        consumer_thread = threading.Thread(
            target=self._consume,
            args=(processed_queue, stop_event),
            daemon=True,
        )
        consumer_thread.start()

        show_raw = self._telemetry_cfg.get("show_raw_stream", True)
        show_proc = self._telemetry_cfg.get("show_processed_stream", True)
        n_telem = sum([show_raw, show_proc])
        n_charts = len(self._chart_cfgs)
        total_rows = n_telem + n_charts

        plt.ion()
        fig, axes_list = plt.subplots(total_rows, 1, figsize=(13, 3 * total_rows))
        fig.patch.set_facecolor("#1e1e2e")
        fig.suptitle("Pipeline Real-Time Dashboard", color="white",
                     fontsize=14, fontweight="bold")

        if total_rows == 1:
            axes_list = [axes_list]

        for ax in axes_list:
            ax.set_facecolor("#2a2a3e")
            ax.tick_params(colors="white")
            for spine in ax.spines.values():
                spine.set_edgecolor("#555577")

        telem_axes = {}
        chart_axes = []
        row = 0

        if show_raw:
            telem_axes["raw"] = axes_list[row]
            row += 1
        if show_proc:
            telem_axes["proc"] = axes_list[row]
            row += 1
        for i in range(n_charts):
            chart_axes.append(axes_list[row + i])

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show(block=False)

        print("[Dashboard] Window opened. Close it with the X button when done.")

        # Keep looping forever until user closes the window
        while plt.fignum_exists(fig.number):

            with self._snap_lock:
                snap = dict(self._snapshot)

            # Raw queue bar
            if "raw" in telem_axes:
                ax = telem_axes["raw"]
                ax.cla()
                ax.set_facecolor("#2a2a3e")
                rqs = snap.get("raw_queue_size", 0)
                rqm = snap.get("raw_queue_max", 1) or 1
                color = _queue_color(rqs, rqm)
                label = _queue_label(rqs, rqm)
                ax.barh(0, rqs, color=color, height=0.4)
                ax.set_xlim(0, rqm)
                ax.set_yticks([])
                ax.set_xlabel("Queue depth", color="white", fontsize=8)
                ax.set_title(
                    "Raw Stream Queue  [{}/{}]  - {}".format(rqs, rqm, label),
                    color=color, fontsize=9, fontweight="bold"
                )
                ax.tick_params(colors="white")
                ax.set_facecolor("#2a2a3e")

            # Processed queue bar
            if "proc" in telem_axes:
                ax = telem_axes["proc"]
                ax.cla()
                ax.set_facecolor("#2a2a3e")
                pqs = snap.get("processed_queue_size", 0)
                pqm = snap.get("processed_queue_max", 1) or 1
                color = _queue_color(pqs, pqm)
                label = _queue_label(pqs, pqm)
                ax.barh(0, pqs, color=color, height=0.4)
                ax.set_xlim(0, pqm)
                ax.set_yticks([])
                ax.set_xlabel("Queue depth", color="white", fontsize=8)
                ax.set_title(
                    "Processed Stream Queue  [{}/{}]  - {}".format(pqs, pqm, label),
                    color=color, fontsize=9, fontweight="bold"
                )
                ax.tick_params(colors="white")
                ax.set_facecolor("#2a2a3e")
                v = snap.get("packets_verified", 0)
                d = snap.get("packets_dropped", 0)
                a = snap.get("packets_averaged", 0)
                ax.text(
                    0.99, 0.95,
                    "Verified: {}   Dropped: {}   Averaged: {}".format(v, d, a),
                    transform=ax.transAxes, color="white",
                    fontsize=7.5, ha="right", va="top"
                )

            # Live sensor values line chart
            if len(chart_axes) > 0 and self._line_cfg:
                ax = chart_axes[0]
                ax.cla()
                ax.set_facecolor("#2a2a3e")
                xs = list(self._x_values)
                ys = list(self._y_metric)
                if xs and ys:
                    ax.plot(xs, ys, color="#00d4ff", linewidth=1.5,
                            marker="o", markersize=3, label="Sensor Value")
                ax.set_title(self._line_cfg.get("title", "Live Sensor Values"),
                             color="white", fontsize=10)
                ax.set_xlabel(self._line_cfg.get("x_axis", "time_period"),
                              color="white", fontsize=8)
                ax.set_ylabel(self._line_cfg.get("y_axis", "metric_value"),
                              color="white", fontsize=8)
                ax.tick_params(colors="white")
                ax.set_facecolor("#2a2a3e")
                ax.grid(True, color="#444466", linewidth=0.5, linestyle="--")
                if xs and ys:
                    ax.legend(facecolor="#1e1e2e", labelcolor="white", fontsize=8)

            # Running average line chart
            if len(chart_axes) > 1 and self._avg_cfg:
                ax = chart_axes[1]
                ax.cla()
                ax.set_facecolor("#2a2a3e")
                xs = list(self._x_values)
                ya = list(self._y_average)
                if xs and ya:
                    ax.plot(xs[-len(ya):], ya, color="#ff9f43", linewidth=2.0,
                            marker="o", markersize=3, label="Running Average")
                ax.set_title(self._avg_cfg.get("title", "Running Average"),
                             color="white", fontsize=10)
                ax.set_xlabel(self._avg_cfg.get("x_axis", "time_period"),
                              color="white", fontsize=8)
                ax.set_ylabel(self._avg_cfg.get("y_axis", "computed_metric"),
                              color="white", fontsize=8)
                ax.tick_params(colors="white")
                ax.set_facecolor("#2a2a3e")
                ax.grid(True, color="#444466", linewidth=0.5, linestyle="--")
                if xs and ya:
                    ax.legend(facecolor="#1e1e2e", labelcolor="white", fontsize=8)

            try:
                plt.tight_layout(rect=[0, 0, 1, 0.96])
                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.5)
            except Exception:
                break

        print("[Dashboard] Window closed by user.")
        stop_event.set()
        consumer_thread.join(timeout=2)