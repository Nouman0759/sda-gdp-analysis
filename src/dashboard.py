import json
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import Combobox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from data_loader import load_gdp_data
from data_processor import process_data
from visualizer import (
    plot_region_gdp,
    plot_continent_gdp_pie,
    plot_year_gdp_line,
    extract_country_trend,
    _extract_country_and_values
)

# ---------------------------
# Year Pie Chart (for Year tab)
# ---------------------------
def plot_year_gdp_pie(filtered_data, year):
    countries, values = _extract_country_and_values(filtered_data, year)

    fig = plt.Figure(figsize=(8, 8))
    ax = fig.add_subplot(111)

    wedges, texts, autotexts = ax.pie(
        values,
        autopct=lambda p: f"{p:.1f}%" if p > 4 else "",
        startangle=140
    )

    ax.legend(
        wedges,
        countries,
        title="Countries",
        loc="center left",
        bbox_to_anchor=(1, 0.5)
    )

    ax.set_title(f"GDP Share by Country ({year})")
    fig.tight_layout()
    return fig


# ---------------------------
# Main Dashboard
# ---------------------------
def show_dashboard():
    # ---------- LOAD CONFIG & DATA ----------
    with open("config/config.json", "r") as file:
        config = json.load(file)

    data = load_gdp_data("data/gdp_with_continent_filled.csv")
    result, filtered_data = process_data(data, config)

    # ---------- MAIN WINDOW ----------
    root = tk.Tk()
    root.title("GDP Analytics Dashboard")
    root.geometry("1200x800")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    tab_summary = ttk.Frame(notebook)
    tab_region = ttk.Frame(notebook)
    tab_year = ttk.Frame(notebook)

    notebook.add(tab_summary, text="Summary")
    notebook.add(tab_region, text="Region GDP")
    notebook.add(tab_year, text="Year GDP")

    # ---------- COUNTRY + YEAR DROPDOWNS ----------
    country_key = [k for k in data[0].keys() if "Country" in k and "Code" not in k][0]
    country_list = [row[country_key] for row in data]
    all_years = [str(y) for y in range(1960, 2025)]

    selected_country = tk.StringVar(value=country_list[0])
    selected_year = tk.StringVar(value=str(config.get("year")))

    country_dropdown = Combobox(
        tab_summary, textvariable=selected_country,
        values=country_list, state="readonly"
    )
    country_dropdown.pack(padx=20, pady=5, anchor="nw")

    year_dropdown = Combobox(
        tab_summary, textvariable=selected_year,
        values=all_years, state="readonly"
    )
    year_dropdown.pack(padx=20, pady=5, anchor="nw")

    # ---------- COUNTRY STATS ----------
    country_stats_label = tk.Label(
        tab_summary, font=("Consolas", 12), justify="left"
    )
    country_stats_label.pack(padx=20, pady=10, anchor="nw")

    # ---------- COUNTRY TREND LINE ----------
    trend_frame = ttk.Frame(tab_summary)
    trend_frame.pack(fill="both", expand=True, padx=20, pady=10)

    trend_canvas = None

    def update_country_trend():
        nonlocal trend_canvas

        if trend_canvas:
            trend_canvas.get_tk_widget().destroy()

        country_name = selected_country.get()
        country_data = [row for row in data if row[country_key] == country_name]

        years, gdp_values = extract_country_trend(country_data)

        fig = plt.Figure(figsize=(10, 4))
        ax = fig.add_subplot(111)

        ax.plot(years, gdp_values, marker="o")
        ax.set_title(f"{country_name} GDP Trend (1960–2024)")
        ax.set_xlabel("Year")
        ax.set_ylabel("GDP Value")
        ax.tick_params(axis="x", rotation=45)

        fig.tight_layout()

        trend_canvas = FigureCanvasTkAgg(fig, master=trend_frame)
        trend_canvas.draw()
        trend_canvas.get_tk_widget().pack(fill="both", expand=True)

    # ================= REGION TAB =================
    region_frame = ttk.Frame(tab_region)
    region_frame.pack(fill="both", expand=True)

    region_canvas = None
    region_mode = tk.StringVar(value="bar")

    def update_region_chart():
        nonlocal region_canvas

        if region_canvas:
            region_canvas.get_tk_widget().destroy()

        if region_mode.get() == "bar":
            continent = config.get("region")
            region_filtered = filtered_data if continent else data
            fig = plot_region_gdp(
                region_filtered,
                {"year": selected_year.get(), "region": continent}
            )
        else:
            fig = plot_continent_gdp_pie(
                data,
                {"year": selected_year.get()}
            )

        region_canvas = FigureCanvasTkAgg(fig, master=region_frame)
        region_canvas.draw()
        region_canvas.get_tk_widget().pack(fill="both", expand=True)

    ttk.Button(
        tab_region,
        text="Toggle Bar / Pie",
        command=lambda: (
            region_mode.set("pie" if region_mode.get() == "bar" else "bar"),
            update_region_chart()
        )
    ).pack(pady=5)

    # ================= YEAR TAB (SCROLLABLE) =================
    container = ttk.Frame(tab_year)
    container.pack(fill="both", expand=True)

    canvas = tk.Canvas(container)
    scrollbar_x = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    scrollbar_y = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

    canvas.pack(side="top", fill="both", expand=True)
    scrollbar_x.pack(side="bottom", fill="x")
    scrollbar_y.pack(side="right", fill="y")

    year_canvas = None
    year_mode = tk.StringVar(value="line")

    def update_year_chart():
        nonlocal year_canvas

        if year_canvas:
            year_canvas.get_tk_widget().destroy()

        if year_mode.get() == "line":
            fig = plot_year_gdp_line(
                data, {"year": selected_year.get()}
            )
        else:
            fig = plot_year_gdp_pie(
                data, selected_year.get()
            )

        year_canvas = FigureCanvasTkAgg(fig, master=scrollable_frame)
        year_canvas.draw()
        widget = year_canvas.get_tk_widget()
        widget.pack(fill="both", expand=True)

        widget.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    ttk.Button(
        tab_year,
        text="Toggle Bar / Pie",
        command=lambda: (
            year_mode.set("pie" if year_mode.get() == "line" else "line"),
            update_year_chart()
        )
    ).pack(pady=5)

    # ---------- UPDATE STATS ----------
    def update_country_stats(event=None):
        country_name = selected_country.get()
        year = selected_year.get()

        country_data = [row for row in data if row[country_key] == country_name]
        country_values = [
            float(row[year]) for row in country_data
            if row.get(year) not in ("", None)
        ]

        country_sum = sum(country_values)
        country_avg = country_sum / len(country_values) if country_values else 0

        continent = next(
            row.get("Continent") for row in data if row[country_key] == country_name
        )

        region_values = [
            float(row[year]) for row in data
            if row.get("Continent") == continent and row.get(year) not in ("", None)
        ]

        region_avg = sum(region_values) / len(region_values) if region_values else 0

        stats_text = f"""
Selected Country   : {country_name}
Year              : {year}
Sum of GDP        : {country_sum:,.2f}
Average GDP       : {country_avg:,.2f}
Average GDP Region: {region_avg:,.2f}
"""
        country_stats_label.config(text=stats_text)

        update_country_trend()
        update_region_chart()
        update_year_chart()

    country_dropdown.bind("<<ComboboxSelected>>", update_country_stats)
    year_dropdown.bind("<<ComboboxSelected>>", update_country_stats)

    # ---------- INITIAL LOAD ----------
    update_country_stats()
    update_region_chart()
    update_year_chart()

    root.mainloop()


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    show_dashboard()
