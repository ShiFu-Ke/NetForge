# coding:utf-8
import logging
import os
from random import random
from time import sleep
from typing import Tuple
from logging import Handler
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtCore import Qt, QRegExp, QStandardPaths
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QHBoxLayout, QHeaderView, QTableWidgetItem, QFileDialog
from qfluentwidgets import LineEdit, PrimaryPushButton, MessageBoxBase, SubtitleLabel, MessageBox, InfoBar, \
    InfoBarPosition, TableWidget, PasswordLineEdit, ComboBox, PlainTextEdit, StrongBodyLabel, PushButton

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
        btn_run.clicked.connect(lambda: self.run())
        btn_stop.clicked.connect(lambda: self.stop())

        # 保存路劲组件
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(10)
        self.dir_lineEdit = LineEdit()
        self.dir_lineEdit.setReadOnly(True)
        self.dir_lineEdit.setText(QStandardPaths.writableLocation(QStandardPaths.DesktopLocation))  # 设置为桌面路劲
        btn_choose_dir = PushButton("修改保存目录")
        btn_choose_dir.clicked.connect(lambda: self.choose_dir())
        dir_layout.addWidget(self.dir_lineEdit)
        dir_layout.addWidget(btn_choose_dir)

        # 日志显示文本框
        self.log_edit = PlainTextEdit()
        self.log_edit.setReadOnly(True)

        # 添加至总布局
        self.vBoxLayout.addLayout(group_layout)
        self.vBoxLayout.addLayout(dir_layout)
        self.vBoxLayout.addWidget(self.log_edit)

        # 更新列表
        self.update_combo(YamlUtil("app/config/device_templates.yml", {"devices": []}).get_keys())

    def run(self):
        if not os.path.exists(self.dir_lineEdit.text()):
            if self.show_message_dialog("开始运行", "保存目录不存在，是否重新选择？"):
                self.choose_dir()
            else:
                return
        if os.path.exists(self.dir_lineEdit.text()):
            self.log_edit.clear()
            self.run_command()

    def stop(self):
        pass

    def update_combo(self, data):
        self.group_combo.clear()
        self.group_combo.addItems(data)

    def run_command(self):
        try:
            device_group = self.group_combo.currentText()
            device_list = YamlUtil("app/config/device_templates.yml", {"devices": []}).get_keys()
            self.setup_logging()
        except Exception as e:
            print(e)

    def setup_logging(self):
        """配置双日志输出（文件+PlainTextEdit组件）"""
        print(os.path.join(self.dir_lineEdit.text(), self.group_combo.currentText()))
        os.makedirs(os.path.join(self.dir_lineEdit.text(), self.group_combo.currentText()), exist_ok=True)
        log_file = os.path.join(self.dir_lineEdit.text(), self.group_combo.currentText(), '巡检日志.log')

        # 清除默认配置
        logging.root.handlers = []

        # 创建处理器
        file_handler = logging.FileHandler(str(log_file), encoding='utf-8')
        text_edit_handler = PlainTextEditHandler(self.log_edit)

        # 设置格式
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        text_edit_handler.setFormatter(formatter)

        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(text_edit_handler)

    def choose_dir(self):
        desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        folder_path = QFileDialog.getExistingDirectory(self, "修改保存目录", desktop_path)
        if folder_path:
            self.dir_lineEdit.setText(folder_path)
        elif os.path.exists(self.dir_lineEdit.text()):
            self.warning_info("修改保存目录", "未选择路径，保持原路径！")
        else:
            self.error_info("修改保存目录", "未选择路径，原路径不可用，请重新选择！")

    def show_message_dialog(self, title, content):
        w = MessageBox(title, content, self.window())
        w.setContentCopyable(True)
        if w.exec():
            return True
        else:
            return False

    def error_info(self, title, content):
        InfoBar.error(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )

    def warning_info(self, title, content):
        InfoBar.warning(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.TOP,
            duration=3000,
            parent=self
        )


class PlainTextEditHandler(Handler, QObject):
    append_log = pyqtSignal(str)  # 定义信号用于跨线程安全更新UI

    def __init__(self, text_edit):
        Handler.__init__(self)
        QObject.__init__(self)
        self.text_edit = text_edit
        self.append_log.connect(self._append_text)  # 绑定信号到槽

    def emit(self, record):
        msg = self.format(record)
        self.append_log.emit(msg)  # 通过信号触发UI更新

    @pyqtSlot(str)
    def _append_text(self, msg):
        self.text_edit.appendPlainText(msg)  # 实际更新UI的方法
