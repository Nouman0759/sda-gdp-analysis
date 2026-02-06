

def filter_data(data, config):
    region = config.get("region")

    filtered = data

    if region:
        filtered = list(
            filter(lambda x: x.get("Continent") == region, filtered)
        )

    return filtered


def extract_year_values(filtered_data, year):
    year = str(year)

    values = list(
        map(
            lambda x: float(x[year]) if x.get(year) not in ("", None) else None,
            filtered_data
        )
    )

    return list(filter(lambda v: v is not None, values))


def compute_result(values, operation):
    if not values:
        return 0

    if operation == "sum":
        return sum(values)

    if operation == "average":
        return sum(values) / len(values)

    raise ValueError("Invalid operation in config")


def process_data(data, config):
    year = config.get("year")
    operation = config.get("operation")

    filtered_data = filter_data(data, config)
    values = extract_year_values(filtered_data, year)

    result = compute_result(values, operation)

    return result, filtered_data
