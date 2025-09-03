class DataManager:
    def __init__(self):
        self.records = []

    def add_record(self, record):
        print("Record added:", record)
        self.records.append(record)
