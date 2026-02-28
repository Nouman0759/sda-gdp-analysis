from typing import Dict, List, Any
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class DashboardWriter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GDP Analysis Dashboard")
        self.root.geometry("1300x850")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvases = {}

    def write(self, results: Dict[str, List[Dict]]) -> None:
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        # 1. Top 10
        if "top_10" in results and results["top_10"]:
            self._create_bar_tab("top_10", results["top_10"], "Top 10 Countries by GDP", "skyblue")

        # 2. Bottom 10
        if "bottom_10" in results and results["bottom_10"]:
            self._create_bar_tab("bottom_10", results["bottom_10"], "Bottom 10 Countries by GDP", "lightcoral")

        # 3. Global Trend
        if "global_trend" in results and results["global_trend"]:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="Global GDP Trend")
            fig = plt.Figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            years = [r["Year"] for r in results["global_trend"]]
            totals = [r["Total GDP"] / 1e12 for r in results["global_trend"]]
            ax.plot(years, totals, marker="o", color="teal")
            ax.set_xlabel("Year")
            ax.set_ylabel("Total GDP (Trillion USD)")
            ax.set_title("Global GDP Trend")
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis="x", rotation=30)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            self.canvases["global_trend"] = canvas

        # 4. Average by Continent
        if "average_continent" in results and results["average_continent"]:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="Avg GDP by Continent")
            fig = plt.Figure(figsize=(10, 6))
            ax = fig.add_subplot(111)
            continents = [r["Continent"] for r in results["average_continent"]]
            avgs = [r["Average GDP"] / 1e12 for r in results["average_continent"]]
            ax.pie(avgs, labels=continents, autopct="%1.1f%%", startangle=90, textprops={'fontsize': 9})
            ax.set_title("Average GDP Share by Continent")
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            self.canvases["average_continent"] = canvas

        # 5. Growth Rates
        if "growth_rates" in results and results["growth_rates"]:
            self._create_growth_tab(results["growth_rates"])

        # 6. Fastest Growing Continent
        if "fastest_continent" in results and results["fastest_continent"]:
            self._create_fastest_cont_tab(results["fastest_continent"])

        # 7. Consistent Decline
        if "consistent_decline" in results and results["consistent_decline"]:
            self._create_decline_tab(results["consistent_decline"])

        # 8. Continent Contribution
        if "continent_contribution" in results and results["continent_contribution"]:
            self._create_contrib_tab(results["continent_contribution"])

    def _create_bar_tab(self, key: str, data: List[Dict], title: str, color: str):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title.split(" ")[0] + " 10")

        fig = plt.Figure(figsize=(12, 7))
        ax = fig.add_subplot(111)

        countries = [r["Country"] for r in data]
        gdps = [r["GDP"] / 1e12 for r in data]

        bars = ax.bar(countries, gdps, color=color, edgecolor="black")

        ax.set_ylabel("GDP (Trillion USD)")
        ax.set_title(title)

        # Improved labels
        short_labels = [c[:35] + "..." if len(c) > 35 else c for c in countries]
        ax.set_xticks(range(len(countries)))
        ax.set_xticklabels(short_labels, rotation=45, ha="right", fontsize=9)

        # Value labels on bars
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.1, f"{h:.2f}", ha="center", va="bottom", fontsize=8)

        ax.grid(True, axis="y", alpha=0.3)
        fig.tight_layout(pad=3.0)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvases[key] = canvas
        # ────────────────────────────────────────────────
    # 3. Growth Rates Tab
    # ────────────────────────────────────────────────
    def _create_growth_tab(self, data: List[Dict]):
        if not data:
            return
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Growth Rates")

        fig = plt.Figure(figsize=(11, 6))
        ax = fig.add_subplot(111)

        for entry in data:
            country = entry["Country"]
            growths = entry["Growths"]
            years = [g["Year"] for g in growths]
            percents = [g["Growth %"] for g in growths]
            ax.plot(years, percents, marker="o", label=country)

        ax.set_xlabel("Year")
        ax.set_ylabel("Growth Rate (%)")
        ax.set_title("GDP Growth Rate - Top Countries")
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvases["growth_rates"] = canvas

    # ────────────────────────────────────────────────
    # 6. Fastest Growing Continent Tab
    # ────────────────────────────────────────────────
    def _create_fastest_cont_tab(self, data: List[Dict]):
        if not data:
            return
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Fastest Continent")

        fig = plt.Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)
        conts = [d["Continent"] for d in data[:5]]
        growths = [d["Avg Annual Growth %"] for d in data[:5]]
        bars = ax.barh(conts, growths, color="seagreen")
        ax.set_xlabel("Avg Annual Growth %")
        ax.set_title("Fastest Growing Continents")
        for bar in bars:
            w = bar.get_width()
            ax.text(w + 0.5, bar.get_y() + bar.get_height()/2, f"{w:.2f}%", va="center")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvases["fastest_continent"] = canvas

    # ────────────────────────────────────────────────
    # 7. Consistent Decline Tab
    # ────────────────────────────────────────────────
    def _create_decline_tab(self, data: List[Dict]):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Consistent Decline")

        fig = plt.Figure(figsize=(12, 7))
        ax = fig.add_subplot(111)

        if not data:
            ax.text(0.5, 0.5, "No countries showed consistent decline", 
                    ha="center", va="center", fontsize=14, color="gray")
            ax.axis("off")
        else:
            # Shorten country names for better spacing
            countries = [d["Country"][:20] + "..." if len(d["Country"]) > 20 else d["Country"] for d in data]
            declines = [d["Avg Decline %"] for d in data]

            # Horizontal bars for negative values (go left from 0)
            bars = ax.barh(countries, declines, color="indianred", edgecolor="black", height=0.7)

            # Zero line for reference
            ax.axvline(0, color="black", linewidth=1, linestyle="--")

            # Set x-limits with padding
            min_decline = min(declines) - 3   # extra space on left
            ax.set_xlim(min_decline, 2)       # small right padding

            ax.set_xlabel("Avg Annual Decline %")
            ax.set_title(f"Countries with Consistent Decline (Last {data[0]['Years']} Years)")

            # Add value labels inside or beside bars
            for bar, val in zip(bars, declines):
                if val < 0:
                    # Inside bar for negative
                    ax.text(val / 2, bar.get_y() + bar.get_height()/2,
                            f"{val:.1f}%", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
                else:
                    # Outside for positive (rare)
                    ax.text(val + 0.5, bar.get_y() + bar.get_height()/2,
                            f"{val:.1f}%", ha="left", va="center", color="black", fontsize=10)

            # Invert y-axis so biggest decline (most negative) at top
            ax.invert_yaxis()

            ax.grid(True, axis="x", alpha=0.3, linestyle="--")

        fig.tight_layout(pad=2.0)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvases["consistent_decline"] = canvas

    # ────────────────────────────────────────────────
    # 8. Continent Contribution Tab (Stacked Area)
    # ────────────────────────────────────────────────
    def _create_contrib_tab(self, data: List[Dict]):
        if not data:
            return
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Continent Contribution")

        fig = plt.Figure(figsize=(11, 6))
        ax = fig.add_subplot(111)

        years = [d["Year"] for d in data]
        conts = sorted(set(c for d in data for c in d["Contributions"]))
        contrib_matrix = []
        for y_data in data:
            row = [y_data["Contributions"].get(c, 0) for c in conts]
            contrib_matrix.append(row)

        # Fix: convert zipped iterator to explicit list of lists
        stacks = [list(col) for col in zip(*contrib_matrix)]

        ax.stackplot(years, stacks, labels=conts)
        ax.set_xlabel("Year")
        ax.set_ylabel("Contribution (%)")
        ax.set_title("Continent Contribution to Global GDP")
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=8)
        ax.grid(True, alpha=0.2)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvases["continent_contribution"] = canvas
    def start(self):
        self.root.mainloop()


class ConsoleWriter:
    def write(self, results: Any) -> None:
        print("\n===== ANALYSIS RESULTS =====")
        if isinstance(results, dict):
            for key, value in results.items():
                print(f"\n--- {key.upper()} ({len(value)} items) ---")
                for item in value[:5]:  # show first few
                    print(item)
        else:
            print(results)
        print("===========================\n")