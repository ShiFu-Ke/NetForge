# coding: utf-8


import yaml
import os
from typing import Any, List

from yaml import Dumper


class YamlUtil:
    def __init__(self, file_path: str, default_data: dict = None):
        """
        初始化时自动创建文件，支持嵌套键操作
        :param file_path: 文件路径（自动创建父目录）
        :param default_data: 文件不存在时的初始化数据（默认空字典）
        """
        self.file_path = file_path
        self.data = None

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.data = yaml.safe_load(file) or {}
        except FileNotFoundError:
            self.data = default_data if default_data else {}
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self._save()
        except Exception as e:
            raise RuntimeError(f"YAML文件加载失败: {str(e)}")

    def get(self, keys: List[str], default: Any = None) -> Any:
        current = self.data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def get_keys(self) -> List[str]:
        """获取所有一级键列表"""
        if isinstance(self.data, dict):
            return list(self.data.keys())
        return []

    def update(self, keys: list, value: Any) -> None:
        current = self.data
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value
        self._save()

    def delete(self, key_path: str) -> bool:
        """删除指定键路径，返回是否成功"""
        keys = key_path.split('.')
        current = self.data
        for i, key in enumerate(keys[:-1]):
            if key not in current:
                return False
            current = current[key]
        if keys[-1] in current:
            del current[keys[-1]]
            self._save()
            return True
        return False

    def _save(self) -> None:
        """保存方法（强制4空格缩进）"""
        with open(self.file_path, 'w', encoding='utf-8') as file:
            yaml.dump(
                self.data,
                file,
                Dumper=IndentDumper,  # 应用自定义缩进规则
                indent=4,  # 主层级缩进4空格
                default_flow_style=False,  # 禁用紧凑格式
                allow_unicode=True,  # 支持中文
                sort_keys=False  # 保持键顺序
            )


class IndentDumper(Dumper):
    """自定义缩进处理器（解决列表项缩进问题）"""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, indentless=False)
