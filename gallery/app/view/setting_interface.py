# coding:utf-8

from PyQt5.QtCore import Qt, QUrl, QRegExp
from PyQt5.QtGui import QDesktopServices, QRegExpValidator
from PyQt5.QtWidgets import QWidget, QLabel
from qfluentwidgets import FluentIcon as FIF, InfoBarPosition, FlyoutView, FlyoutAnimationType, Flyout, \
    MessageBoxBase, SubtitleLabel, PasswordLineEdit, PrimaryPushButton
from qfluentwidgets import InfoBar
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, OptionsSettingCard, HyperlinkCard,
                            PrimaryPushSettingCard, ScrollArea,
                            ExpandLayout, CustomColorSettingCard,
                            setTheme, setThemeColor, RangeSettingCard)

from ..common.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR, isWin11, RELEASE_URL
from ..common.signal_bus import signalBus
from ..common.style_sheet import StyleSheet
from ..util.update_util import UpdateUtil


class SettingInterface(ScrollArea):
    """ 设置页面 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.settingLabel = QLabel("设置", self)

        # 个性化
        self.personalGroup = SettingCardGroup('个性化', self.scrollWidget)
        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            '云母效应',
            '窗口和表面显示半透明',
            cfg.micaEnabled,
            self.personalGroup
        )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            '应用主题',
            "调整你的应用的外观",
            texts=['亮', '暗', '使用系统设置'],
            parent=self.personalGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FIF.PALETTE,
            '主题色',
            '调整你的应用的主题色',
            self.personalGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            "界面缩放",
            "调整小部件和字体的大小",
            texts=["100%", "125%", "150%", "175%", "200%", "使用系统设置"],
            parent=self.personalGroup
        )
        self.blurRadiusCard = RangeSettingCard(
            cfg.blurRadius,
            FIF.ALBUM,
            '亚克力磨砂半径',
            '磨砂半径越大，图像越模糊',
            self.personalGroup
        )

        # 软件更新
        self.updateSoftwareGroup = SettingCardGroup("软件更新", self.scrollWidget)
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            '在应用程序启动时检查更新',
            '新版本将更加稳定并拥有更多功能（建议启用此选项）',
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.updateSoftwareGroup
        )

        # 应用
        self.aboutGroup = SettingCardGroup('关于', self.scrollWidget)
        self.helpCard = HyperlinkCard(
            HELP_URL,
            '打开帮助页面',
            FIF.HELP,
            '帮助',
            '发现新功能并学习有关PyQt Fluent Widgets的有用提示',
            self.aboutGroup
        )
        self.feedbackCard = PrimaryPushSettingCard(
            '提供反馈',
            FIF.FEEDBACK,
            '提供反馈',
            '通过提供反馈帮助我们改进PyQt Fluent小部件',
            self.aboutGroup
        )

        self.aboutCard = PrimaryPushSettingCard(
            '检查更新',
            FIF.INFO,
            '关于',
            '© ' + '版权' + f" {YEAR}, {AUTHOR}. " + '版本' + " " + VERSION,
            self.aboutGroup
        )

        self.__initWidget()

        # 检查更新
        if cfg.get(cfg.checkUpdateAtStartUp):
            self.check_update()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # 初始化样式表
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        self.micaCard.setEnabled(isWin11())

        # 初始化布局
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        # 向组中添加卡片
        self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.blurRadiusCard)

        self.updateSoftwareGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # 将设置卡组添加到布局中
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.updateSoftwareGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            '更新成功',
            '配置在重新启动后生效',
            duration=1500,
            parent=self
        )

    def __connectSignalToSlot(self):
        """ 将信号连接到信号槽 """
        cfg.appRestartSig.connect(self.__showRestartTooltip)

        # 个性化
        cfg.themeChanged.connect(setTheme)
        self.themeColorCard.colorChanged.connect(lambda c: setThemeColor(c))
        self.micaCard.checkedChanged.connect(signalBus.micaEnableChanged)

        # 关于
        self.feedbackCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FEEDBACK_URL)))

        # 检查更新
        self.aboutCard.clicked.connect(lambda: self.check_update())

    def check_update(self):
        software_msg = UpdateUtil.software_mag()
        if software_msg is None:
            InfoBar.warning(
                title="检查更新",
                content="检查更新失败，请检查你的网络！",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.window()
            )
        elif VERSION == software_msg["version"]:
            InfoBar.success(
                title="检查更新",
                content="已更新至最新版本！",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.window()
            )
        else:
            view = FlyoutView(
                title="发现新版本",
                content='\n'.join(f"{i + 1}. {item}" for i, item in enumerate(software_msg["msg"])),
                image=':gallery/images/header1.png',
                isClosable=True
            )

            # 修改关闭按钮槽函数
            view.closeButton.clicked.disconnect()
            view.closeButton.clicked.connect(view.close)

            # 添加按钮
            download_button = PrimaryPushButton('下载新版本')
            download_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(RELEASE_URL)))
            view.addWidget(download_button, align=Qt.AlignRight)

            # adjust layout (optional)
            view.widgetLayout.insertSpacing(1, 5)
            view.widgetLayout.insertSpacing(0, 5)
            view.widgetLayout.addSpacing(5)

            # 显示弹窗
            Flyout.make(view, target=self.window(), parent=self, aniType=FlyoutAnimationType.PULL_UP)


class CustomMessageBox(MessageBoxBase):
    """ 文本输入消息框 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.title_label = SubtitleLabel("设置加密", self)

        self.password_lineEdit = PasswordLineEdit(self)
        regex = QRegExp("[a-zA-Z0-9\\s]+")
        validator = QRegExpValidator(regex)
        self.password_lineEdit.setValidator(validator)
        self.password_lineEdit.setPlaceholderText("密码")
        self.password_lineEdit.setClearButtonEnabled(True)

        # 添加组件到布局
        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.password_lineEdit)

        # 修改按钮文本
        self.yesButton.setText("确认")
        self.cancelButton.setText("取消")

        # 修改确认按钮点击槽函数
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self.net_yes_button_clicked)

        self.widget.setMinimumWidth(360)