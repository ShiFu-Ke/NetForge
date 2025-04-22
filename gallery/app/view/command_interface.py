# coding:utf-8

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QAbstractItemView
from netmiko.ssh_dispatcher import CLASS_MAPPER_BASE
from qfluentwidgets import LineEdit, ComboBox, PushButton, BodyLabel, CardWidget, ListWidget, PrimaryPushButton, \
    StrongBodyLabel, MessageBoxBase, SubtitleLabel, MessageBox, InfoBar, InfoBarPosition

from .gallery_interface import GalleryInterface
from ..util.yaml_util import YamlUtil


class CommandInterface(GalleryInterface):
    """ 命令模板页面 """

    def __init__(self, parent=None):
        super().__init__(
            title="命令模板",
            subtitle='配置设备要执行的命令模板',
            parent=parent
        )
        self.setObjectName('commandInterface')

        # 加载配置文件
        default_data = {'huawei_base': {'device_type': 'huawei',
                                        'inspection_commands': ['screen-length 0 temporary', 'display version',
                                                                'display device', 'display interface brief',
                                                                'display ip interface brief', 'display power',
                                                                'display fan', 'display cpu-usage'],
                                        'backup_commands': ['display current-configuration'], 'send_command': '>'}}
        self.command_yaml = YamlUtil("app/config/command_templates.yml", default_data)

        # 配置组管理
        group_layout = QHBoxLayout()
        group_layout.setSpacing(10)
        self.group_combo = ComboBox()
        self.group_combo.currentIndexChanged.connect(  # 绑定下拉框的值发生变化更新选中的模板数据
            lambda: self.update_select_data(self.group_combo.currentText()))
        btn_new = PushButton("新建模板")
        btn_del = PushButton("删除模板")
        group_layout.addWidget(self.group_combo, 6)
        group_layout.addWidget(btn_new, 1)
        group_layout.addWidget(btn_del, 1)
        btn_new.clicked.connect(lambda: self.add_config_group())
        btn_del.clicked.connect(lambda: self.remove_config_group())

        # 基础设置
        form_card = CardWidget()
        form_card.setBorderRadius(8)  # 圆角半径
        form_card.setProperty('lightBackground', '#FFFFFF')  # 浅色模式背景
        form_card.setProperty('darkBackground', '#2B2B2B')  # 深色模式背景
        form_layout = QHBoxLayout(form_card)
        form_layout.setSpacing(5)
        self.device_type_combo = ComboBox()
        self.device_type_combo.addItems(sorted(CLASS_MAPPER_BASE.keys(), key=str.lower))
        self.device_type_combo.activated.connect(
            lambda: self.command_yaml.update([self.group_combo.currentText(), "device_type"],
                                             self.device_type_combo.currentText()))
        self.send_command_edit = LineEdit()
        self.send_command_edit.setMaxLength(10)
        self.send_command_edit.textChanged.connect(
            lambda: self.command_yaml.update([self.group_combo.currentText(), "send_command"],
                                             self.send_command_edit.text()))
        form_layout.addWidget(BodyLabel("设备类型:"))
        form_layout.addWidget(self.device_type_combo, 1)
        form_layout.addSpacing(50)
        form_layout.addWidget(BodyLabel("结束符号:"))
        form_layout.addWidget(self.send_command_edit, 1)

        # 命令布局
        command_layout = QHBoxLayout()

        # 巡检命令组件
        inspection_card = CardWidget()
        inspection_card.setBorderRadius(8)  # 圆角半径
        inspection_card.setProperty('lightBackground', '#FFFFFF')  # 浅色模式背景
        inspection_card.setProperty('darkBackground', '#2B2B2B')  # 深色模式背景
        inspection_layout = QVBoxLayout(inspection_card)

        self.inspection_list = ListWidget()
        self.inspection_list.setSelectionMode(ListWidget.MultiSelection)
        self.inspection_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.inspection_list.setDragEnabled(True)
        self.inspection_list.setAcceptDrops(True)
        self.inspection_list.model().rowsMoved.connect(
            lambda: self.command_yaml.update([self.group_combo.currentText(), "inspection_commands"],
                                             [self.inspection_list.item(i).text() for i in
                                              range(self.inspection_list.count())]))

        inspection_btn_add = PrimaryPushButton("添加命令")
        inspection_btn_remove = PrimaryPushButton("删除选中")
        inspection_btn_add.clicked.connect(lambda: self.add_inspection_command())
        inspection_btn_remove.clicked.connect(lambda: self.remove_inspection_command())
        inspection_btn_layout = QHBoxLayout()
        inspection_btn_layout.addWidget(inspection_btn_add)
        inspection_btn_layout.addWidget(inspection_btn_remove)

        inspection_layout.addWidget(StrongBodyLabel("巡检命令"), 0, Qt.AlignCenter)
        inspection_layout.addWidget(self.inspection_list)
        inspection_layout.addLayout(inspection_btn_layout)

        # 备份命令组件
        backup_card = CardWidget()
        backup_card.setBorderRadius(8)  # 圆角半径
        backup_card.setProperty('lightBackground', '#FFFFFF')  # 浅色模式背景
        backup_card.setProperty('darkBackground', '#2B2B2B')  # 深色模式背景
        backup_layout = QVBoxLayout(backup_card)

        self.backup_list = ListWidget()
        self.backup_list.setSelectionMode(ListWidget.MultiSelection)
        self.backup_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.backup_list.setDragEnabled(True)
        self.backup_list.setAcceptDrops(True)
        self.backup_list.model().rowsMoved.connect(
            lambda: self.command_yaml.update([self.group_combo.currentText(), "backup_commands"],
                                             [self.backup_list.item(i).text() for i in
                                              range(self.backup_list.count())]))

        backup_btn_add = PrimaryPushButton("添加命令")
        backup_btn_remove = PrimaryPushButton("删除选中")
        backup_btn_add.clicked.connect(lambda: self.add_backup_command())
        backup_btn_remove.clicked.connect(lambda: self.remove_backup_command())
        backup_btn_layout = QHBoxLayout()
        backup_btn_layout.addWidget(backup_btn_add)
        backup_btn_layout.addWidget(backup_btn_remove)

        backup_layout.addWidget(StrongBodyLabel("备份命令"), 0, Qt.AlignCenter)
        backup_layout.addWidget(self.backup_list)
        backup_layout.addLayout(backup_btn_layout)

        # 添加命令组件至命令布局
        command_layout.addWidget(inspection_card)
        command_layout.addWidget(backup_card)

        # 将布局添加至窗口
        self.vBoxLayout.addLayout(group_layout)
        self.vBoxLayout.addWidget(form_card)
        self.vBoxLayout.addLayout(command_layout)

        # 数据更新
        self.update_group_combo(self.command_yaml.get_keys()[0])

    def add_config_group(self):
        w = CustomMessageBox("新建命令模板", "输入命令模板名称",is_zh=True,parent=self.window())
        if w.exec():
            if w.lineEdit.text() in self.command_yaml.get_keys():
                InfoBar.error(
                    title="新建模板",
                    content="模板名称已存在！",
                    orient=Qt.Horizontal,
                    isClosable=False,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                return
            if w.lineEdit.text() is None or w.lineEdit.text().strip()=="":
                InfoBar.warning(
                    title="新建模板",
                    content="模板名称不能为空！",
                    orient=Qt.Horizontal,
                    isClosable=False,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                return
            new_data = {'device_type': 'huawei', 'inspection_commands': [], 'backup_commands': [], 'send_command': ''}
            self.command_yaml.update([w.lineEdit.text()], new_data)
            self.update_group_combo(w.lineEdit.text())

    def remove_config_group(self):
        if self.group_combo.count() <= 1:
            InfoBar.error(
                title="删除模板",
                content="剩最后一个了，不准删！",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return
        if self.show_message_dialog("删除模板", "你确定？删了就回不来了哦！"):
            self.command_yaml.delete(self.group_combo.text())
            self.update_group_combo(self.command_yaml.get_keys()[0])

    def add_inspection_command(self):
        w = CustomMessageBox("添加巡检命令", "输入命令内容", parent=self.window())
        if w.exec():
            if w.lineEdit.text() is None or w.lineEdit.text().strip()=="":
                InfoBar.warning(
                    title="添加巡检命令",
                    content="命令不能为空！",
                    orient=Qt.Horizontal,
                    isClosable=False,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                return
            self.inspection_list.addItem(w.lineEdit.text())
            self.command_yaml.update([self.group_combo.currentText(), "inspection_commands"],
                                     [self.inspection_list.item(i).text() for i in range(self.inspection_list.count())])

    def add_backup_command(self):
        w = CustomMessageBox("添加备份命令", "输入命令内容", parent=self.window())
        if w.exec():
            if w.lineEdit.text() is None or w.lineEdit.text().strip()=="":
                InfoBar.warning(
                    title="添加备份命令",
                    content="命令不能为空！",
                    orient=Qt.Horizontal,
                    isClosable=False,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                return
            self.backup_list.addItem(w.lineEdit.text())
            self.command_yaml.update([self.group_combo.currentText(), "backup_commands"],
                                     [self.backup_list.item(i).text() for i in range(self.backup_list.count())])

    def remove_inspection_command(self):
        if self.show_message_dialog("删除模板", "你确定？删了就回不来了哦！"):
            selected_items = self.inspection_list.selectedItems()
            for item in reversed(selected_items):
                row = self.inspection_list.row(item)
                taken_item = self.inspection_list.takeItem(row)
                del taken_item
            self.command_yaml.update([self.group_combo.currentText(), "inspection_commands"],
                                     [self.inspection_list.item(i).text() for i in range(self.inspection_list.count())])

    def remove_backup_command(self):
        if self.show_message_dialog("删除模板", "你确定？删了就回不来了哦！"):
            selected_items = self.backup_list.selectedItems()
            for item in reversed(selected_items):
                row = self.backup_list.row(item)
                taken_item = self.backup_list.takeItem(row)
                del taken_item
            self.command_yaml.update([self.group_combo.currentText(), "backup_commands"],
                                     [self.backup_list.item(i).text() for i in range(self.backup_list.count())])

    def update_group_combo(self, current_text):
        self.group_combo.clear()
        command_templates = self.command_yaml.get_keys()
        self.group_combo.addItems(command_templates)  # 添加数据
        self.group_combo.setCurrentText(current_text)  # 选中第一个
        self.update_select_data(current_text)

    def update_select_data(self, command_templates: str):
        if command_templates not in self.command_yaml.get_keys():
            return

        # 修改硬件类型下拉框选项
        self.device_type_combo.setCurrentText(
            self.command_yaml.get([command_templates, "device_type"]))

        # 修改结束符号
        self.send_command_edit.setText(
            self.command_yaml.get([command_templates, "send_command"]))

        # 修改巡检命令模板
        self.inspection_list.clear()
        inspection_commands = self.command_yaml.get([command_templates, "inspection_commands"])
        if type(inspection_commands) is list:
            self.inspection_list.addItems(inspection_commands)

        # 修改备份命令模板
        self.backup_list.clear()
        backup_commands = self.command_yaml.get([command_templates, "backup_commands"])
        if type(backup_commands) is list:
            self.backup_list.addItems(backup_commands)

    def show_message_dialog(self, title, content):
        w = MessageBox(title, content, self.window())
        w.setContentCopyable(True)
        if w.exec():
            return True
        else:
            return False


class CustomMessageBox(MessageBoxBase):
    """ 文本输入消息框 """

    def __init__(self, title_text, edit_text, is_zh=False,parent=None):
        super().__init__(parent)
        self.title_label = SubtitleLabel(title_text, self)
        self.lineEdit = LineEdit(self)
        if not is_zh:
            regex = QRegExp("[a-zA-Z0-9\\s]+")
            validator = QRegExpValidator(regex)
            self.lineEdit.setValidator(validator)
        self.lineEdit.setPlaceholderText(edit_text)
        self.lineEdit.setClearButtonEnabled(True)

        # 添加组件到布局
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.lineEdit)

        # 修改按钮文本
        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")

        self.widget.setMinimumWidth(360)
