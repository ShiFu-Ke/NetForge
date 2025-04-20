# coding:utf-8
import sys
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator,
                            OptionsValidator, RangeConfigItem, RangeValidator,
                            Theme)



def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """ Config of application """

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)

    # Material
    blurRadius  = RangeConfigItem("Material", "AcrylicBlurRadius", 15, RangeValidator(0, 40))

    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())


YEAR = 2023
AUTHOR = "Morbid"
VERSION = "0.1.2(测试版)"
HELP_URL = "https://space.bilibili.com/660801861"
REPO_URL = "https://github.com/ShiFu-Ke/NetForge"
EXAMPLE_URL = "https://www.bilibili.com/"
FEEDBACK_URL = "https://github.com/ShiFu-Ke/NetForge/issues"
RELEASE_URL = "https://github.com/ShiFu-Ke/NetForge/releases/latest"


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load('app/config/config.json', cfg)