from __future__ import annotations

import os
import yaml
from widgets.video_info import VideoInfo
from widgets.video_download import VideoDownload
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QLayout, \
    QScrollArea
from pytube import YouTube


# Чтение локального файла настроек
def read_settings_yaml(file_path: str):
    with open(file_path, "r") as config_file:
        return yaml.load(config_file, Loader=yaml.FullLoader)


# Очистка слоя
def clear_layout(layout: QLayout):
    for i in reversed(range(layout.count())):
        layout.itemAt(i).widget().deleteLater()


# Класс главного окна приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Чтение файла настроек приложения
        self.settings = read_settings_yaml(os.path.join("config", "settings.yml"))

        # Заголовок окна приложения
        self.setWindowTitle("simple-youtube-downloader")
        self.setWindowIcon(QIcon(os.path.join("data", "icons", "icon.ico")))

        # Главный виджет
        self.main_widget = QWidget(self)
        self.main_widget.setMinimumWidth(700)
        self.main_widget.setMinimumHeight(400)
        self.setCentralWidget(self.main_widget)

        # Главный слой
        vbl = QVBoxLayout(self.main_widget)

        # Заголовок
        label = QLabel("<b>Введите ссылку для скачивания:</b>", self.main_widget)
        label.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        label.setStyleSheet("QLabel{font-size: 8pt;}")
        label.setMaximumHeight(30)
        label.setMargin(5)
        vbl.addWidget(label)

        # Поле для ввода ссылки
        link_layout = QHBoxLayout()
        self.link = QLineEdit(self.main_widget)
        self.link.setPlaceholderText("Ссылка на видео")
        self.link.textChanged.connect(self.get_video_info)
        link_layout.addWidget(self.link)

        # Кнопка скачивания видео
        self.download_button = QPushButton("Скачать", self.main_widget)
        self.download_button.clicked.connect(self.create_download)
        self.download_button.hide()
        link_layout.addWidget(self.download_button)
        vbl.addLayout(link_layout)

        # Поле с информацией о видео
        self.video_info_layout = QVBoxLayout()
        vbl.addLayout(self.video_info_layout)

        # Загрузки видео
        scroll_area = QScrollArea(self.main_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea {border: none}")
        widget = QWidget()
        scroll_area.setWidget(widget)
        self.downloads_layout = QVBoxLayout(widget)
        self.downloads_layout.addStretch()
        vbl.addWidget(scroll_area)

    # Проверка ссылки видео на доступность
    def check_video_available(self) -> YouTube | None:
        try:
            self.download_button.show()
            return YouTube(self.link.text())
        except (ValueError, Exception):
            self.download_button.hide()
            return None

    # Отображение информационного виджета
    def get_video_info(self):
        clear_layout(self.video_info_layout)
        yt = self.check_video_available()
        if yt:
            video_info = VideoInfo(yt, self.main_widget)
            self.video_info_layout.addWidget(video_info)

    # Создание загрузки
    def create_download(self):
        yt = self.check_video_available()
        if yt:
            download = VideoDownload(yt, self.settings["DOWNLOAD_DIR"], self.settings["FORMAT"], self.main_widget)
            # self.downloads_layout.addWidget(download)
            self.downloads_layout.insertWidget(0, download)
