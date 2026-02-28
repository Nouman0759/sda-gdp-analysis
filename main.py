import json
from core.engine import TransformationEngine
from plugins.inputs import CsvReader, JsonReader
from plugins.outputs import ConsoleWriter, DashboardWriter

INPUT_DRIVERS = {
    "csv": CsvReader,
    "json": JsonReader
}

OUTPUT_DRIVERS = {
    "console": ConsoleWriter,
    "dashboard": DashboardWriter
}

def bootstrap():
    with open("config.json", "r") as file:
        config = json.load(file)

    output_type = config["output"]["type"]
    sink_class = OUTPUT_DRIVERS[output_type]
    sink = sink_class()

    engine = TransformationEngine(sink)
    engine.config = config  # temporary - later pass params explicitly

    input_type = config["input"]["type"]
    input_path = config["input"]["file_path"]
    reader_class = INPUT_DRIVERS[input_type]
    reader = reader_class(input_path, engine)

    reader.run()

    if output_type == "dashboard":
        sink.start()


if __name__ == "__main__":
    print("=" * 50)
    print("GDP ANALYSIS SYSTEM STARTED")
    print("=" * 50)
    bootstrap()
    print("=" * 50)
    print("GDP ANALYSIS SYSTEM FINISHED")
    print("=" * 50)