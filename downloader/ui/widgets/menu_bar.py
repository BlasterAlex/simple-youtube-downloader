import logging

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QActionGroup

from downloader.utils.settings import write_settings


class MenuBar(QMenuBar):
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)

        self.format_menu = QMenu('Формат', self)
        self.addMenu(self.format_menu)

        format_actions = QActionGroup(self.format_menu)
        set_mp3_action = QAction('Аудио', format_actions, checkable=True)
        set_mp3_action.triggered.connect(self.set_mp3)
        self.format_menu.addAction(set_mp3_action)

        set_mp4_action = QAction('Видео', format_actions, checkable=True)
        set_mp4_action.triggered.connect(self.set_mp4)
        self.format_menu.addAction(set_mp4_action)

        self.set_format_title()
        if self.settings['FORMAT'] == 'mp3':
            set_mp3_action.setChecked(True)
        else:
            set_mp4_action.setChecked(True)

    def set_format_title(self):
        if self.settings['FORMAT'] == 'mp3':
            self.format_menu.setTitle('Формат: Аудио')
        else:
            self.format_menu.setTitle('Формат: Видео')

    def set_mp3(self):
        self.settings['FORMAT'] = 'mp3'
        write_settings(self.settings)
        self.set_format_title()
        logging.info('Format of downloaded videos has been changed to mp3')

    def set_mp4(self):
        self.settings['FORMAT'] = 'mp4'
        write_settings(self.settings)
        self.set_format_title()
        logging.info('Format of downloaded videos has been changed to mp4')
