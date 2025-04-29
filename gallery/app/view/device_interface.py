# coding:utf-8

from PyQt5.QtCore import Qt, QRegExp, pyqtSignal
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QHBoxLayout, QHeaderView, QTableWidgetItem
from qfluentwidgets import LineEdit, PrimaryPushButton, MessageBoxBase, SubtitleLabel, MessageBox, InfoBar, \
    InfoBarPosition, TableWidget, ComboBox

from .gallery_interface import GalleryInterface
from ..util.yaml_util import YamlUtil


class DeviceInterface(GalleryInterface):
    """ 设备组页面 """
    send_to_run_page_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(
            title="设备组",
            subtitle='配置需要执行操作的设备组',
            parent=parent
        )
        self.setObjectName('deviceInterface')
        # 加载配置文件
        self.device_yaml = YamlUtil("app/config/device_templates.yml", {"devices": []})

        # 配置组管理
        group_layout = QHBoxLayout()
        group_layout.setSpacing(10)
        self.group_combo = ComboBox()
        self.group_combo.currentIndexChanged.connect(  # 绑定下拉框的值发生变化更新选中的模板数据
            lambda: self.update_device_table(self.group_combo.currentText()))
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
        self.device_table.setHorizontalHeaderLabels(["设备地址", "端口号", "设备名称", "命令模板", "用户模板"])

        self.device_table.doubleClicked.connect(lambda: self.edit_device())

        # 按钮
        btn_layout = QHBoxLayout()
        btn_add = PrimaryPushButton("添加设备")
        btn_edit = PrimaryPushButton("编辑设备")
        btn_remove = PrimaryPushButton("删除设备")

        btn_add.clicked.connect(lambda: self.add_device())
        btn_edit.clicked.connect(lambda: self.edit_device())
        btn_remove.clicked.connect(lambda: self.remove_device())

        btn_layout.addStretch(1)
        btn_layout.addWidget(btn_add, 1)
        btn_layout.addWidget(btn_edit, 1)
        btn_layout.addWidget(btn_remove, 1)
        btn_layout.addStretch(1)

        # 添加组建到窗口
        self.vBoxLayout.addLayout(group_layout)
        self.vBoxLayout.addWidget(self.device_table)
        self.vBoxLayout.addLayout(btn_layout)

        self.update_group_combo(self.device_yaml.get_keys()[0])

    def add_device_row(self, data: list[str]):
        new_row_index = self.device_table.rowCount()  # 获取当前总行数
        self.device_table.insertRow(new_row_index)  # 在末尾插入新行
        if len(data) == self.device_table.columnCount():
            for col in range(len(data)):
                item = QTableWidgetItem(data[col])
                item.setTextAlignment(Qt.AlignCenter)
                self.device_table.setItem(new_row_index, col, item)

    def update_group_combo(self, current_text):
        self.group_combo.clear()
        device_group = self.device_yaml.get_keys()
        self.group_combo.addItems(device_group)  # 添加列表至设备组下拉框
        self.send_to_run_page_signal.emit(device_group)  # 添加列表至运行页面
        self.group_combo.setCurrentText(current_text)  # 选中第一个
        self.update_device_table(current_text)

    def update_device_table(self, device_group: str):
        if device_group not in self.device_yaml.get_keys():
            return
        # 修改设备列表
        device_msg = self.device_yaml.get([device_group])
        self.device_table.setRowCount(0)
        for i in device_msg:
            self.add_device_row(
                [i.get("host"), i.get("port"), i.get("device_name"), i.get("command_template"), i.get("user_template")])

    def add_device_group(self):
        w = CustomDevicesMessageBox(self.device_yaml.get_keys(), parent=self.window())
        if w.exec():
            self.device_yaml.update([w.lineEdit.text().strip()], [])
            self.update_group_combo(w.lineEdit.text().strip())

    def remove_device_group(self):
        if self.group_combo.count() <= 1:
            self.error_info("删除设备组", "剩最后一个了，不准删！")
            return
        if self.show_message_dialog("删除设备组", "你确定？删了就回不来了哦！"):
            self.device_yaml.delete(self.group_combo.text().strip())
            self.update_group_combo(self.device_yaml.get_keys()[0])

    def add_device(self):
        if not self.check_data('添加设备'):
            return
        device_group = self.group_combo.currentText()
        w = CustomDeviceMessageBox("添加设备", parent=self.window())
        if w.exec():
            data = self.device_yaml.get([device_group])
            new_data = {"host": w.host_lineEdit.text().strip(), "port": w.port_lineEdit.text().strip(),
                        "device_name": w.device_name_lineEdit.text().strip(),
                        "command_template": w.command_combo.currentText().strip(),
                        "user_template": w.user_combo.currentText().strip()}
            data.append(new_data)
            self.device_yaml.update([device_group], data)
            self.update_device_table(device_group)

    def edit_device(self):
        if not self.check_data('编辑设备'):
            return
        item_index = self.device_table.currentRow()
        if item_index < 0:
            self.error_info("编辑设备", "请选择待编辑设备")
            return
        device_group = self.group_combo.currentText()
        data = [self.device_table.item(item_index, 0).text(),
                self.device_table.item(item_index, 1).text(),
                self.device_table.item(item_index, 2).text(),
                self.device_table.item(item_index, 3).text(),
                self.device_table.item(item_index, 4).text()]
        if data[3] not in YamlUtil("app/config/command_templates.yml").get_keys():
            data[3] = ""
            self.warning_info("编辑设备", "命令模板丢失，请重新选择！")
        if data[4] not in YamlUtil("app/config/user_templates.yml").get_keys():
            data[4] = ""
            self.warning_info("编辑设备", "用户模板丢失，请重新选择！")
        w = CustomDeviceMessageBox("编辑设备", data=data, parent=self.window())
        if w.exec():
            data = self.device_yaml.get([device_group])
            new_data = {"host": w.host_lineEdit.text().strip(), "port": w.port_lineEdit.text().strip(),
                        "device_name": w.device_name_lineEdit.text().strip(),
                        "command_template": w.command_combo.currentText().strip(),
                        "user_template": w.user_combo.currentText().strip()}
            data[item_index] = new_data
            self.device_yaml.update([device_group], data)
            self.update_device_table(device_group)

    def remove_device(self):
        item_index = self.device_table.currentRow()
        if item_index < 0:
            self.error_info("删除设备", "请选择待删除设备")
            return
        if self.show_message_dialog("删除设备", "你确定要删除吗？"):
            device_group = self.group_combo.currentText()
            data = self.device_yaml.get([device_group])
            del data[item_index]
            self.device_yaml.update([device_group], data)
            self.update_device_table(device_group)

    def check_data(self, title):
        command_templates = YamlUtil("app/config/command_templates.yml").get_keys()
        user_templates = YamlUtil("app/config/user_templates.yml").get_keys()
        if command_templates is None or len(command_templates) <= 0:
            self.error_info(title, "请先创建命令模板！")
            return False
        if user_templates is None or len(user_templates) <= 0:
            self.error_info(title, "请先创建用户模板！")
            return False
        return True

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


