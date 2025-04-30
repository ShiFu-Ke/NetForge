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


YEAR = 2025
AUTHOR = "Morbid"
VERSION = "v1.0.0"
HELP_URL = "https://www.baidu.com/"
REPO_URL = "https://github.com/ShiFu-Ke/NetForge"
EXAMPLE_URL = "https://www.baidu.com/"
FEEDBACK_URL = "https://github.com/ShiFu-Ke/NetForge/issues"
RELEASE_URL = "https://github.com/ShiFu-Ke/NetForge/releases/latest"


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load('app/config/config.json', cfg)