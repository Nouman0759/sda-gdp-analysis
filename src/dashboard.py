import json 
from data_loader import load_gdp_data
from data_processor import cleandata,filterdata,statistics
from visualizer import region,year

def dashboard():
    try:
        # Load Configuration
        with open("config/config.json","r") as file:
            config=json.load(file)
        print("GDP ANALYTICS DASHBOARD")
        print("________________________")
        print(f"Region    : {config.get('region')}")
        print(f"Year      : {config.get('year')}")
        print(f"Operation : {config.get('operation')}")
        print()
        # Load and Process Data
        rawdata=load_gdp_data("data/gdp_data.csv")
        cleaned=cleandata(rawdata)

        filtered=filterdata (
            cleaned,
            region=config.get("region"),
            year=config.get("year"),
            country=config.get("country")
        )
        # Compute result
        result = statistics(filtered, config.get("operation"))

        print(f"Computed Result: {result}")

        # Visualization (controlled by config)
        if config.get("output") == "dashboard":
            region(filtered)   
            year(filtered)

    except FileNotFoundError:
        print("Required file not found. Please check data or config files.")
    except Exception as e:
        print(f"Error: {e}")

