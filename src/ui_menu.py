from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QHBoxLayout, QCheckBox, QDateEdit, QTimeEdit,
    QComboBox, QStackedLayout, QWidget, QMessageBox
)
from PyQt6.QtCore import QDate, QTime, Qt


class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Setup Intersection")

        self.main_layout = QVBoxLayout(self)

        self.video_paths = []
        self.data_path = None

        # --- Dropdown menu ---
        collection_types = ["Volume only", 'Near-Miss Evaluation', 'Find Conflicts']
        self.main_layout.addWidget(QLabel("Select data collection type:"))
        self.collection_type = QComboBox()
        self.collection_type.addItems(collection_types)
        self.main_layout.addWidget(self.collection_type)
        self.collection_type.currentIndexChanged.connect(self._switch_type)

        # Select video button
        self.video_btn = QPushButton("Select Videos")
        self.video_btn.clicked.connect(self._select_videos)
        self.main_layout.addWidget(self.video_btn)

        self.type_stack = QStackedLayout()
        ##### for volume data collection
        self.volume_widget = self._get_volume_config_widget()
        self.type_stack.addWidget(self.volume_widget)
        ##### for conflict
        self.data_btn = QPushButton("Select metadata")
        self.data_btn.clicked.connect(self._select_data)
        # self.type_stack.addWidget(self.data_btn)
        data_widget = QWidget()
        data_layout = QVBoxLayout(data_widget)
        data_layout.addWidget(self.data_btn, alignment=Qt.AlignmentFlag.AlignTop)  # no stretching
        self.type_stack.addWidget(data_widget)
        ### add stack to the main layout
        self.main_layout.addLayout(self.type_stack)


        # OK/Cancel
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")
        ok_btn.clicked.connect(self._click_ok)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        self.main_layout.addLayout(buttons_layout)

    def _is_collection_type_volume(self):
        return self.collection_type.currentText() == "Volume only"

    def _switch_type(self):
        if self._is_collection_type_volume():
            self.type_stack.setCurrentIndex(0)
        else:
            self.type_stack.setCurrentIndex(1)

    def _get_volume_config_widget(self):
        volume_widget = QWidget(self)
        volume_layout = QVBoxLayout(volume_widget)
        # --- Observation date ---
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        volume_layout.addWidget(QLabel("Date of observation:"))
        volume_layout.addWidget(self.date_input)
        # --- Video start time ---
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime(12, 0))
        volume_layout.addWidget(QLabel("Video starting time:"))
        volume_layout.addWidget(self.time_input)
        # Approaches
        volume_layout.addWidget(QLabel("Select approaches:"))
        self.approaches = {}
        approaches_layout = QHBoxLayout()
        for name in ["NB", "SB", "WB", "EB"]:
            cb = QCheckBox(name)
            cb.setChecked(True)
            self.approaches[name] = cb
            approaches_layout.addWidget(cb)
        volume_layout.addLayout(approaches_layout)
        return volume_widget


    def _click_ok(self):
        # if len(self.video_paths)==0:
        if not self.video_paths:
            self._run_msg_box("Missing Videos",
                              "Please select at least one video before proceeding.")
            return
        if  self._is_collection_type_volume():
            self.accept()
        else:
            if self.data_path is None:
                self._run_msg_box("Missing Metadata",
                                  "Please select the metadata file before proceeding.")
                return
            self.accept()

    def _run_msg_box(self, title, txt):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(txt)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def _select_videos(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Video")
        if paths:
            self.video_paths = paths
            # self.video_btn.setText(paths.split("/")[-1])
            self.video_btn.setText(f'{len(paths)} video(s) selected')
        print(self.video_paths)

    def _select_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Metadata")
        if path:
            self.data_path = path
            # self.video_btn.setText(paths.split("/")[-1])
            self.data_btn.setText(f'Metadata: {path.split("/")[-1]} selected')
        print(self.data_path)


    def get_config(self):
        """Return dict with selected approaches, date, and start time."""
        if self._is_collection_type_volume():
            selected_approaches = [name for name, cb in self.approaches.items() if cb.isChecked()]
            t = self.get_start_time()
            return {
                "video_paths": self.video_paths,
                "collection_type": self.collection_type.currentText(),
                "approaches": selected_approaches,
                "date": self.get_date(),
                "start_time": t[0],
                "start_time_seconds": t[1]
            }
        else:
            return {
                "video_paths": self.video_paths,
                "data_path": self.data_path,
                "collection_type": self.collection_type.currentText()
            }


    def get_date(self):
        """Return selected date as YYYY-MM-DD string"""
        return self.date_input.date().toString("yyyy-MM-dd")

    def get_start_time(self):
        """Return starting time in seconds"""
        t = self.time_input.time()
        ts = t.hour() * 3600 + t.minute() * 60 + t.second()
        return [f'{t.hour():02}:{t.minute():02}:{t.second():02}',ts]


class CacheDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cache Found")
        self.setModal(True)  # block input to parent window
        self.setFixedSize(350, 120)

        # Message label
        message = QLabel("Cache found. Do you want to reload your previous process?")
        message.setWordWrap(True)

        # Yes/No buttons
        yes_btn = QPushButton("Yes")
        no_btn = QPushButton("No")
        yes_btn.clicked.connect(self.accept)  # closes dialog with Accepted
        no_btn.clicked.connect(self.reject)   # closes dialog with Rejected

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()  # push buttons to the right
        btn_layout.addWidget(yes_btn)
        btn_layout.addWidget(no_btn)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(message)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
