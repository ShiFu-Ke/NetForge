import base64
import re
from itertools import cycle
import platform
import hashlib
import subprocess


class Encryption:

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """
        加密字符串
        :param plaintext: 待加密文本
        :return: Base64编码的加密结果
        :raises ValueError: 当密钥为空时抛出
        """
        key = cls.get_key()
        if not key:
            raise ValueError("加密密钥不能为空")

        # 密钥强化处理（SHA256哈希）
        key_bytes = cls._hash_key(key)

        # 执行异或加密
        encrypted = bytearray()
        for p_byte, k_byte in zip(plaintext.encode('utf-8'), cycle(key_bytes)):
            encrypted.append(p_byte ^ k_byte)

        return base64.b64encode(encrypted).decode()

    @classmethod
    def decrypt(cls, ciphertext: str) -> str:
        """
        解密字符串
        :param ciphertext: Base64编码的密文
        :return: 解密后的原始文本
        :raises ValueError: 当密钥错误或数据损坏时抛出
        """
        key = cls.get_key()
        if not key:
            raise ValueError("解密密钥不能为空")

        try:
            # Base64解码
            encrypted_bytes = base64.b64decode(ciphertext)

            # 密钥强化处理
            key_bytes = cls._hash_key(key)

            # 执行异或解密
            decrypted = bytearray()
            for e_byte, k_byte in zip(encrypted_bytes, cycle(key_bytes)):
                decrypted.append(e_byte ^ k_byte)

            return decrypted.decode('utf-8')
        except Exception as e:
            raise ValueError("解密失败，请检查密钥或数据完整性") from e

    @staticmethod
    def _hash_key(raw_key: str) -> bytes:
        """
        密钥哈希处理（SHA256）
        :param raw_key: 原始密钥字符串
        :return: 32字节哈希密钥
        """
        return hashlib.sha256(raw_key.encode('utf-8')).digest()

    @staticmethod
    def get_key():
        system = platform.system()
        if system == 'Windows':
            try:
                # 使用WMIC命令获取UUID
                output = subprocess.check_output(
                    ['wmic', 'csproduct', 'get', 'uuid'],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                # 处理输出结果
                lines = output.decode().strip().split('\r\r\n')
                if len(lines) >= 2:
                    return lines[1].strip()
            except Exception as e:
                return "uuid"
        elif system == 'Linux':
            try:
                # 读取DMI信息文件
                with open('/sys/class/dmi/id/product_uuid', 'r') as f:
                    return f.read().strip()
            except Exception as e:
                return "uuid"
        elif system == 'Darwin':  # macOS
            try:
                # 使用ioreg命令获取硬件信息
                output = subprocess.check_output(
                    ['ioreg', '-rd1', '-c', 'IOPlatformExpertDevice']
                )
                output_str = output.decode()
                # 正则匹配UUID
                match = re.search(r'"IOPlatformUUID"\s*=\s*"([^"]+)"', output_str)
                if match:
                    return match.group(1)
                else:
                    return "uuid"
            except Exception as e:
                return "uuid"
        else:
            return "uuid"  # 不支持的系统
