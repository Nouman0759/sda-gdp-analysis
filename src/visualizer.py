
import matplotlib.pyplot as plt


def plot_region_gdp(filtered_data, config):
    """
    Bar chart: GDP of countries in a selected region for a specific year
    """
    year = str(config.get("year"))

    if not filtered_data:
        print("No data available for region GDP plot.")
        return

    countries = list(map(lambda x: x["Country Name"], filtered_data))
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


