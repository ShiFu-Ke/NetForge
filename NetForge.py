# coding:utf-8
import os
import sys

from PyQt5.QtCore import Qt, QTranslator, QLocale
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from gallery.app.common.config import cfg
from gallery.app.view.main_window import MainWindow


# 启用dpi比例
if cfg.get(cfg.dpiScale) == "Auto":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
else:
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

# 创建应用程序
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

# 翻译默认中文
translator = FluentTranslator(QLocale(QLocale.Chinese, QLocale.China))

app.installTranslator(translator)

# 创建主窗口
w = MainWindow()
w.show()

app.exec_()