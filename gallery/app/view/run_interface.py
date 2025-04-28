# coding:utf-8
from random import random
from time import sleep
from typing import Tuple

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QHBoxLayout, QHeaderView, QTableWidgetItem
from qfluentwidgets import LineEdit, PrimaryPushButton, MessageBoxBase, SubtitleLabel, MessageBox, InfoBar, \
    InfoBarPosition, TableWidget, PasswordLineEdit, ComboBox, PlainTextEdit, StrongBodyLabel

from .gallery_interface import GalleryInterface
from ..util.encryption_util import Encryption
from ..util.yaml_util import YamlUtil


class RunInterface(GalleryInterface):
    """ 命令模板页面 """

    def __init__(self, parent=None):
        super().__init__(
            title="运行命令",
            subtitle='运行预设的配置命令',
            parent=parent
        )
        self.setObjectName('runInterface')

        # 设备组管理
        group_layout = QHBoxLayout()
        group_layout.setSpacing(10)
        self.group_combo = ComboBox()
        btn_run = PrimaryPushButton("开始运行")
        btn_stop = PrimaryPushButton("停止运行")
        group_layout.addWidget(self.group_combo, 6)
        group_layout.addWidget(btn_run, 1)
        group_layout.addWidget(btn_stop, 1)
        btn_run.clicked.connect(lambda: self.run_command())
        btn_stop.clicked.connect(lambda: self.stop_command())

        # 日志显示文本框
        self.log_edit = PlainTextEdit()
        self.log_edit.setReadOnly(True)

        # 添加至总布局
        self.vBoxLayout.addLayout(group_layout)
        self.vBoxLayout.addWidget(self.log_edit)

        # 更新列表
        self.update_combo(YamlUtil("app/config/device_templates.yml", {"devices": []}).get_keys())

    def run_command(self):
        self.log_edit.appendPlainText(str(random()) + "test111111")

    def stop_command(self):
        self.log_edit.clear()

    def update_combo(self, data):
        self.group_combo.clear()
        self.group_combo.addItems(data)
