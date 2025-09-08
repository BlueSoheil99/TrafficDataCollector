# from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox
# from PyQt6.QtCore import pyqtSignal, QDateTime
#
# from src.intersection_config import IntersectionConfig
#
#
# class CounterPanel(QWidget):
#     count_added = pyqtSignal(dict)
#
#     def __init__(self, config:IntersectionConfig):
#         super().__init__()
#         layout = QVBoxLayout(self)
#
#         layout.addWidget(QLabel("Count Panel"))
#
#         # --- Dropdown menu ---
#         layout.addWidget(QLabel("Select approach:"))
#         self.selected_approach = QComboBox()
#         self.selected_approach.addItems(config.approaches)
#         layout.addWidget(self.selected_approach)
#
#         # Very simple: just 2 buttons
#         self.car_btn = QPushButton("Car +1")
#         self.truck_btn = QPushButton("Truck +1")
#         layout.addWidget(self.car_btn)
#         layout.addWidget(self.truck_btn)
#
#         self.car_btn.clicked.connect(lambda: self.add_count("Car"))
#         self.truck_btn.clicked.connect(lambda: self.add_count("Truck"))
#
#     def add_count(self, vehicle_type):
#         record = {
#             "time": QDateTime.currentDateTime().toString(),
#             "vehicle": vehicle_type,
#         }
#         self.count_added.emit(record)


from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt

from src.intersection_config import IntersectionConfig


#
# class CounterPanel(QWidget):
#     def __init__(self, config):
#         super().__init__()
#         self.layout = QVBoxLayout(self)
#
#         # Dropdown to select approach
#         self.layout.addWidget(QLabel("Select Approach:"))
#         self.approach_select = QComboBox()
#         self.approach_select.addItems(config.approaches)
#         self.layout.addWidget(self.approach_select)
#
#         # Table widget
#         self.table = QTableWidget()
#         self.layout.addWidget(self.table)
#
#         # Define rows and columns
#         self.rows = ['car', 'bus', 'truck', 'bike']
#         self.columns = ['through', 'left', 'right']
#
#         # Store tables and memory for each approach
#         self.tables_data = {}
#         self.memory = {}
#         for approach in config.approaches:
#             self.tables_data[approach] = self.create_table()
#             self.memory[approach] = self.create_memory()
#
#         # Show first approach table
#         self.current_approach = config.approaches[0]
#         self.show_table(self.current_approach)
#
#         # Connect dropdown
#         self.approach_select.currentTextChanged.connect(self.on_approach_changed)
#
#     def create_memory(self):
#         """Initialize memory dictionary for counts"""
#         memory = {}
#         for r in self.rows:
#             memory[r] = {c: 0 for c in self.columns}
#         return memory
#
#     def create_table(self):
#         """Create table with buttons for each cell"""
#         table = QTableWidget()
#         table.setRowCount(len(self.rows))
#         table.setColumnCount(len(self.columns))
#         table.setHorizontalHeaderLabels(self.columns)
#         table.setVerticalHeaderLabels(self.rows)
#
#         for row_idx, row_name in enumerate(self.rows):
#             for col_idx, col_name in enumerate(self.columns):
#                 btn = QPushButton("0")
#                 btn.clicked.connect(lambda checked, r=row_name, c=col_name: self.increment_count(r, c))
#                 table.setCellWidget(row_idx, col_idx, btn)
#
#         return table
#
#     def increment_count(self, row, col):
#         """Increase count in memory and update button text"""
#         self.memory[self.current_approach][row][col] += 1
#         # Find button and update text
#         table = self.tables_data[self.current_approach]
#         row_idx = self.rows.index(row)
#         col_idx = self.columns.index(col)
#         btn = table.cellWidget(row_idx, col_idx)
#         btn.setText(str(self.memory[self.current_approach][row][col]))
#
#     def show_table(self, approach):
#         """Display the table for the selected approach"""
#         if self.current_approach:
#             # Remove old table
#             self.layout.removeWidget(self.table)
#             self.table.hide()
#
#         self.table = self.tables_data[approach]
#         self.layout.addWidget(self.table)
#         self.table.show()
#
#         self.current_approach = approach
#
#     def on_approach_changed(self, approach):
#         self.show_table(approach)
#
#     def get_memory(self, approach=None):
#         """Return memory dictionary for current or specified approach"""
#         if approach is None:
#             approach = self.current_approach
#         return self.memory[approach]


class CounterPanel(QWidget):
    def __init__(self, config:IntersectionConfig, get_current_time_callback):
        super().__init__()
        self.get_current_time = get_current_time_callback  # function returning current video time
        self.layout = QVBoxLayout(self)

        # Approach dropdown
        self.layout.addWidget(QLabel("Select Approach:"))
        self.approach_select = QComboBox()
        self.approach_select.addItems(config.approaches)
        self.layout.addWidget(self.approach_select)

        # Table
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.rows = config.vehicle_classifications
        self.columns = ['through', 'left', 'right']

        # Store tables, memory, and click timestamps
        self.tables_data = {}
        self.memory = {}
        self.timestamps = {}  # store timestamps for each approach, row, column
        for approach in config.approaches:
            self.tables_data[approach] = self.create_table()
            self.memory[approach] = self.create_memory(default=0)
            self.timestamps[approach] = self.create_memory(default=[])

        # Show first approach table
        self.current_approach = config.approaches[0]
        self.show_table(self.current_approach)
        self.approach_select.currentTextChanged.connect(self.on_approach_changed)

    def create_memory(self, default):
        memory = {}
        for r in self.rows:
            memory[r] = {c: default for c in self.columns}
        return memory


    def create_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.rows))
        table.setColumnCount(len(self.columns))
        table.setHorizontalHeaderLabels(self.columns)
        table.setVerticalHeaderLabels(self.rows)

        for row_idx, row_name in enumerate(self.rows):
            for col_idx, col_name in enumerate(self.columns):
                btn = QPushButton("0")
                btn.clicked.connect(lambda checked, r=row_name, c=col_name: self.increment_count(r, c))
                table.setCellWidget(row_idx, col_idx, btn)
        return table

    def increment_count(self, row, col):
        """Increment count and store timestamp"""
        self.memory[self.current_approach][row][col] += 1
        btn = self.tables_data[self.current_approach].cellWidget(
            self.rows.index(row), self.columns.index(col)
        )
        btn.setText(str(self.memory[self.current_approach][row][col]))

        # Store timestamp of click
        timestamp = self.get_current_time()  # in seconds
        print(timestamp)
        if row not in self.timestamps[self.current_approach]:
            self.timestamps[self.current_approach][row] = {}
        if col not in self.timestamps[self.current_approach][row]:
            self.timestamps[self.current_approach][row][col] = []
        self.timestamps[self.current_approach][row][col].append(timestamp)

    def show_table(self, approach):
        if self.current_approach:
            self.layout.removeWidget(self.table)
            self.table.hide()

        self.table = self.tables_data[approach]
        self.layout.addWidget(self.table)
        self.table.show()
        self.current_approach = approach

    def on_approach_changed(self, approach):
        self.show_table(approach)

    def get_memory(self, approach=None):
        if approach is None:
            approach = self.current_approach
        return self.memory[approach]

    def get_timestamps(self, approach=None):
        if approach is None:
            approach = self.current_approach
        return self.timestamps[approach]

