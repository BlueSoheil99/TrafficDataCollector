from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QHBoxLayout, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QIcon

from src.data_manager import DataManager
from src.intersection_config import IntersectionConfig




class CounterPanel(QWidget):
    def __init__(self, config:IntersectionConfig, get_current_time_callback):
        super().__init__()
        self.get_current_time = get_current_time_callback  # function returning current video time
        self.layout = QVBoxLayout(self)

        # Approach dropdown
        self.layout.addWidget(QLabel("Select Approach:"))
        self.selection_layout = QHBoxLayout(self)
        self.approach_select = QComboBox()
        self.approach_select.addItems(config.approaches)
        self.selection_layout.addWidget(self.approach_select)
        # # add eraser
        self.erase_mode=False
        self.erase_button = QPushButton("Erase")
        self.erase_button.setIcon(QIcon(config.icons['erase']))
        self.selection_layout.addWidget(self.erase_button)
        self.erase_button.clicked.connect(self.erase_clicked)

        self.layout.addLayout(self.selection_layout)

        # Table
        self.layout.addWidget(QLabel('Vehicle counts'))
        self.table = QTableWidget()
        self.table_layout = QHBoxLayout()
        self.table_layout.addWidget(self.table)
        self.layout.addLayout(self.table_layout)

        self.veh_rows = config.vehicle_classifications
        self.vru_rows = config.vru_classifications
        self.columns = ['through', 'left', 'right']

        # Store tables, memory, and click timestamps
        self.tables_data = {}
        self.timestamps = {}  # store timestamps for each approach, row, column
        for approach in config.approaches:
            self.tables_data[approach] = self.create_table()
            self.timestamps[approach] = self.create_memory()

        # Show first approach table
        self.current_approach = config.approaches[0]
        self.show_table(self.current_approach)
        self.approach_select.currentTextChanged.connect(self.on_approach_changed)

        # add VRU counts
        self.layout.addWidget(QLabel("VRU counts"))
        self.vru_layout = QHBoxLayout()
        self.vru_buttons = {}
        for user in config.vru_classifications:
            self.vru_buttons[user] = QPushButton(f"{user}:0")
            self.vru_buttons[user].clicked.connect(lambda checked, vru_class=user:
                                                   self.vru_clicked(vru_class))
            self.vru_layout.addWidget(self.vru_buttons[user])

        self.layout.addLayout(self.vru_layout)

        # save button
        self.data_manager = DataManager(config, self)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.data_manager.save_file)
        self.layout.addWidget(self.save_btn)


    def create_memory(self):
        memory = {}
        for r in self.veh_rows:
            memory[r] = {c: [] for c in self.columns}
        for r in self.vru_rows:
            memory[f'vru_{r}'] = []
        return memory

    def create_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.veh_rows))
        table.setColumnCount(len(self.columns))
        table.setHorizontalHeaderLabels(self.columns)
        table.setVerticalHeaderLabels(self.veh_rows)

        for row_idx, row_name in enumerate(self.veh_rows):
            for col_idx, col_name in enumerate(self.columns):
                btn = QPushButton("0")
                btn.clicked.connect(lambda checked, r=row_name, c=col_name: self.table_clicked(r, c))
                table.setCellWidget(row_idx, col_idx, btn)
        return table

    def update_table_display(self):
        for row in self.veh_rows:
            for col in self.columns:
                if self.erase_mode:
                    try:
                        label = str(self.timestamps[self.current_approach][row][col][-1])
                    except IndexError:
                        label = '-'
                else:
                    label = str(len(self.timestamps[self.current_approach][row][col]))

                btn = self.tables_data[self.current_approach].cellWidget(
                    self.veh_rows.index(row), self.columns.index(col)
                )
                btn.setText(label)

    def update_VRU_display(self):
        for user in self.vru_rows:
            btn = self.vru_buttons[user]
            key = f'vru_{user}'
            if self.erase_mode:
                try:
                    label = str(self.timestamps[self.current_approach][key][-1])
                except IndexError:
                    label = '-'
            else:
                label = str(len(self.timestamps[self.current_approach][key]))
            btn.setText(f'{user}:{label}')


    def table_clicked(self, row, col):
        """
        increase count and store timestamp if erase_mode is off,
        removes last entry if erase_mode is on
        """
        if self.erase_mode:
            if len(self.timestamps[self.current_approach][row][col])>0:
                deleted_entry = self.timestamps[self.current_approach][row][col].pop()
                print(f'The entry at time {deleted_entry} is removed from {self.current_approach}:[{row}, {col}]')
                try:
                    new_label = str(self.timestamps[self.current_approach][row][col][-1])
                except IndexError:
                    new_label = '-'
            else:
                new_label = '-'
        else:
            timestamp = self.get_current_time()  # in seconds
            self.timestamps[self.current_approach][row][col].append(timestamp)
            new_label = str(len(self.timestamps[self.current_approach][row][col]))

        btn = self.tables_data[self.current_approach].cellWidget(
            self.veh_rows.index(row), self.columns.index(col)
        )
        btn.setText(new_label)

    def vru_clicked(self, vru_class):
        key = f'vru_{vru_class}'
        if self.erase_mode:
            if len(self.timestamps[self.current_approach][key])>0:
                deleted_entry = self.timestamps[self.current_approach][key].pop()
                print(f'pedestrian at {deleted_entry} is removed from {self.current_approach} approach')
                try:
                    new_label = str(self.timestamps[self.current_approach][key][-1])
                except IndexError:
                    new_label = '-'
            else:
                new_label = '-'
        else:
            timestamp = self.get_current_time()  # in seconds
            self.timestamps[self.current_approach][key].append(timestamp)
            new_label = str(len(self.timestamps[self.current_approach][key]))
        btn = self.vru_buttons[vru_class]
        btn.setText(f'{vru_class}: {new_label}')

    def erase_clicked(self):
        if self.erase_mode:
            self.erase_mode = False
            self.erase_button.setStyleSheet('')
        else:
            self.erase_mode = True
            self.erase_button.setStyleSheet("background-color: salmon;")
        self.update_table_display()
        self.update_VRU_display()

    def show_table(self, approach):
        if self.current_approach:
            self.table_layout.removeWidget(self.table)
            self.table.hide()

        self.table = self.tables_data[approach]
        self.table_layout.addWidget(self.table)

        #todo check these
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)

        self.table.show()
        self.current_approach = approach

    def on_approach_changed(self, approach):
        self.show_table(approach)
        self.update_table_display()
        self.update_VRU_display()


