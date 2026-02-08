import csv

def load_gdp_data(file_path):
    try:
        with open(file_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        raise Exception("GDP data file not found.")

