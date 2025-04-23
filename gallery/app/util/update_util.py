import yaml
import requests
from ..common.config import VERSION


class UpdateUtil:

    @staticmethod
    def is_update(timeout=10):
        """有更新返回True，无更新返回False，请求失败返回None"""
        try:
            # 发送GET请求获取内容
            response = requests.get("https://gitee.com/Ke_ShiFu/file/raw/master/update.yaml", timeout=timeout)
            response.raise_for_status()
            if VERSION == yaml.safe_load(response.text)["NetForge"]["version"]:
                return False
            else:
                return True
        except Exception:
            return None