class CustomDevicesMessageBox(MessageBoxBase):
    """ 添加模板文本输入消息框 """

    def __init__(self, key_list, parent=None):
        super().__init__(parent)
        self.title_label = SubtitleLabel("新建设备组", self)
        self.lineEdit = LineEdit(self)
        self.lineEdit.setPlaceholderText("输入设备组名称")
        self.lineEdit.setClearButtonEnabled(True)

        # 添加组件到布局
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.lineEdit)

        # 修改按钮文本
        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")

        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(lambda: self.net_yes_button_clicked(key_list))

        self.widget.setMinimumWidth(360)

    def net_yes_button_clicked(self, key_list):
        if self.lineEdit.text() is not None and self.lineEdit.text().strip() != "" and self.validate():
            if self.lineEdit.text().strip() in key_list:
                InfoBar.error(
                    title="新建设备组",
                    content="设备组已存在！",
                    orient=Qt.Horizontal,
                    isClosable=False,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                return
            else:
                self.accept()
        else:
            InfoBar.error(
                title="新建设备组",
                content="设备组不能为空！",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )


class CustomDeviceMessageBox(MessageBoxBase):
    """ 添加设备的消息框 """

    def __init__(self, title, data=None, parent=None):
        command_templates = YamlUtil("app/config/command_templates.yml").get_keys()
        user_templates = YamlUtil("app/config/user_templates.yml").get_keys()
        super().__init__(parent)
        self.title = title
        self.title_label = SubtitleLabel(self.title, self)

        # 设备地址
        self.host_lineEdit = LineEdit(self)
        ipv4_regex = r"((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])"
        ipv6_regex = r"(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(([0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4})?::(([0-9a-fA-F]{1,4}:){1,7}[0-9a-fA-F]{1,4})?)"
        regex = QRegExp(f"^({ipv4_regex}|{ipv6_regex})$")
        validator = QRegExpValidator(regex)
        self.host_lineEdit.setValidator(validator)
        self.host_lineEdit.setPlaceholderText("设备地址（必填）")
        self.host_lineEdit.setClearButtonEnabled(True)

        # 端口号
        self.port_lineEdit = LineEdit(self)
        regex = QRegExp("^(0|[1-9]\\d{0,3}|[1-5]\\d{4}|6[0-4]\\d{3}|65[0-4]\\d{2}|655[0-2]\\d|6553[0-5])$")
        validator = QRegExpValidator(regex)
        self.port_lineEdit.setValidator(validator)
        self.port_lineEdit.setPlaceholderText("端口号（22）")
        self.port_lineEdit.setClearButtonEnabled(True)

        # 设备名称
        self.device_name_lineEdit = LineEdit(self)
        self.device_name_lineEdit.setPlaceholderText("设备名称")
        self.device_name_lineEdit.setClearButtonEnabled(True)

        # 命令模板
        self.command_combo = ComboBox()
        self.command_combo.addItems(command_templates)

        # 用户模板
        self.user_combo = ComboBox()
        self.user_combo.addItems(user_templates)

        # 修改值
        if data is not None:
            self.host_lineEdit.setText(data[0])
            self.port_lineEdit.setText(data[1])
            self.device_name_lineEdit.setText(data[2])
            if data[3] != "":
                self.command_combo.setText(data[3])
            if data[4] != "":
                self.user_combo.setText(data[4])

        # 添加组件到布局
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.host_lineEdit)
        self.viewLayout.addWidget(self.port_lineEdit)
        self.viewLayout.addWidget(self.device_name_lineEdit)
        self.viewLayout.addWidget(self.command_combo)
        self.viewLayout.addWidget(self.user_combo)

        # 修改按钮文本
        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")

        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(lambda: self.net_yes_button_clicked())

        self.widget.setMinimumWidth(360)

    def net_yes_button_clicked(self):
        if self.host_lineEdit is None or self.host_lineEdit.text().strip() == "":
            InfoBar.error(
                title=self.title,
                content="设备地址不能为空！",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
        elif self.port_lineEdit.text() is None or self.port_lineEdit.text().strip() == "":
            self.port_lineEdit.setText("22")
        if self.validate():
            self.accept()
