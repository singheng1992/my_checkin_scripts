"""息知推送通知模块"""

import logging
import os

import requests

logger = logging.getLogger(__name__)


class XizhiNotifier:
    """息知推送通知类

    使用息知 (xizhi.qqoq.net) 发送消息通知

    Attributes:
        key: 息知推送的 key
        base_url: 息知 API 基础地址
    """

    BASE_URL = "https://xizhi.qqoq.net"

    def __init__(self, key: str | None = None) -> None:
        """初始化通知器

        Args:
            key: 息知推送的 key，若不传则从环境变量 XIZHI_KEY 读取
        """
        self.key = key or os.environ.get("XIZHI_KEY")
        if not self.key:
            raise ValueError("key 不能为空，请传入 key 或设置环境变量 XIZHI_KEY")

    def send(self, title: str, content: str = "") -> bool:
        """发送通知

        Args:
            title: 消息标题
            content: 消息内容，可选

        Returns:
            发送是否成功
        """
        url = f"{self.BASE_URL}/{self.key}.send"
        params = {
            "title": title,
            "content": content,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            logger.info("通知发送成功: %s", title)
            return True
        except requests.RequestException as e:
            logger.error("发送通知失败: %s", e)
            return False


if __name__ == "__main__":
    # 使用示例
    notifier = XizhiNotifier()
    notifier.send("测试标题", "测试内容")
