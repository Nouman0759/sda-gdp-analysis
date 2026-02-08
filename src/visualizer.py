import matplotlib.pyplot as plt

# -------------------------------------------------
# Helper: extract country names + GDP values
# -------------------------------------------------
def _extract_country_and_values(filtered_data, year):
    country_key = [
        k for k in filtered_data[0].keys()
        if "Country" in k and "Code" not in k
    ][0]

    countries = []
    values = []

    for row in filtered_data:
        name = row.get(country_key)
        value = row.get(year)

        # Skip empty values
        if value in ("", None):
            continue

        # ❌ Remove non-country aggregates
        if name in (
            "World",
            "Arab World",
            "Africa Eastern and Southern",
            "Africa Western and Central",
            "European Union",
            "High income",
            "Low income",
            "Middle income"
        ):
            continue

        countries.append(name)
        values.append(float(value))

    return countries, values


# -------------------------------------------------
# Helper: extract GDP trend for a single country
# -------------------------------------------------
def extract_country_trend(country_data, start_year=1960, end_year=2024):
    years = [str(y) for y in range(start_year, end_year + 1)]
    gdp_values = [
        float(country_data[0].get(y))
        if country_data and country_data[0].get(y) not in ("", None)
        else 0
        for y in years
    ]
    return years, gdp_values


# -------------------------------------------------
# REGION TAB — Country-wise BAR chart
# -------------------------------------------------
def plot_region_gdp(filtered_data, config):
    year = str(config.get("year"))

    countries, raw_values = _extract_country_and_values(filtered_data, year)

    # Convert to Trillions
    values = [v / 1e12 for v in raw_values]

    # Sort DESC
    data = sorted(zip(countries, values), key=lambda x: x[1], reverse=True)

    # Take top 20
    data = data[:20]

    countries, values = zip(*data)

    fig = plt.Figure(figsize=(12, 6))
    ax = fig.add_subplot(111)

    ax.bar(countries, values)
    ax.set_title(f"Top 20 Countries GDP ({year})")
    ax.set_ylabel("GDP (Trillion USD)")
    ax.tick_params(axis="x", rotation=90)

    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    return fig


# -------------------------------------------------
# REGION TAB — Continent-wise PIE chart
# -------------------------------------------------
def plot_continent_gdp_pie(full_data, config):
    year = str(config.get("year"))

    continent_totals = {}
    for row in full_data:
        continent = row.get("Continent")
        value = row.get(year)

        if value in ("", None):
            continue

        continent_totals[continent] = continent_totals.get(continent, 0) + float(value)

    continents = list(continent_totals.keys())
    values = [v / 1e12 for v in continent_totals.values()]

    fig = plt.Figure(figsize=(9, 9))
    ax = fig.add_subplot(111)

    ax.pie(
        values,
        labels=continents,
        autopct=lambda p: f"{p:.1f}%" if p > 4 else "",
        startangle=140
    )

    ax.set_title(f"GDP Share by Continent ({year})")
    fig.tight_layout()
    return fig


# -------------------------------------------------
# YEAR TAB — Country-wise BAR chart (FIXED)
# -------------------------------------------------
def plot_year_gdp_line(filtered_data, config):
    year = str(config.get("year"))

    countries, raw_values = _extract_country_and_values(filtered_data, year)

    # Convert to Trillions
    values = [v / 1e12 for v in raw_values]

    # Sort DESC
    data = sorted(zip(countries, values), key=lambda x: x[1], reverse=True)

    # 🔥 TOP 30 ONLY (KEY FIX)
    data = data[:30]

    countries, values = zip(*data)

    fig = plt.Figure(figsize=(16, 6))
    ax = fig.add_subplot(111)

    ax.bar(countries, values, width=0.8)
    ax.set_title(f"Top 30 Countries by GDP ({year})")
    ax.set_ylabel("GDP (Trillion USD)")
    ax.tick_params(axis="x", rotation=90)

    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.margins(y=0.2)

    fig.tight_layout()
    return fig
