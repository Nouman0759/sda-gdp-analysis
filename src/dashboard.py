import json
from data_loader import load_gdp_data
from data_processor import process_data
from visualizer import (
    plot_region_gdp,
    plot_year_gdp_line,
)

def show_dashboard():
    try:
        print("Starting dashboard...")
        
        # Load configuration - go up one directory level
        with open("config/config.json", "r") as file:
            config = json.load(file)
        
        print("Config loaded successfully!")
        print("GDP ANALYTICS DASHBOARD")
        print("=======================")
        print(f"Region    : {config.get('region')}")
        print(f"Year      : {config.get('year')}")
        print(f"Operation : {config.get('operation')}")
        print()
        
        # Load GDP data - go up one directory level
        print("Loading GDP data...")
        data = load_gdp_data("data/gdp_with_continent_filled.csv")
        print(f"Loaded {len(data)} records")
        
        # Process data
        print("Processing data...")
        result, filtered_data = process_data(data, config)
        
        print(f"Computed Result: {result}")
        print(f"Filtered records: {len(filtered_data)}")
        print()
        
        # Visualization
        if config.get("output") == "dashboard":
            print("Generating visualizations...")
            plot_region_gdp(filtered_data, config)
            plot_year_gdp_line(filtered_data, config)
            
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
        import traceback
        traceback.print_exc()