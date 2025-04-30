# coding:utf-8

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPainterPath, QLinearGradient
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import ScrollArea, isDarkTheme, FluentIcon

from ..common.config import HELP_URL, REPO_URL, EXAMPLE_URL, FEEDBACK_URL
from ..common.style_sheet import StyleSheet
from ..components.link_card import LinkCardView
from ..components.sample_card import SampleCardView


class BannerWidget(QWidget):
    """ 横幅小部件 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedHeight(336)

        self.vBoxLayout = QVBoxLayout(self)
        self.galleryLabel = QLabel('NetForge', self)
        self.banner = QPixmap(':/gallery/images/header.png')
        self.linkCardView = LinkCardView(self)

        self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 20, 0, 0)
        self.vBoxLayout.addWidget(self.galleryLabel)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.linkCardView.addCard(
            ':/gallery/images/logo.png',
            '开始',
            '帮助您快速了解软件功能。',
            HELP_URL
        )

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            '项目源码',
            '通过解读并修改源码提高便捷性，提高您的工作效率。',
            REPO_URL
        )

        self.linkCardView.addCard(
            FluentIcon.CODE,
            '功能演示',
            '了解程序的功能，将您的工作效率提高至999999999999999%',
            EXAMPLE_URL
        )

        self.linkCardView.addCard(
            FluentIcon.FEEDBACK,
            '提供反馈',
            '通过提供反馈帮助我们改进NetForge的功能。',
            FEEDBACK_URL
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        w, h = self.width(), self.height()
        path.addRoundedRect(QRectF(0, 0, w, h), 10, 10)
        path.addRect(QRectF(0, h - 50, 50, 50))
        path.addRect(QRectF(w - 50, 0, 50, 50))
        path.addRect(QRectF(w - 50, h - 50, 50, 50))
        path = path.simplified()

        # 初始线性梯度效应
        gradient = QLinearGradient(0, 0, 0, h)

        # 绘制背景颜色
        if not isDarkTheme():
            gradient.setColorAt(0, QColor(207, 216, 228, 255))
            gradient.setColorAt(1, QColor(207, 216, 228, 0))
        else:
            gradient.setColorAt(0, QColor(0, 0, 0, 255))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.fillPath(path, QBrush(gradient))

        # 绘制横幅图像
        pixmap = self.banner.scaled(
            self.size(), transformMode=Qt.SmoothTransformation)
        painter.fillPath(path, QBrush(pixmap))


class HomeInterface(ScrollArea):
    """ 主页页面 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.banner = BannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__init_widget()
        self.load_samples()

    def __init_widget(self):
        self.view.setObjectName('view')
        self.setObjectName('homeInterface')
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

    def load_samples(self):
        """ 加载样本 """

        # 快速跳转
        quick_jump_view = SampleCardView('快速跳转', self.view)
        quick_jump_view.addSampleCard(
            icon=":/gallery/images/controls/Run.png",
            title="运行命令",
            content="运行预设的配置命令",
            routeKey="runInterface",
            index=0
        )
        quick_jump_view.addSampleCard(
            icon=":/gallery/images/controls/Device.png",
            title="设备组",
            content="配置需要执行操作的设备组",
            routeKey="deviceInterface",
            index=0
        )
        quick_jump_view.addSampleCard(
            icon=":/gallery/images/controls/Command.png",
            title="命令模板",
            content="配置设备要执行的命令模板",
            routeKey="commandInterface",
            index=0
        )
        quick_jump_view.addSampleCard(
            icon=":/gallery/images/controls/User.png",
            title="用户模板",
            content="配置登录设备的用户模板",
            routeKey="userInterface",
            index=0
        )
        self.vBoxLayout.addWidget(quick_jump_view)

