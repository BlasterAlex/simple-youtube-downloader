import sys
from datetime import timedelta

from PyQt5.QtCore import Qt, QTimer, QElapsedTimer
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QProgressBar, QMessageBox
from pytube import YouTube

sys.path.insert(0, '..')
from utils.download_thread import DownloadThread  # noqa
from utils.get_youtube_thumbnail import get_youtube_thumbnail  # noqa


class VideoDownload(QGroupBox):

    def set_elapsed_time(self, is_start: bool = True):
        if is_start:
            self.elapsed.setText("Прошло времени: <b>%s</b>" % timedelta(seconds=int(self.time.elapsed() / 1000)))
        else:
            self.elapsed.setText("Прошло времени: <b>%s</b>" % timedelta(seconds=0))

    def __init__(self, yt: YouTube, directory: str, fmt: str, parent=None):
        super().__init__(parent)
        self.directory = directory
        self.title = yt.title
        self.fmt = fmt

        self.setStyleSheet("QGroupBox {border: 1px solid gray; border-radius: 5px}")
        self.setFixedHeight(100)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Video thumbnail
        image = get_youtube_thumbnail(yt.thumbnail_url, 120)
        video_image = QLabel(self)
        video_image.setPixmap(image)
        video_image.setFixedWidth(100)
        video_image.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        video_image.setContentsMargins(10, 15, 10, 0)
        layout.addWidget(video_image)

        # Info
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(0)
        layout.addLayout(info_layout)

        # Video title
        title = QLabel("<b>%s</b>" % self.title, self)
        title.setStyleSheet("QLabel{font-size: 7pt}")
        title.setMaximumHeight(20)
        title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        info_layout.addWidget(title)

        # Time counter
        self.elapsed = QLabel(self)
        self.elapsed.setStyleSheet("QLabel{font-size: 6pt}")
        self.elapsed.setMaximumHeight(20)
        self.elapsed.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.set_elapsed_time(False)
        info_layout.addWidget(self.elapsed)

        # Progress bar
        self.progress = QProgressBar(self)
        info_layout.addWidget(self.progress)

        # Start downloading
        self.download_tread = DownloadThread(yt.watch_url, self.directory, self.title, self.fmt)
        self.download_tread.download_signal.connect(self.progress_function)
        self.download_tread.download_exception.connect(self.exception_handler)
        self.download_tread.start()

        # Start timer
        self.time = QElapsedTimer()
        self.timer = QTimer()
        self.timer.setInterval(int(1000))
        self.timer.timeout.connect(self.set_elapsed_time)
        self.time.start()
        self.timer.start()

    def stop(self):
        if self.timer.isActive():
            self.set_elapsed_time()
            self.timer.stop()

    def progress_function(self, current_progress: int):
        self.progress.setValue(int(current_progress))
        if current_progress < 100:
            return
        self.stop()

    def exception_handler(self, message):
        self.stop()
        if len(message) != 0:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setText(
                "Ошибка при скачивании <b>%s</b>" % self.title
            )
            msg.setInformativeText(
                "Нажмите <i>Show Details</i> для получения дополнительной информации"
            )
            msg.setWindowTitle("Ошибка скачивания")
            if self.download_tread.step <= self.download_tread.down_part * 100:
                msg.setDetailedText("Downloading error: " + message)
            else:
                msg.setDetailedText("Converting error: " + message)
            msg.exec()
