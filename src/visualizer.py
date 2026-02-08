import matplotlib.pyplot as plt

# -------------------------------------------------
# Helper: extract country names + GDP values for a specific year
# -------------------------------------------------
def _extract_country_and_values(filtered_data, year):
    country_key = [k for k in filtered_data[0].keys() if "Country" in k and "Code" not in k][0]

    countries = [row[country_key] for row in filtered_data]
    values = [
        float(row.get(year)) if row.get(year) not in ("", None) else 0
        for row in filtered_data
    ]

    return countries, values


# -------------------------------------------------
# Helper: extract all years GDP for a single country
# -------------------------------------------------
def extract_country_trend(country_data, start_year=1960, end_year=2024):
    """
    Returns two lists: years and GDP values for a single country.
    """
    years = [str(y) for y in range(start_year, end_year + 1)]
    gdp_values = [
        float(country_data[0].get(y, 0)) if country_data and country_data[0].get(y) not in ("", None) else 0
        for y in years
    ]
    return years, gdp_values


# -------------------------------------------------
# REGION TAB — Country-wise BAR chart
# -------------------------------------------------
def plot_region_gdp(filtered_data, config):
    year = str(config.get("year"))

    if not filtered_data:
        return None

    countries, values = _extract_country_and_values(filtered_data, year)

    fig = plt.Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    ax.bar(countries, values)
    ax.set_title(f"Country-wise GDP ({config.get('region')} - {year})")
    ax.set_xlabel("Country")
    ax.set_ylabel("GDP Value")
    ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    return fig


# -------------------------------------------------
# REGION TAB — Continent-wise PIE chart
# -------------------------------------------------
def plot_continent_gdp_pie(full_data, config):
    year = str(config.get("year"))

    # Aggregate by continent
    continent_totals = {}
    for row in full_data:
        continent = row.get("Continent")
        value = float(row.get(year)) if row.get(year) not in ("", None) else 0
        if continent:
            continent_totals[continent] = continent_totals.get(continent, 0) + value

    continents = list(continent_totals.keys())
    values = list(continent_totals.values())

    fig = plt.Figure(figsize=(10, 10))
    ax = fig.add_subplot(111)

    wedges, texts, autotexts = ax.pie(
        values,
        autopct=lambda p: f"{p:.1f}%" if p > 4 else "",
        startangle=140
    )

    ax.legend(
        wedges,
        continents,
        title="Continents",
        loc="center left",
        bbox_to_anchor=(1, 0.5)
    )

    ax.set_title(f"GDP Share by Continent ({year})")
    fig.tight_layout()
    return fig


# -------------------------------------------------
# YEAR TAB — Country-wise LINE chart
# -------------------------------------------------
def plot_year_gdp_line(filtered_data, config):
    year = str(config.get("year"))

    if not filtered_data:
        return None

    countries, values = _extract_country_and_values(filtered_data, year)

    fig = plt.Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    ax.plot(countries, values, marker="o")
    ax.set_title(f"Country-wise GDP Trend ({year})")
    ax.set_xlabel("Country")
    ax.set_ylabel("GDP Value")
    ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    return fig
