import os.path
import re
import sys
import tempfile
from datetime import timedelta

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSlot, QTimer, QElapsedTimer
from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QProgressBar, QMessageBox
from ffmpeg_progress_yield import FfmpegProgress
from pytube import YouTube
from .utils.get_youtube_thumbnail import *


class DownloadThread(QThread):
    download_signal = QtCore.pyqtSignal(float)
    download_exception = QtCore.pyqtSignal(str)
    down_part = 1
    filesize = 0
    step = 0

    def __init__(self, url: str, directory: str, title: str, fmt: str):
        super(DownloadThread, self).__init__()
        self.url = url
        self.directory = directory
        self.fmt = fmt
        self.title = re.sub(" +", " ", re.sub(r'[\\/*?:"<>|]', "", title))
        if fmt == "mp3":
            self.down_part = 0.5

    @pyqtSlot(str)
    def run(self):
        self.download()
        if self.step == 0:
            self.download_exception.emit("")

    def download(self):
        try:
            yt = YouTube(self.url)
            yt.register_on_progress_callback(self.progress_func)
            if self.fmt == "mp3":
                stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
                self.filesize = stream.filesize
                with tempfile.TemporaryDirectory() as tmp_dir:
                    print("Created temporary directory:", tmp_dir)
                    tmp_file_name = self.get_available_filename(tmp_dir, "mp4")
                    tmp_file_mp4 = os.path.join(tmp_dir, tmp_file_name)
                    stream.download(output_path=tmp_dir, filename=tmp_file_name)

                    file_mp3_name = self.get_available_filename(self.directory, self.fmt)
                    file_mp3 = os.path.join(self.directory, file_mp3_name)
                    print("Converting file %s to %s" % (tmp_file_mp4, file_mp3))
                    cmd = [
                        "./ffmpeg/bin/ffmpeg.exe", '-i', tmp_file_mp4, file_mp3,
                        "-f", "null", "/dev/null",
                    ]
                    ff = FfmpegProgress(cmd)
                    for progress in ff.run_command_with_progress():
                        progress = int(100 * self.down_part + progress * (1 - self.down_part))
                        self.download_signal.emit(progress)
                    os.remove(tmp_file_mp4)

            else:
                stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
                self.filesize = stream.filesize
                stream.download(
                    output_path=self.directory,
                    filename=self.get_available_filename(self.directory, self.fmt)
                )
        except:
            self.download_exception.emit(str(sys.exc_info()[1]))

    def progress_func(self, chunk, file_handle, bytes_remaining):
        remaining = (100 * self.down_part * bytes_remaining) / self.filesize
        self.step = 100 * self.down_part - int(remaining)
        self.download_signal.emit(self.step)

    def get_available_filename(self, directory: str, fmt: str) -> str:
        file_counter = 1
        filename = "%s.%s" % (self.title, fmt)
        while os.path.isfile(os.path.join(directory, filename)):
            filename = "%s (%d).%s" % (self.title, file_counter, fmt)
            file_counter += 1
        if file_counter != 1:
            print("File with same name exists, using filename: \"%s\"" % filename)
        return filename


class VideoDownload(QGroupBox):

    def setElapsedTime(self, is_start: bool = True):
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

        # Картинка видео
        image = get_youtube_thumbnail(yt.thumbnail_url, 120)
        video_image = QLabel(self)
        video_image.setPixmap(image)
        video_image.setFixedWidth(100)
        video_image.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        video_image.setContentsMargins(10, 15, 10, 0)
        layout.addWidget(video_image)

        # Информация
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(0)
        layout.addLayout(info_layout)

        # Заголовок видео
        title = QLabel("<b>%s</b>" % self.title, self)
        title.setStyleSheet("QLabel{font-size: 7pt}")
        title.setMaximumHeight(20)
        title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        info_layout.addWidget(title)

        # Счетчик времени
        self.elapsed = QLabel(self)
        self.elapsed.setStyleSheet("QLabel{font-size: 6pt}")
        self.elapsed.setMaximumHeight(20)
        self.elapsed.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setElapsedTime(False)
        info_layout.addWidget(self.elapsed)

        # Прогресс бар
        self.progress = QProgressBar(self)
        info_layout.addWidget(self.progress)

        # Запуск загрузки
        self.download_tread = DownloadThread(yt.watch_url, self.directory, self.title, self.fmt)
        self.download_tread.download_signal.connect(self.progress_function)
        self.download_tread.download_exception.connect(self.exception_handler)
        self.download_tread.start()

        # Запуск таймера
        self.time = QElapsedTimer()
        self.timer = QTimer()
        self.timer.setInterval(int(1000))
        self.timer.timeout.connect(self.setElapsedTime)
        self.time.start()
        self.timer.start()

    def stop(self):
        if self.timer.isActive():
            self.setElapsedTime()
            self.timer.stop()

    def progress_function(self, current_progress: int):
        self.progress.setValue(current_progress)
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
            msg.setDetailedText("Exception: " + message)
            msg.exec()
        self.deleteLater()

    # def open_directory(self):
    #     QDesktopServices.openUrl(QUrl("file:///" + self.directory))
