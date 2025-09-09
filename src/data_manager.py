from src.intersection_config import IntersectionConfig


class DataManager:
    def __init__(self, config:IntersectionConfig, counter_panel):
        self.records = []

    def add_record(self, record):
        print("Record added:", record)
        self.records.append(record)

    def save_file(self):
        pass
