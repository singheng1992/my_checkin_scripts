#!/usr/bin/env python3
"""
网易云音乐签到脚本
https://music.163.com/
"""

import logging
import os
import sys
import traceback

import requests
from utils.notify import XizhiNotifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

# 环境变量
ENV_COOKIES = "MUSIC163_COOKIES"

# API 配置
MOBILE_URL = "http://music.163.com/api/point/dailyTask?type=0"
DESKTOP_URL = "http://music.163.com/api/point/dailyTask?type=1"


class Music163Client:
    """网易云音乐签到客户端"""

    def __init__(self) -> None:
        """初始化客户端"""
        self.cookies: list[str] = []

    def load_cookies(self) -> None:
        """从环境变量加载 cookies"""
        raw_cookies = os.environ.get(ENV_COOKIES)
        if not raw_cookies:
            logger.error(f'请设置 {ENV_COOKIES} 环境变量, 格式: {ENV_COOKIES}="c1||c2"')
            sys.exit(1)

        for cookie in raw_cookies.split("||"):
            cookie = cookie.strip()
            self.cookies.append(cookie)

        logger.info(f"加载了 {len(self.cookies)} 个账号")

    def _checkin_single(self, url: str, cookie: str, client_type: str) -> str:
        """单端签到

        Args:
            url: 签到 API 地址
            cookie: Cookie 字符串
            client_type: 客户端类型（手机端/桌面端）

        Returns:
            签到结果消息
        """
        try:
            response = requests.get(url, headers={"Cookie": cookie})

            if not response.ok:
                return f"{client_type}签到失败: HTTP {response.status_code}"

            data = response.json()
            if "重复" in str(data):
                return f"{client_type}: 重复签到"
            elif "point" in str(data):
                return f"{client_type}: 获得 {data.get('point', 0)} 云贝"
            else:
                return f"{client_type}: Cookie失效"

        except requests.RequestException as e:
            return f"{client_type}请求失败: {e}"
        except Exception as e:
            return f"{client_type}异常: {e}"

    def checkin(self, cookie: str) -> tuple[str, str]:
        """执行签到

        Args:
            cookie: Cookie 字符串

        Returns:
            (手机端结果, 桌面端结果)
        """
        mobile_result = self._checkin_single(MOBILE_URL, cookie, "手机端")
        desktop_result = self._checkin_single(DESKTOP_URL, cookie, "桌面端")
        return mobile_result, desktop_result

    def run(self) -> None:
        """执行所有账号签到"""
        self.load_cookies()

        success_count = 0
        for idx, cookie in enumerate(self.cookies, 1):
            try:
                logger.info(f"账号 [{idx}/{len(self.cookies)}]: 签到中...")
                mobile_result, desktop_result = self.checkin(cookie)
                logger.info(f"  {mobile_result}")
                logger.info(f"  {desktop_result}")
                success_count += 1

            except Exception:
                logger.error(
                    f"账号 {idx}: 签到失败, 错误信息: {traceback.format_exc()}"
                )
                notifier = XizhiNotifier()
                notifier.send(
                    "music163 签到失败",
                    f"账号 {idx}: 签到失败, 错误信息: {traceback.format_exc()}",
                )
            finally:
                logger.info("=" * 40)

        logger.info(f"签到完成: 成功 {success_count}/{len(self.cookies)}")


def main():
    """主函数"""
    client = Music163Client()
    client.run()


if __name__ == "__main__":
    main()
