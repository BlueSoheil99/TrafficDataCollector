import sys

from PyQt6.QtCore import QSize
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
        # self.setFixedSize(QSize(800, 500))


        # Central widget layout
        central = QWidget()
        layout = QHBoxLayout(central)

        # Video player on the left
        self.video_player = VideoPlayer(config)
        layout.addWidget(self.video_player)

        # Data manager
        # self.data_manager = DataManager() moveinside panel code

        # Counter panel on the right
        self.counter_panel = CounterPanel(config,
                                          get_current_time_callback=self.video_player.get_current_time)
        layout.addWidget(self.counter_panel)

        self.setCentralWidget(central)


    def on_count_added(self, record):
        self.data_manager.add_record(record)

    # def get_current_time(self):
    #     video_time = self.video_player.get_current_time
    #     return video_time



def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('data/icons/traffic.png'))
    # Run setup dialog
    dialog = SetupDialog()
    if dialog.exec() == dialog.DialogCode.Accepted:
        config = IntersectionConfig(dialog.get_config())
        if config.video_path == '':  ##todo DEBUG
            config.video_path = ('/Users/soheil/Library/CloudStorage/OneDrive-UW/0 Research/Sound '
                                 'Transit Project/Codes/TrafficDataCollector/data/0_0_1730564065032_10003_10026_0.mp4')
        window = MainWindow(config)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit()


if __name__ == "__main__":
    main()
