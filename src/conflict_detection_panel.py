from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QFormLayout, QLineEdit, QSpinBox,
    QPushButton, QLabel, QHBoxLayout, QHeaderView, QFileDialog, QFrame, QSizePolicy, QMessageBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer

from src.data_manager import DataManager
from src.intersection_config import IntersectionConfig
from src.message_widget import MessageWidget


class DetectionPanel(QWidget):
    def __init__(self, config:IntersectionConfig, get_current_time_vid_callback, from_cache=False):
        super().__init__()
        self.get_current_time_and_video = get_current_time_vid_callback  # function returning current video time
        self.data_manager = DataManager(config)
        self.columns = ['timestamp', 'notes']

        self.main_layout = QVBoxLayout(self)

        #### Add Buttons
        ## Add 'add' btn
        add_btn = QPushButton('Add')
        add_btn.clicked.connect(self.add_clicked)
        self.main_layout.addWidget(add_btn)
        ## Add 'erase' btn
        self.erase_button = QPushButton("Erase")
        self.erase_button.setIcon(QIcon(config.icons['erase']))
        self.erase_button.clicked.connect(self.erase_clicked)
        self.main_layout.addWidget(self.erase_button)
        self.create_line()

        #### Add Table
        self.table = self.create_table(config)
        self.main_layout.addWidget(self.table)
        self.create_line()

        ### SAVE BUTTON
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_data)
        self.main_layout.addWidget(self.save_btn)

        ### MESSAGE section
        self.msg_widget = MessageWidget()
        self.main_layout.addWidget(self.msg_widget)

        # Create a timer to autosave cache
        self.cache_timer = QTimer(self)
        self.cache_timer.timeout.connect(self.auto_save_cache)
        self.cache_timer.start(30000)  # 30,000 ms = 30 seconds


    def create_table(self, config:IntersectionConfig):
        table = QTableWidget(self)
        table.setColumnCount(2)
        table.setColumnWidth(0, 50)
        table.setColumnWidth(1, 150)
        table.setHorizontalHeaderLabels(self.columns)
        self._load_from_cache(table, config)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        table.show()
        return table

    def _load_from_cache(self, table, config:IntersectionConfig):
        if config.timestamps:
            cache = config.timestamps
            table.setRowCount(len(cache))
            row = 0
            for e in cache:
                table.setItem(row, 0, QTableWidgetItem(e['timestamp']))
                table.setItem(row, 1, QTableWidgetItem(e['notes']))
                row += 1

    def create_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_layout.addWidget(line)

    def add_clicked(self):
        entry_time = _format_time(self.get_current_time_and_video()[0])
        row_num = self.table.rowCount()
        self.table.insertRow(row_num)
        self.table.setItem(row_num, 0, QTableWidgetItem(entry_time))
        self.msg_widget.update_message_box(f'Added entry @{entry_time}')
        return


    def erase_clicked(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            return QMessageBox.warning(self, 'Warning', 'Please select a record to delete')

        button = QMessageBox.question(
            self,
            'Confirmation',
            'Are you sure that you want to delete the selected row?',
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )
        if button == QMessageBox.StandardButton.Yes:
            entry_time = self.table.item(current_row, self.columns.index('timestamp')).text()
            self.table.removeRow(current_row)
            self.msg_widget.update_message_box(f'Removed enty @{entry_time}')



    def save_data(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Counts",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            msg = self.data_manager.save_file(file_path, cache=False, data=self.get_table_data())
            self.msg_widget.update_message_box(msg)

    def auto_save_cache(self):
        """Save cache automatically every 1 minute"""
        # pick a cache path (temporary file or fixed location)
        cache_path = "data/cache.json"
        msg = self.data_manager.save_file(cache_path, cache=True, data=self.get_table_data())
        self.msg_widget.update_message_box(msg)

    def get_table_data(self):
        data = []
        for row in range(self.table.rowCount()):
            item = {}
            for idx, col in enumerate(self.columns):
                val = self.table.item(row, idx)
                if val:
                    item[col] = self.table.item(row, idx).text() # string values
                else:
                    item[col] = self.table.item(row, idx) # None values

            data.append(item)
        return data


btn_stylesheet = """ QPushButton { background-color: white;border: 1px solid lightgray; 
                                    min-height: 30px; min-width: 100px;}
                    QPushButton:hover { background-color: lightblue; }"""
def _format_time(seconds):
    mins, secs = divmod(seconds, 60)
    formatted_time =  f'{int(mins):02d}:{secs:04.1f}'
    return formatted_time