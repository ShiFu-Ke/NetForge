# coding:utf-8
from typing import Tuple

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QHBoxLayout, QHeaderView, QTableWidgetItem
from qfluentwidgets import LineEdit, PrimaryPushButton, MessageBoxBase, SubtitleLabel, MessageBox, InfoBar, \
    InfoBarPosition, TableWidget, PasswordLineEdit, ComboBox

from .gallery_interface import GalleryInterface
from ..util.encryption_util import Encryption
from ..util.yaml_util import YamlUtil


class DeviceInterface(GalleryInterface):
    """ 设备组页面 """

    def __init__(self, parent=None):
        super().__init__(
            title="设备组",
            subtitle='配置需要执行操作的设备组',
            parent=parent
        )
        self.setObjectName('deviceInterface')
        # 加载配置文件
        self.user_yaml = YamlUtil("app/config/device_templates.yml")

        # 配置组管理
        group_layout = QHBoxLayout()
        group_layout.setSpacing(10)
        self.group_combo = ComboBox()
        self.group_combo.currentIndexChanged.connect(  # 绑定下拉框的值发生变化更新选中的模板数据
            lambda: self.update_select_data(self.group_combo.currentText()))
        btn_new = PrimaryPushButton("新建设备组")
        btn_del = PrimaryPushButton("删除设备组")
        group_layout.addWidget(self.group_combo, 6)
        group_layout.addWidget(btn_new, 1)
        group_layout.addWidget(btn_del, 1)
        btn_new.clicked.connect(lambda: self.add_device_group())
        btn_del.clicked.connect(lambda: self.remove_device_group())

        # 设备列表
        self.device_table = TableWidget()
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.device_table.verticalHeader().hide()
        self.device_table.setBorderRadius(8)
        self.device_table.setBorderVisible(True)
        self.device_table.setEditTriggers(TableWidget.NoEditTriggers)
        self.device_table.setColumnCount(5)
        self.device_table.setHorizontalHeaderLabels(["设备ip", "端口号", "设备名称", "命令模板", "用户模板"])

        self.device_table.doubleClicked.connect(lambda: self.edit_user())

        # 按钮
        btn_layout = QHBoxLayout()
        btn_add = PrimaryPushButton("添加设备")
        btn_edit = PrimaryPushButton("编辑设备")
        btn_remove = PrimaryPushButton("删除设备")

        btn_add.clicked.connect(lambda: self.add_user())
        btn_edit.clicked.connect(lambda: self.edit_user())
        btn_remove.clicked.connect(lambda: self.remove_user())

        btn_layout.addStretch(1)
        btn_layout.addWidget(btn_add, 1)
        btn_layout.addWidget(btn_edit, 1)
        btn_layout.addWidget(btn_remove, 1)
        btn_layout.addStretch(1)

        # 添加组建到窗口
        self.vBoxLayout.addLayout(group_layout)
        self.vBoxLayout.addWidget(self.device_table)
        self.vBoxLayout.addLayout(btn_layout)
