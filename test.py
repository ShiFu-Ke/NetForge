import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QFormLayout, QLineEdit, QListWidget, QPushButton,
                             QComboBox, QInputDialog, QListWidgetItem, QSizePolicy)


class ConfigGroupWidget(QWidget):
    """单个配置组的编辑组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 基础设置
        base_group = QGroupBox("Base Settings")
        form_layout = QFormLayout()
        self.device_type_edit = QLineEdit()
        self.send_command_edit = QLineEdit()
        form_layout.addRow("Device Type:", self.device_type_edit)
        form_layout.addRow("Send Command:", self.send_command_edit)
        base_group.setLayout(form_layout)
        layout.addWidget(base_group)

        # 检查命令列表
        inspection_group = QGroupBox("Inspection Commands (支持多选)")
        inspection_layout = QHBoxLayout()
        self.inspection_list = QListWidget()
        self.inspection_list.setSelectionMode(QListWidget.MultiSelection)
        btn_add = QPushButton("添加命令")
        btn_remove = QPushButton("删除选中")
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_remove)
        btn_layout.addStretch()
        inspection_layout.addWidget(self.inspection_list)
        inspection_layout.addLayout(btn_layout)
        inspection_group.setLayout(inspection_layout)
        layout.addWidget(inspection_group)

        # 连接信号
        btn_add.clicked.connect(self.add_command)
        btn_remove.clicked.connect(lambda: self.remove_commands(self.inspection_list))

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def add_command(self):
        text, ok = QInputDialog.getText(self, '添加命令', '输入CLI命令:')
        if ok and text:
            self.inspection_list.addItem(QListWidgetItem(text))

    def remove_commands(self, list_widget):
        for item in list_widget.selectedItems():
            list_widget.takeItem(list_widget.row(item))


class MultiConfigEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_groups = {}  # 存储所有配置组
        self.current_config = None
        self.initUI()
        self.add_config_group()  # 初始默认配置组

    def initUI(self):
        self.setWindowTitle('多设备配置管理')
        self.setGeometry(300, 300, 800, 600)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 配置组管理
        group_control = QHBoxLayout()
        self.group_combo = QComboBox()
        self.group_combo.currentIndexChanged.connect(self.switch_config_group)
        btn_new = QPushButton("新建配置组")
        btn_del = QPushButton("删除当前组")
        group_control.addWidget(self.group_combo, 3)
        group_control.addWidget(btn_new, 1)
        group_control.addWidget(btn_del, 1)
        main_layout.addLayout(group_control)

        # 配置编辑区域
        self.config_widget = ConfigGroupWidget()
        main_layout.addWidget(self.config_widget)

        # 连接信号
        btn_new.clicked.connect(self.add_config_group)
        btn_del.clicked.connect(self.remove_config_group)

    def add_config_group(self):
        group_name, ok = QInputDialog.getText(
            self, '新建配置组', '输入配置组名称:',
            text=f"huawei_config_{len(self.config_groups) + 1}"
        )
        if ok and group_name:
            if group_name in self.config_groups:
                QMessageBox.warning(self, "警告", "配置组名称已存在！")
                return

            self.config_groups[group_name] = {
                "device_type": "huawei",
                "send_command": ">",
                "inspection_commands": []
            }
            self.group_combo.addItem(group_name)
            self.group_combo.setCurrentText(group_name)

    def remove_config_group(self):
        current = self.group_combo.currentText()
        if current:
            reply = QMessageBox.question(
                self, "确认删除", f"确定要删除配置组 {current} 吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.group_combo.removeItem(self.group_combo.currentIndex())
                del self.config_groups[current]

    def switch_config_group(self):
        group_name = self.group_combo.currentText()
        if group_name in self.config_groups:
            self.current_config = self.config_groups[group_name]
            # 更新界面显示
            self.config_widget.device_type_edit.setText(self.current_config["device_type"])
            self.config_widget.send_command_edit.setText(self.current_config["send_command"])
            self.config_widget.inspection_list.clear()
            for cmd in self.current_config["inspection_commands"]:
                self.config_widget.inspection_list.addItem(QListWidgetItem(cmd))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MultiConfigEditor()
    ex.show()
    sys.exit(app.exec_())