from datetime import timedelta
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel

from pytube import YouTube, Channel # noqa
from utils.get_youtube_thumbnail import get_youtube_thumbnail  # noqa


class VideoInfo(QGroupBox):

    def __init__(self, yt: YouTube, parent=None):
        super().__init__(parent)

        # Info widget
        self.setStyleSheet("QGroupBox {border: none}")
        self.setMaximumHeight(100)
        layout = QHBoxLayout(self)

        # Video thumbnail
        image = get_youtube_thumbnail(yt.thumbnail_url, 150)
        video_image = QLabel(self)
        video_image.setPixmap(image)
        video_image.setFixedWidth(150)
        video_image.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(video_image)

        # Information
        info_layout = QVBoxLayout()
        title = QLabel("Название: <b>%s</b>" % yt.title, self)
        title.setStyleSheet("QLabel{font-size: 8pt;}")
        title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        title.setContentsMargins(10, 5, 0, 0)
        info_layout.addWidget(title)

        channel = QLabel("Канал: <b>%s</b>" % Channel(yt.channel_url).channel_name, self)
        channel.setStyleSheet("QLabel{font-size: 7pt;}")
        channel.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        channel.setContentsMargins(10, 5, 0, 0)
        info_layout.addWidget(channel)

        duration = QLabel("Продолжительность: <b>%s</b>" % timedelta(seconds=yt.length), self)
        duration.setStyleSheet("QLabel{font-size: 7pt;}")
        duration.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        duration.setContentsMargins(10, 5, 0, 0)
        info_layout.addWidget(duration)
        info_layout.addStretch()
        layout.addLayout(info_layout)
