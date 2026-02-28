import json
import csv
from typing import List, Any
from core.contracts import PipelineService


class JsonReader:
    """
    Reads JSON file and sends raw data to Core.
    """

    def __init__(self, file_path: str, service: PipelineService):
        self.file_path = file_path
        self.service = service

    def run(self) -> None:
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            raise Exception("JSON file not found.")

        # Send raw data to Core
        self.service.execute(data)


class CsvReader:
    """
    Reads CSV file and sends raw data to Core.
    """

    def __init__(self, file_path: str, service: PipelineService):
        self.file_path = file_path
        self.service = service

    def run(self) -> None:
        try:
            with open(self.file_path, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                data = list(reader)
        except FileNotFoundError:
            raise Exception("CSV file not found.")

        # Send raw data to Core
        self.service.execute(data)