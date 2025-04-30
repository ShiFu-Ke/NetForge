# coding:utf-8
from typing import Tuple

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QHBoxLayout, QHeaderView, QTableWidgetItem
from qfluentwidgets import LineEdit, PrimaryPushButton, MessageBoxBase, SubtitleLabel, MessageBox, InfoBar, \
    InfoBarPosition, TableWidget, PasswordLineEdit

from .gallery_interface import GalleryInterface
from ..util.encryption_util import Encryption
from ..util.yaml_util import YamlUtil


class UserInterface(GalleryInterface):
    """ 命令模板页面 """

    def __init__(self, parent=None):
        super().__init__(
            title="用户模板",
            subtitle='配置登录设备的用户模板',
            parent=parent
        )
        self.setObjectName('userInterface')
        # 加载配置文件
        self.user_yaml = YamlUtil("app/config/user_templates.yml")

        # 用户列表
        self.user_table = TableWidget()
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.verticalHeader().hide()
        self.user_table.setBorderRadius(8)
        self.user_table.setBorderVisible(True)
        self.user_table.setEditTriggers(TableWidget.NoEditTriggers)
        self.user_table.setColumnCount(2)
        self.user_table.setHorizontalHeaderLabels(["模板名称", "用户名"])

        self.user_table.doubleClicked.connect(lambda: self.edit_user())

        # 按钮
        btn_layout = QHBoxLayout()
        btn_add = PrimaryPushButton("新建模板")
        btn_edit = PrimaryPushButton("编辑模板")
        btn_remove = PrimaryPushButton("删除模板")

        btn_add.clicked.connect(lambda: self.add_user())
        btn_edit.clicked.connect(lambda: self.edit_user())
        btn_remove.clicked.connect(lambda: self.remove_user())

        btn_layout.addStretch(1)
        btn_layout.addWidget(btn_add, 1)
        btn_layout.addWidget(btn_edit, 1)
        btn_layout.addWidget(btn_remove, 1)
        btn_layout.addStretch(1)

        # 添加组建到窗口
        self.vBoxLayout.addWidget(self.user_table)
        self.vBoxLayout.addLayout(btn_layout)

        self.update_user_table()

    def add_user(self):
        w = CustomMessageBox("新建用户模板", parent=self.window())
        if w.exec():
            if w.templates_lineEdit.text().strip() in self.user_yaml.get_keys():
                InfoBar.error(
                    title="新建用户模板",
                    content="该用户模板已存在",
                    orient=Qt.Horizontal,
                    isClosable=False,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
            self.user_yaml.update([w.templates_lineEdit.text().strip(), "username"], w.user_lineEdit.text().strip())
            self.user_yaml.update([w.templates_lineEdit.text().strip(), "password"],
                                  Encryption.encrypt(w.password_lineEdit.text().strip()))
            self.update_user_table()

    def edit_user(self):
        item_index = self.user_table.currentRow()
        if item_index < 0:
            InfoBar.warning(
                title="编辑用户模板",
                content="请选择待编辑用户模板",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        user_key = self.user_table.item(item_index, 0).text()
        w = CustomMessageBox("编辑用户模板",
                             data=[user_key, self.user_yaml.get([user_key, "username"], ""), ""],
                             parent=self.window())
        if w.exec():
            self.user_yaml.update([w.templates_lineEdit.text().strip(), "username"], w.user_lineEdit.text().strip())
            self.user_yaml.update([w.templates_lineEdit.text().strip(), "password"],
                                  Encryption.encrypt(w.password_lineEdit.text().strip()))
            self.update_user_table()

    def remove_user(self):
        item_index = self.user_table.currentRow()
        if item_index < 0:
            InfoBar.warning(
                title="删除用户模板",
                content="请选择待删除用户模板",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        if self.show_message_dialog("删除用户模板", "删了设备就登不上去了，你确定？"):
            self.user_yaml.delete(self.user_table.item(item_index, 0).text())
            self.update_user_table()

    def add_user_row(self, data: list[str]):
        new_row_index = self.user_table.rowCount()  # 获取当前总行数
        self.user_table.insertRow(new_row_index)  # 在末尾插入新行
        if len(data) == self.user_table.columnCount():
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

    def update_user_table(self):
        self.user_table.setRowCount(0)
        for i in self.user_yaml.get_keys():
            self.add_user_row([i, self.user_yaml.get([i, "username"])])

    def show_message_dialog(self, title, content):
        w = MessageBox(title, content, self.window())
        w.setContentCopyable(True)
        if w.exec():
            return True
        else:
            return False


class CustomMessageBox(MessageBoxBase):
    """ 文本输入消息框 """

    def __init__(self, title_text, data=None, parent=None):
        super().__init__(parent)
        if data is None:
            data = ["", "", ""]
        self.title_label = SubtitleLabel(title_text, self)

        self.templates_lineEdit = LineEdit(self)
        self.templates_lineEdit.setPlaceholderText("用户模板名称")
        self.templates_lineEdit.setClearButtonEnabled(True)

        self.user_lineEdit = LineEdit(self)
        regex = QRegExp("[a-zA-Z0-9\\s]+")
        validator = QRegExpValidator(regex)
        self.user_lineEdit.setValidator(validator)
        self.user_lineEdit.setPlaceholderText("用户名")
        self.user_lineEdit.setClearButtonEnabled(True)

        self.password_lineEdit = PasswordLineEdit(self)
        self.password_lineEdit.setPlaceholderText("密码")
        self.password_lineEdit.setClearButtonEnabled(True)

        # 如果有数据，则添加进布局,并禁止模板名称编辑,去掉删除按钮
        if data is not None and data[0] != "":
            self.templates_lineEdit.setText(data[0])
            self.user_lineEdit.setText(data[1])
            self.password_lineEdit.setText(data[2])
            self.templates_lineEdit.setReadOnly(True)
            self.templates_lineEdit.setClearButtonEnabled(False)

        # 添加组件到布局
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.templates_lineEdit)
        self.viewLayout.addWidget(self.user_lineEdit)
        self.viewLayout.addWidget(self.password_lineEdit)

        # 修改按钮文本
        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")

        # 修改确认按钮点击槽函数
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self.net_yes_button_clicked)

        self.widget.setMinimumWidth(360)

    def net_yes_button_clicked(self):
        is_not_null, msg = self.data_is_not_null()
        if is_not_null and self.validate():
            self.accept()
        else:
            InfoBar.error(
                title="用户模板",
                content=msg,
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )

    def data_is_not_null(self) -> Tuple[bool, str]:
        if self.templates_lineEdit.text() is None or self.templates_lineEdit.text().strip() == "":
            return False, "用户模板名称不能为空"
        if self.user_lineEdit.text() is None or self.user_lineEdit.text().strip() == "":
            return False, "用户名不能为空"
        if self.password_lineEdit.text() is None or self.password_lineEdit.text().strip() == "":
            return False, "密码不能为空"
        return True, ""
