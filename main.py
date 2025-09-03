import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout

from src.ui_menu import SetupDialog
from src.video_player import VideoPlayer
from src.counter_panel import CounterPanel
from src.intersection_config import IntersectionConfig
from src.data_manager import DataManager


class MainWindow(QMainWindow):
    def __init__(self, config:IntersectionConfig):
        super().__init__()
        self.setWindowTitle("Traffic Counter")

        # Central widget layout
        central = QWidget()
        layout = QHBoxLayout(central)

        # Video player on the left
        self.video_player = VideoPlayer(config.video_path)
        layout.addWidget(self.video_player)

        # Counter panel on the right
        self.counter_panel = CounterPanel(config)
        layout.addWidget(self.counter_panel)

        self.setCentralWidget(central)

        # Data manager
        self.data_manager = DataManager()

        # Connect signals
        self.counter_panel.count_added.connect(self.on_count_added)

    def on_count_added(self, record):
        self.data_manager.add_record(record)


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('data/icons/traffic.png'))
    # Run setup dialog
    dialog = SetupDialog()
    if dialog.exec() == dialog.DialogCode.Accepted:
        config = IntersectionConfig(dialog.get_config())
        window = MainWindow(config)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()


if __name__ == "__main__":
    main()
