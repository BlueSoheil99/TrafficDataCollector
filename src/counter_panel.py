from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QTableWidget,
    QPushButton, QLabel, QHBoxLayout, QHeaderView, QFileDialog, QFrame, QSizePolicy
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer

from src.data_manager import DataManager
from src.intersection_config import IntersectionConfig


class CounterPanel(QWidget):
    def __init__(self, config:IntersectionConfig, get_current_time_vid_callback, from_cache=False):
        super().__init__()
        self.get_current_time_and_video = get_current_time_vid_callback  # function returning current video time
        self.layout = QVBoxLayout(self)

        ### Initiating memory and datamanagere component
        self.veh_rows = config.vehicle_classifications
        self.vru_rows = config.vru_classifications
        self.columns = ['Left', 'Through', 'Right']  # movements
        self.data_manager = DataManager(config,
                                        (self.veh_rows, self.vru_rows, self.columns))

        #### Approach dropdown and Mode selection
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

        self.create_line()
        #### vehicle count Table
        self.layout.addWidget(QLabel('Vehicle counts'))
        self.table = QTableWidget()  # probably don't need this line
        self.table_layout = QHBoxLayout()
        self.table_layout.addWidget(self.table)
        self.layout.addLayout(self.table_layout)
        # Store tables, memory
        self.tables_data = {}
        for approach in config.approaches:
            self.tables_data[approach] = self.create_table()
        # Show first approach table
        self.current_approach = config.approaches[0]
        self.show_table(self.current_approach)
        self.update_table_display() # to make sure loaded cache is show from the beginning
        self.approach_select.currentTextChanged.connect(self.on_approach_changed)

        ### VRU COUNTS
        self.layout.addWidget(QLabel("VRU counts"))
        self.vru_layout = QHBoxLayout()
        self.vru_buttons = {}
        for user in config.vru_classifications:
            self.vru_buttons[user] = QPushButton(f"{user}: 0")
            self.vru_buttons[user].setStyleSheet(btn_stylesheet)
            self.vru_buttons[user].clicked.connect(lambda checked, vru_class=user:
                                                   self.vru_clicked(vru_class))
            self.vru_layout.addWidget(self.vru_buttons[user])
        self.layout.addLayout(self.vru_layout)
        self.create_line()

        ### SAVE BUTTON
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_data)
        self.layout.addWidget(self.save_btn)

        ### MESSAGE section
        self.msg_layout = QHBoxLayout()
        self.last_action_label = QLabel("Last Action:")
        # self.msg_layout.addWidget(self.last_action_label)
        self.message_label = QLabel()
        # self.msg_layout.addWidget(self.message_label)
        style_message_section(self.msg_layout, self.last_action_label, self.message_label)
        self.layout.addLayout(self.msg_layout)

        #Create a timer to autosave cache
        self.cache_timer = QTimer(self)
        self.cache_timer.timeout.connect(self.auto_save_cache)
        self.cache_timer.start(30000)  # 30,000 ms = 30 seconds


    def create_table(self):
        table = QTableWidget()
        table.setRowCount(len(self.veh_rows))
        table.setColumnCount(len(self.columns))
        table.setHorizontalHeaderLabels(self.columns)
        table.setVerticalHeaderLabels(self.veh_rows)
        for row_idx, row_name in enumerate(self.veh_rows):
            for col_idx, col_name in enumerate(self.columns):
                btn = QPushButton("0")
                btn.setStyleSheet(btn_stylesheet)
                btn.clicked.connect(lambda checked, r=row_name, c=col_name: self.table_clicked(r, c))
                table.setCellWidget(row_idx, col_idx, btn)
        return table

    def create_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(line)

    def update_table_display(self):
        for veh_class in self.veh_rows:
            for movement in self.columns:
                counts = self.data_manager.get_veh_counts(veh_class, movement, self.current_approach)
                if self.erase_mode:
                    try:
                        # label = str(self.timestamps[self.current_approach][row][col][-1])
                        label = str(counts[-1])
                    except IndexError:
                        label = '-'
                else:
                    # label = str(len(self.timestamps[self.current_approach][row][col]))
                    label = str(len(counts))

                btn = self.tables_data[self.current_approach].cellWidget(
                    self.veh_rows.index(veh_class), self.columns.index(movement)
                )
                btn.setText(label)

    def update_VRU_display(self):
        for user in self.vru_rows:
            btn = self.vru_buttons[user]
            counts = self.data_manager.get_vru_counts(user, self.current_approach)
            if self.erase_mode:
                try:
                    label = str(counts[-1])
                except IndexError:
                    label = '-'
            else:
                label = str(len(counts))
            btn.setText(f'{user}: {label}')

    def table_clicked(self, row, col):
        """
        increase count and store timestamp if erase_mode is off,
        removes last entry if erase_mode is on
        """
        new_label, msg = self.data_manager.update_veh_counts(row, col,
                                                       self.current_approach,
                                                       self.erase_mode,
                                                       self.get_current_time_and_video())
        self.update_message_box(msg)
        btn = self.tables_data[self.current_approach].cellWidget(
            self.veh_rows.index(row), self.columns.index(col)
        )
        btn.setText(new_label)

    def vru_clicked(self, vru_class):
        new_label, msg = self.data_manager.update_vru_counts(vru_class,
                                                       self.current_approach,
                                                       self.erase_mode,
                                                       self.get_current_time())
        self.update_message_box(msg)
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
        # self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        self.table.show()
        self.current_approach = approach

    def on_approach_changed(self, approach):
        self.show_table(approach)
        self.update_table_display()
        self.update_VRU_display()

    def save_data(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Counts",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            msg = self.data_manager.save_file(file_path, cache=False)
            self.update_message_box(msg)

    def auto_save_cache(self):
        """Save cache automatically every 1 minute"""
        # pick a cache path (temporary file or fixed location)
        cache_path = "data/cache.json"
        msg = self.data_manager.save_file(cache_path, cache=True)
        # self.message_label.setText("💾 Cache saved")
        self.update_message_box(msg)

    def update_message_box(self, text):
        if text: #not None
            self.message_label.setText(text)


btn_stylesheet = """ QPushButton { background-color: white;border: 1px solid lightgray; 
                                    min-height: 30px; min-width: 100px;}
                    QPushButton:hover { background-color: lightblue; }"""

def style_message_section(msg_layout, last_action_label, message_label):
    msg_layout.setSpacing(5)  # small gap between label and message
    msg_layout.setContentsMargins(0, 0, 0, 0)  # remove extra padding around layout

    # Left-side label
    last_action_label.setStyleSheet("""
        QLabel {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-weight: normal;
            color: #2C3E50;   /* subtle dark color */
        }
    """)
    msg_layout.addWidget(last_action_label)

    # Message label
    message_label.setStyleSheet("""
        QLabel {
            font-family: 'Courier New', Courier, monospace;
            font-weight: normal;
            color: #555555;
            background-color: #F7F7F7;
            border-radius: 3px;
            padding: 2px 6px;
        }
    """)
    # Let the message stretch to fill remaining horizontal space
    message_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    msg_layout.addWidget(message_label)


