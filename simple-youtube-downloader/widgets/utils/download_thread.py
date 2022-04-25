import logging
import os.path
import re
import sys
import tempfile
import traceback

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSlot
from ffmpeg_progress_yield import FfmpegProgress
from pytube import YouTube


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
        self.title = re.sub(' +', ' ', re.sub(r'[\\/*?:"<>|]', '', title)).encode('ascii', 'ignore').decode().strip()
        if fmt == 'mp3':
            self.down_part = 0.5

    @pyqtSlot(str)
    def run(self):
        self.download()
        if self.step == 0:
            self.download_exception.emit('')

    def download(self):
        try:
            yt = YouTube(self.url)
            yt.register_on_progress_callback(self.progress_func)
            if self.fmt == 'mp3':
                stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
                self.filesize = stream.filesize
                with tempfile.TemporaryDirectory() as tmp_dir:
                    logging.info('Created temporary directory: %s' % tmp_dir)
                    tmp_file_name = self.get_available_filename(tmp_dir, 'mp4')
                    tmp_file_mp4 = os.path.join(tmp_dir, tmp_file_name)
                    stream.download(output_path=tmp_dir, filename=tmp_file_name)

                    file_mp3_name = self.get_available_filename(self.directory, self.fmt)
                    file_mp3 = os.path.join(self.directory, file_mp3_name)
                    logging.info('Converting file %s to %s' % (tmp_file_mp4, file_mp3))
                    cmd = [
                        './ffmpeg/bin/ffmpeg.exe', '-i', tmp_file_mp4, file_mp3,
                        '-f', 'null', '/dev/null',
                    ]
                    ff = FfmpegProgress(cmd)
                    for progress in ff.run_command_with_progress():
                        progress = int(100 * self.down_part + progress * (1 - self.down_part))
                        self.download_signal.emit(progress)
                    os.remove(tmp_file_mp4)

            else:
                stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
                self.filesize = stream.filesize
                stream.download(
                    output_path=self.directory,
                    filename=self.get_available_filename(self.directory, self.fmt)
                )
        except:
            self.download_exception.emit(str(sys.exc_info()[1]))
            logging.error(traceback.format_exc())

    def progress_func(self, chunk, file_handle, bytes_remaining):
        remaining = (100 * self.down_part * bytes_remaining) / self.filesize
        self.step = int(100 * self.down_part - int(remaining))
        self.download_signal.emit(self.step)

    def get_available_filename(self, directory: str, fmt: str) -> str:
        file_counter = 1
        filename = '%s.%s' % (self.title, fmt)
        while os.path.isfile(os.path.join(directory, filename)):
            filename = '%s (%d).%s' % (self.title, file_counter, fmt)
            file_counter += 1
        if file_counter != 1:
            logging.info('File with same name exists, using filename: "%s"' % filename)
        return filename
