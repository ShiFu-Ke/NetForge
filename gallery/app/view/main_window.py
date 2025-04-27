# coding: utf-8

from PyQt5.QtCore import QSize, QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF, InfoBar, InfoBarPosition
from qfluentwidgets import (NavigationItemPosition, FluentWindow, SplashScreen, SystemThemeListener, isDarkTheme)

from .command_interface import CommandInterface
from .gallery_interface import GalleryInterface
from .home_interface import HomeInterface
from .setting_interface import SettingInterface
from .user_interface import UserInterface
from ..common.config import cfg
from ..common.signal_bus import signalBus

from ..common import resource


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # 创建系统主题监听器
        self.themeListener = SystemThemeListener(self)

        # 创建子界面
        self.homeInterface = HomeInterface(self)
        self.commandInterface = CommandInterface(self)
        self.userInterface = UserInterface(self)
        self.settingInterface = SettingInterface(self)

        # 启用亚克力效果
        self.navigationInterface.setAcrylicEnabled(True)
        self.connectSignalToSlot()

        # 向导航界面添加项目
        self.initNavigation()
        self.splashScreen.finish()

        # 启动主题监听器
        self.themeListener.start()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToSampleCard.connect(self.switchToSample)

    def initNavigation(self):

        # 添加导航项目
        self.addSubInterface(self.homeInterface, FIF.HOME, "主页")
        self.navigationInterface.addSeparator()

        pos = NavigationItemPosition.SCROLL

        self.addSubInterface(self.commandInterface, FIF.COMMAND_PROMPT, "命令模板", pos)
        self.addSubInterface(self.userInterface, FIF.PEOPLE, "用户模板", pos)

        # 将自定义小部件添加到底部

        self.addSubInterface(
            self.settingInterface, FIF.SETTING, "设置", NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle('NetForge')
        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # 创建启动画面
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(150, 150))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def closeEvent(self, e):
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        super().closeEvent(e)

    def _onThemeChangedFinished(self):
        super()._onThemeChangedFinished()

        # 重试
        if self.isMicaEffectEnabled():
            QTimer.singleShot(100, lambda: self.windowEffect.setMicaEffect(self.winId(), isDarkTheme()))

    def switchToSample(self, routeKey):
        """ switch to sample """
        interfaces = self.findChildren(GalleryInterface)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackedWidget.setCurrentWidget(w, False)
