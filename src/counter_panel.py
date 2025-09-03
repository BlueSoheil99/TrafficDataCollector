from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal, QDateTime


class CounterPanel(QWidget):
    count_added = pyqtSignal(dict)

    def __init__(self, config):
        super().__init__()
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Counters"))

        # Very simple: just 2 buttons
        self.car_btn = QPushButton("Car +1")
        self.truck_btn = QPushButton("Truck +1")
        layout.addWidget(self.car_btn)
        layout.addWidget(self.truck_btn)

        self.car_btn.clicked.connect(lambda: self.add_count("Car"))
        self.truck_btn.clicked.connect(lambda: self.add_count("Truck"))

    def add_count(self, vehicle_type):
        record = {
            "time": QDateTime.currentDateTime().toString(),
            "vehicle": vehicle_type,
        }
        self.count_added.emit(record)
