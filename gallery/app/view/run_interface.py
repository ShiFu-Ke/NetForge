# coding:utf-8
import logging
import os
import threading
from logging import Handler
from time import sleep

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtCore import Qt, QStandardPaths
from PyQt5.QtWidgets import QHBoxLayout, QFileDialog
from netmiko import ConnectHandler, NetMikoTimeoutException, NetMikoAuthenticationException
from qfluentwidgets import LineEdit, PrimaryPushButton, MessageBox, InfoBar, \
    InfoBarPosition, ComboBox, PlainTextEdit, PushButton, StateToolTip

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

        # 定义成员变量
        self.save_path = None
        self.run_thread = None
        self.run_thread_flag = False
        self.stop_state_tooltip = None

        # 设备组管理
        group_layout = QHBoxLayout()
        group_layout.setSpacing(10)
        self.group_combo = ComboBox()
        btn_run = PrimaryPushButton("开始运行")
        btn_stop = PrimaryPushButton("中止运行")
        group_layout.addWidget(self.group_combo, 6)
        group_layout.addWidget(btn_run, 1)
        group_layout.addWidget(btn_stop, 1)
        btn_run.clicked.connect(lambda: self.run())
        btn_stop.clicked.connect(lambda: self.stop())

        # 保存路径组件
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
        self.log_edit.setLineWrapMode(PlainTextEdit.NoWrap)

        # 添加至总布局
        self.vBoxLayout.addLayout(group_layout)
        self.vBoxLayout.addLayout(dir_layout)
        self.vBoxLayout.addWidget(self.log_edit)

        # 更新列表
        self.update_combo(YamlUtil("app/config/device_templates.yml", {"devices": []}).get_keys())

    def run(self):
        if self.run_thread and self.run_thread.is_alive():
            self.error_info("开始运行", "请勿重复运行！")
            return
        if not os.path.exists(self.dir_lineEdit.text()):
            if self.show_message_dialog("开始运行", "保存目录不存在，是否重新选择？"):
                self.choose_dir()
            else:
                return
        if os.path.exists(self.dir_lineEdit.text()):
            self.log_edit.clear()
            self.run_thread_flag = False
            self.run_thread = threading.Thread(target=lambda: self.run_command(), daemon=True)
            self.run_thread.start()

    def stop(self):
        if self.run_thread and self.run_thread.is_alive():
            if not self.run_thread_flag:
                self.run_thread_flag = True
                self.stop_state_tooltip = StateToolTip("中止运行", "正在中止运行~", self.window())
                self.stop_state_tooltip.move(self.stop_state_tooltip.getSuitablePos())
                self.stop_state_tooltip.show()
            else:
                self.error_info("中止运行", "正在中止运行！")
        else:
            self.error_info("中止运行", "未开始运行！")

    def update_combo(self, data):
        self.group_combo.clear()
        self.group_combo.addItems(data)

    def run_command(self):
        user_templates = YamlUtil("app/config/user_templates.yml")
        command_templates = YamlUtil("app/config/command_templates.yml")
        device_list = YamlUtil("app/config/device_templates.yml", {"devices": []}).get([self.group_combo.text()])
        self.setup_logging()
        logging.info(f"{'=' * 15}开始执行操作！{'=' * 15}")
        for i in device_list:
            command = command_templates.data[i["command_template"]]
            user = user_templates.data[i["user_template"]]
            device = {
                "device_name": i["host"] if i["device_name"] == "" else i["device_name"],
                "host": i["host"],
                "port": i["port"],
                "username": user['username'],
                "password": Encryption.decrypt(user['password']),
                "device_type": command["device_type"],
                "inspection_commands": command["inspection_commands"],
                "backup_commands": command["backup_commands"],
                "send_command": command["send_command"],
            }
            self.process_device(device)
            if self.run_thread_flag:
                logging.info(f"{'=' * 15}已中止运行！{'=' * 15}")
                self.stop_state_tooltip.setContent("已中止运行！")
                self.stop_state_tooltip.setState(True)
                sleep(2)
                self.stop_state_tooltip.closedSignal.emit()
                self.stop_state_tooltip.hide()
                self.stop_state_tooltip = None
                return
        logging.info(f"{'=' * 15}所有操作已完成！{'=' * 15}")

    def process_device(self, device):
        """处理单个设备"""
        logging.info(f"{'=' * 15} 开始处理设备: {device["device_name"]}({device["host"]}) {'=' * 15}")
        try:
            # 建立连接
            conn_params = {
                "device_type": device['device_type'],
                "host": device["host"],
                "port": device["port"],
                "username": device["username"],
                "password": device["password"],
                "timeout": 30,
                "fast_cli": False
            }
            with ConnectHandler(**conn_params) as conn:
                # Cisco特权模式处理
                if device['device_type'] == 'cisco_ios':
                    conn.enable()

                # 执行巡检命令
                self.execute_inspection(conn, device['inspection_commands'], device["host"], device['send_command'])
                if self.run_thread_flag:
                    return
                    # 执行备份命令
                backup_data = self.execute_inspection_config_back(conn, device['backup_commands'],
                                                                  device['send_command'])
                if self.run_thread_flag:
                    return

                # 保存配置
                self.save_backup(
                    self.save_path, device['device_name'] + ".log", backup_data, device["host"])
                if self.run_thread_flag:
                    return

        except (NetMikoAuthenticationException, NetMikoTimeoutException) as e:
            logging.error(f"连接失败 [{type(e).__name__}]: {str(e)}\n")
        except Exception as e:
            logging.error(f"未知错误: {str(e)}\n")

    def execute_inspection(self, conn, commands, ip, expect_string):
        """执行巡检命令序列"""
        for cmd in commands:
            if self.run_thread_flag:
                return
            try:
                output = conn.send_command(cmd, expect_string=expect_string)
                if output.strip() != "":
                    logging.info(f"{ip} 执行 [{cmd}] 成功\n输出内容:\n{output}\n{'-' * 80}")
                else:
                    logging.info(f"{ip} 执行 [{cmd}] 成功，无输出内容。")
            except Exception as e:
                logging.warning(f"命令执行失败 [{cmd}]: {str(e)}")

    def execute_inspection_config_back(self, conn, commands, expect_string):
        """执行巡检命令序列"""
        data = ""
        for cmd in commands:
            if self.run_thread_flag:
                return ""
            try:
                output = conn.send_command(cmd, expect_string=expect_string)
                data += f"执行 {cmd}:\n{output}\n\n\n"
            except Exception as e:
                logging.warning(f"命令执行失败 [{cmd}]: {str(e)}")
        return data

    @staticmethod
    def save_backup(path, filename, data, ip):
        """保存配置文件"""
        try:
            full_path = os.path.join(path, filename).replace("/", "\\")
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(data)
            logging.info(f"{ip} 配置已保存至: {full_path}\n")
        except IOError as e:
            logging.error(f"文件保存失败: {str(e)}\n")

    def setup_logging(self):
        """配置双日志输出（文件+PlainTextEdit组件）"""
        self.save_path = os.path.join(self.dir_lineEdit.text(), self.group_combo.currentText())
        os.makedirs(self.save_path, exist_ok=True)
        log_file = os.path.join(self.save_path, '巡检日志.log')

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
        if self.run_thread and self.run_thread.is_alive():
            self.error_info("修改保存目录", "正在运行，请完成后再修改！")
            return
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
