import logging
import sys
import os
from datetime import datetime


class AppLogger:
    def __init__(self,
                 log_dir: str = "",  # 新增日志目录参数
                 log_file_prefix: str = "app",
                 file_level: int = logging.DEBUG,
                 console_level: int = logging.INFO):
        """
        初始化日志记录器
        :param log_dir: 日志文件保存目录（默认当前目录）
        :param log_file_prefix: 日志文件名前缀
        :param file_level: 文件日志级别
        :param console_level: 控制台日志级别
        """
        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(logging.DEBUG)

        # 创建日志目录（如果不存在）
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # 防止重复添加处理器
        if not self.logger.handlers:
            self._configure_handlers(
                log_dir=log_dir,
                prefix=log_file_prefix,
                file_level=file_level,
                console_level=console_level
            )
            self._setup_exception_hook()

    def _configure_handlers(self, log_dir, prefix, file_level, console_level):
        """配置日志处理器"""
        # 生成完整日志路径
        log_filename = f"{prefix}_{datetime.now().strftime('%Y%m')}.log"
        log_filepath = os.path.join(log_dir, log_filename)

        # 文件处理器
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(file_level)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)

        # 统一日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def _setup_exception_hook(self):
        """设置全局异常捕获"""

        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            self.logger.error("未捕获的异常",
                              exc_info=(exc_type, exc_value, exc_traceback))

        sys.excepthook = handle_exception

    def __getattr__(self, name: str):
        """代理日志记录方法"""
        return getattr(self.logger, name)


# 使用示例
if __name__ == "__main__":
    # 初始化日志记录器（保存到logs目录）
    logger = AppLogger(
        log_dir="logs",  # 指定日志目录
        log_file_prefix="myapp",  # 自定义日志文件名前缀
        console_level=logging.WARNING
    )

    try:
        logger.info("程序启动")
        logger.debug("调试信息")
        logger.warning("警告信息")
        1 / 0
    except Exception as e:
        logger.exception("捕获到异常")