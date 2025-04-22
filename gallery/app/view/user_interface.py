# coding:utf-8
from typing import List
from urllib.response import addclosehook

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QAbstractItemView, QFormLayout, QDialog, QHeaderView, \
    QTableWidgetItem, QTableWidget
from netmiko.cli_tools.helpers import update_device_params
from netmiko.ssh_dispatcher import CLASS_MAPPER_BASE
from qfluentwidgets import LineEdit, ComboBox, PushButton, BodyLabel, CardWidget, ListWidget, PrimaryPushButton, \
    StrongBodyLabel, MessageBoxBase, SubtitleLabel, MessageBox, InfoBar, InfoBarPosition, TextEdit, TableWidget

from .gallery_interface import GalleryInterface
from ..util.yaml_util import YamlUtil


class UserInterface(GalleryInterface):
    """ 命令模板页面 """

    def __init__(self, parent=None):
        super().__init__(
            title="用户模板",
            subtitle='配置用户登录的账户模板',
            parent=parent
        )
        self.setObjectName('userInterface')


        # 用户列表
        self.user_table=TableWidget()
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.verticalHeader().hide()
        self.user_table.setBorderRadius(8)
        self.user_table.setBorderVisible(True)
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.user_table.setColumnCount(2)
        self.user_table.setHorizontalHeaderLabels(["模板名称","用户名"])

        self.user_table.doubleClicked.connect(lambda :print(self.get_user_row_data(self.user_table.currentRow())))

        # 按钮
        btn_layout=QHBoxLayout()
        btn_add=PrimaryPushButton("新建用户")
        btn_edit=PrimaryPushButton("编辑用户")
        btn_remove=PrimaryPushButton("删除用户")

        btn_add.clicked.connect(lambda: self.add_user())
        btn_edit.clicked.connect(lambda :self.edit_user())
        btn_remove.clicked.connect(lambda: self.remove_user())

        btn_layout.addStretch(1)
        btn_layout.addWidget(btn_add,1)
        btn_layout.addWidget(btn_edit,1)
        btn_layout.addWidget(btn_remove,1)
        btn_layout.addStretch(1)


        # 添加组建到窗口
        self.vBoxLayout.addWidget(self.user_table)
        self.vBoxLayout.addLayout(btn_layout)

    def add_user(self):
        w = CustomMessageBox("新建用户", parent=self.window())
        if w.exec():
            print("点击了确定")

    def edit_user(self):
        w = CustomMessageBox("编辑用户", parent=self.window())
        if w.exec():
            print("点击了确定")
    def remove_user(self):
        pass

    def add_user_row(self,data:list[str]):
        new_row_index = self.user_table.rowCount()  # 获取当前总行数
        self.user_table.insertRow(new_row_index)  # 在末尾插入新行
        if len(data)==self.user_table.columnCount():
            for col in range(len(data)):
                item = QTableWidgetItem(data[col])
                item.setTextAlignment(Qt.AlignCenter)
                self.user_table.setItem(new_row_index, col, item)

    def get_user_row_data(self, target_row):
        row_data = []
        for col in range(self.user_table.columnCount()):
            item = self.user_table.item(target_row, col)
            row_data.append(item.text() if item else "")
        return row_data


class CustomMessageBox(MessageBoxBase):
    """ 文本输入消息框 """

    def __init__(self, title_text, data=None, parent=None):
        super().__init__(parent)
        if data is None:
            data = ["", "", ""]
        self.title_label = SubtitleLabel(title_text, self)

        self.templates_lineEdit = LineEdit(self)
        self.templates_lineEdit.setPlaceholderText("模板名称")
        self.templates_lineEdit.setClearButtonEnabled(True)

        self.user_lineEdit = LineEdit(self)
        regex = QRegExp("[a-zA-Z0-9\\s]+")
        validator = QRegExpValidator(regex)
        self.user_lineEdit.setValidator(validator)
        self.user_lineEdit.setPlaceholderText("用户名")
        self.user_lineEdit.setClearButtonEnabled(True)

        self.password_lineEdit = LineEdit(self)
        regex = QRegExp("[a-zA-Z0-9\\s]+")
        validator = QRegExpValidator(regex)
        self.password_lineEdit.setValidator(validator)
        self.password_lineEdit.setPlaceholderText("密码")
        self.password_lineEdit.setClearButtonEnabled(True)

        # 如果有数据，则添加进布局
        if data is not None:
            self.templates_lineEdit.setText(data[0])
            self.user_lineEdit.setText(data[1])
            self.password_lineEdit.setText(data[2])

        # 添加组件到布局
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.templates_lineEdit)
        self.viewLayout.addWidget(self.user_lineEdit)
        self.viewLayout.addWidget(self.password_lineEdit)

        # 修改按钮文本
        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(360)