import yaml
import requests


class UpdateUtil:

    @staticmethod
    def software_mag(timeout=10):
        """返回软件信息"""
        try:
            # 发送GET请求获取内容
            response = requests.get("https://gitee.com/Ke_ShiFu/file/raw/master/update.yaml", timeout=timeout)
            response.raise_for_status()
            return yaml.safe_load(response.text)["NetForge"]
        except Exception:
            return None
