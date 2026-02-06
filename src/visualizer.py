


import matplotlib.pyplot as plt


def plot_region_gdp(filtered_data, config):
    """
    Bar chart: GDP of countries in a selected region for a specific year
    """
    year = str(config.get("year"))

    if not filtered_data:
        print("No data available for region GDP plot.")
        return


    country_key = [k for k in filtered_data[0].keys() if "Country" in k and "Code" not in k][0]

    countries = list(map(lambda x: x[country_key], filtered_data))
    values = list(
        map(
            lambda x: float(x[year]) if x.get(year) not in ("", None) else 0,
            filtered_data
        )
    )

    plt.figure(figsize=(10, 6))
    plt.bar(countries, values)
    plt.title(f"Region-wise GDP ({config.get('region')} - {year})")
    plt.xlabel("Country")
    plt.ylabel("GDP Value")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


def plot_year_gdp_line(filtered_data, config):
    """
    Line graph: GDP comparison of countries for a given year
    """
    year = str(config.get("year"))

    if not filtered_data:
        print("No data available for year GDP line plot.")
        return

    country_key = [k for k in filtered_data[0].keys() if "Country" in k and "Code" not in k][0]

    countries = list(map(lambda x: x[country_key], filtered_data))
    values = list(
        map(
            lambda x: float(x[year]) if x.get(year) not in ("", None) else 0,
            filtered_data
        )
    )

    plt.figure(figsize=(10, 6))
    plt.plot(countries, values, marker='o')
    plt.title(f"Year-specific GDP ({year})")
    plt.xlabel("Country")
    plt.ylabel("GDP Value")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


