# SDA Project – Phase 1

## Functional & Data-Driven GDP Analysis

---

## Project Description

This project implements a **GDP analysis system** using **Python functional programming principles**.
It analyzes **World Bank GDP data** and produces **statistical results and visual dashboards** based entirely on a **configuration file**, without using hardcoded values.

The system follows the **Single Responsibility Principle (SRP)** by separating data loading, processing, visualization, and orchestration into distinct modules.

---

## Objectives

* Use **functional programming** (`map`, `filter`, `lambda`)
* Enforce **configuration-driven behavior**
* Apply **Single Responsibility Principle**
* Compute GDP statistics (average, sum)
* Generate multiple **data visualizations**
* Maintain proper **GitHub version control**

---

## Technologies Used

* Python
* Matplotlib
* CSV Data Processing
* Git & GitHub

---

## Project Structure

```
sda-gdp-analysis/
│
├── data/
│   └── gdp_data.csv
│
├── config/
│   └── config.json
│
├── src/
│   ├── data_loader.py
│   ├── data_processor.py
│   ├── visualizer.py
│   ├── dashboard.py
│   ├── main.py
│
├── README.md
```

---

## Configuration File

All filtering and computation logic is controlled using `config/config.json`.

### Example:

```json
{
  "region": "South Asia",
  "year": 2020,
  "operation": "average",
  "output": "dashboard"
}
```

✔ No region, year, or operation is hardcoded in source code.

---

## Functional Programming Usage

The project uses:

* `map`
* `filter`
* `lambda` functions

These are mainly applied in **data processing** and **visualization** modules.

---

## Module Responsibilities

### Data Loader

* Loads GDP data from CSV files

### Data Processor

* Cleans data
* Filters by region, year, and country
* Computes statistical results

### Visualizer

* Generates:

  * Bar chart (Region-wise GDP)
  * Line chart (Year-specific GDP)
  * Pie chart (GDP distribution)

### Dashboard

* Reads configuration
* Coordinates all modules
* Displays results and charts
* Handles errors

### Main

* Entry point of the application
* Starts the dashboard

---

## Visualizations

* Region-wise GDP (Bar Chart)
* Year-specific GDP (Line Chart)
* GDP Distribution (Pie Chart)

All charts include proper titles and labels.

---

## ⚠️ Error Handling

* Missing CSV files
* Invalid configuration values
* Empty filtered datasets

Errors are shown as clear messages in the dashboard.

---

## How to Run

1. Install dependency:

```bash
pip install matplotlib
```

2. Run the project:

```bash
python src/main.py
```

3. Modify `config.json` to analyze different regions or years.


## Team Members

* **Muhammad Nouman Malik**
* **Abdullah Nawaz**

## Key Features

* Fully configuration-driven
* Functional programming based
* SRP-compliant architecture
* Dashboard-style output
* Incremental GitHub commits

