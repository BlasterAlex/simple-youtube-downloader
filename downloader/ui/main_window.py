from __future__ import annotations

import logging
import os

import yaml
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QLayout, \
    QScrollArea
from pytube import YouTube  # noqa

from downloader.ui.widgets.video_download import VideoDownload
from downloader.ui.widgets.video_info import VideoInfo


def read_settings_yaml(file_path: str):
    with open(file_path, "r", encoding='utf-8') as config_file:
        return yaml.load(config_file, Loader=yaml.FullLoader)


def clear_layout(layout: QLayout):
    for i in reversed(range(layout.count())):
        layout.itemAt(i).widget().deleteLater()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Reading app settings file
        self.settings = read_settings_yaml(os.path.join("config", "settings.yml"))

        # Logging settings
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(
                    filename=self.settings['LOG_FILE'],
                    encoding='utf-8'
                ),
                logging.StreamHandler()
            ]
        )

        # App window title
        self.setWindowTitle("simple-youtube-downloader")
        self.setWindowIcon(QIcon(os.path.join("data", "icons", "icon.ico")))

        # Main widget
        self.main_widget = QWidget(self)
        self.main_widget.setMinimumWidth(700)
        self.main_widget.setMinimumHeight(400)
        self.setCentralWidget(self.main_widget)

        # Main layout
        vbl = QVBoxLayout(self.main_widget)

        # Title
        label = QLabel("<b>Введите ссылку для скачивания:</b>", self.main_widget)
        label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        label.setStyleSheet("QLabel{font-size: 8pt;}")
        label.setMaximumHeight(30)
        label.setMargin(5)
        vbl.addWidget(label)

        # Link field
        link_layout = QHBoxLayout()
        self.link = QLineEdit(self.main_widget)
        self.link.setPlaceholderText("Ссылка на видео")
        self.link.textChanged.connect(self.get_video_info)
        link_layout.addWidget(self.link)

        # Download button
        self.download_button = QPushButton("Скачать", self.main_widget)
        self.download_button.clicked.connect(self.create_download)
        self.download_button.hide()
        link_layout.addWidget(self.download_button)
        vbl.addLayout(link_layout)

        # Video info
        self.video_info_layout = QVBoxLayout()
        vbl.addLayout(self.video_info_layout)

        # Last downloads
        scroll_area = QScrollArea(self.main_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea {border: none}")
        widget = QWidget()
        scroll_area.setWidget(widget)
        self.downloads_layout = QVBoxLayout(widget)
        self.downloads_layout.addStretch()
        vbl.addWidget(scroll_area)

    # Check youtube video link availability
    def check_video_available(self) -> YouTube | None:
        try:
            self.download_button.show()
            return YouTube(self.link.text())
        except (ValueError, Exception):
            self.download_button.hide()
            return None

    # Show info widget
    def get_video_info(self):
        clear_layout(self.video_info_layout)
        yt = self.check_video_available()
        if yt:
            video_info = VideoInfo(yt, self.main_widget)
            self.video_info_layout.addWidget(video_info)

    # Create download
    def create_download(self):
        logging.info('Download video %s' % self.link.text())
        yt = self.check_video_available()
        if yt:
            download = VideoDownload(yt, self.settings['DOWNLOAD_DIR'], self.settings['FORMAT'], self.main_widget)
            self.downloads_layout.insertWidget(0, download)
