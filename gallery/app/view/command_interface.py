# coding:utf-8

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import LineEdit, ComboBox, PushButton, BodyLabel, CardWidget, ListWidget, PrimaryPushButton, \
    StrongBodyLabel

from .gallery_interface import GalleryInterface


class CommandInterface(GalleryInterface):
    """ Date time interface """

    def __init__(self, parent=None):
        super().__init__(
            title="命令模板",
            subtitle='配置设备要执行的命令模板',
            parent=parent
        )
        self.setObjectName('commandInterface')

        # 配置组管理
        group_layout = QHBoxLayout()
        group_layout.setSpacing(10)
        group_combo = ComboBox()
        # group_combo.currentIndexChanged.connect(self.switch_config_group)
        btn_new = PushButton("新建配置组")
        btn_del = PushButton("删除当前组")
        group_layout.addWidget(group_combo, 6)
        group_layout.addWidget(btn_new, 1)
        group_layout.addWidget(btn_del, 1)

        # 基础设置
        form_card = CardWidget()
        form_card.setBorderRadius(8)  # 圆角半径
        form_card.setProperty('lightBackground', '#FFFFFF')  # 浅色模式背景
        form_card.setProperty('darkBackground', '#2B2B2B')  # 深色模式背景
        form_layout = QHBoxLayout(form_card)
        form_layout.setSpacing(5)
        device_type_edit = ComboBox()
        send_command_edit = LineEdit()
        form_layout.addWidget(BodyLabel("设备类型："))
        form_layout.addWidget(device_type_edit, 5)
        form_layout.addSpacing(30)
        form_layout.addWidget(BodyLabel("结束符号："))
        form_layout.addWidget(send_command_edit, 1)

        # 命令布局
        command_layout = QHBoxLayout()

        # 巡检命令组件
        inspection_card = CardWidget()
        inspection_card.setBorderRadius(8)  # 圆角半径
        inspection_card.setProperty('lightBackground', '#FFFFFF')  # 浅色模式背景
        inspection_card.setProperty('darkBackground', '#2B2B2B')  # 深色模式背景
        inspection_layout = QVBoxLayout(inspection_card)

        inspection_list = ListWidget()
        inspection_list.addItems(["1", "2", "3"])
        inspection_list.setSelectionMode(ListWidget.MultiSelection)

        inspection_btn_add = PrimaryPushButton("添加命令")
        inspection_btn_remove = PrimaryPushButton("删除选中")
        inspection_btn_layout = QHBoxLayout()
        inspection_btn_layout.addWidget(inspection_btn_add)
        inspection_btn_layout.addWidget(inspection_btn_remove)

        inspection_layout.addWidget(StrongBodyLabel("巡检命令"), 0, Qt.AlignCenter)
        inspection_layout.addWidget(inspection_list)
        inspection_layout.addLayout(inspection_btn_layout)

        # 备份命令组件
        backup_card = CardWidget()
        backup_card.setBorderRadius(8)  # 圆角半径
        backup_card.setProperty('lightBackground', '#FFFFFF')  # 浅色模式背景
        backup_card.setProperty('darkBackground', '#2B2B2B')  # 深色模式背景
        backup_layout = QVBoxLayout(backup_card)

        backup_list = ListWidget()
        backup_list.addItems(["1", "2", "3"])
        backup_list.setSelectionMode(ListWidget.MultiSelection)

        backup_btn_add = PrimaryPushButton("添加命令")
        backup_btn_remove = PrimaryPushButton("删除选中")
        backup_btn_layout = QHBoxLayout()
        backup_btn_layout.addWidget(backup_btn_add)
        backup_btn_layout.addWidget(backup_btn_remove)

        backup_layout.addWidget(StrongBodyLabel("备份命令"), 0, Qt.AlignCenter)
        backup_layout.addWidget(backup_list)
        backup_layout.addLayout(backup_btn_layout)

        # 添加命令组件至命令布局
        command_layout.addWidget(inspection_card)
        command_layout.addWidget(backup_card)

        # 将布局添加至窗口
        self.vBoxLayout.addLayout(group_layout)
        self.vBoxLayout.addWidget(form_card)
        self.vBoxLayout.addLayout(command_layout)
