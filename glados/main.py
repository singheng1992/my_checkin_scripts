#!/usr/bin/env python3
"""
glados签到脚本
https://glados.cloud/
"""

import json
import logging
import os
import sys
import traceback
from typing import Any, Dict, Optional

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

# 环境变量
ENV_COOKIES = "GLADOS_COOKIES"
# API 配置
CHECKIN_URL = "https://glados.cloud/api/user/checkin"
STATUS_URL = "https://glados.cloud/api/user/status"
POINTS_URL = "https://glados.cloud/api/user/points"
# POST 请求数据
CHECKIN_DATA = {"token": "glados.cloud"}
# 请求头
HEADERS = {
    "referer": "https://glados.cloud/console/checkin",
    "origin": "https://glados.cloud",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "content-type": "application/json;charset=UTF-8",
}


class GladosClient:
    """GLADOS 签到客户端"""

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

        logger.info(f"加载了 {len(self.cookies)} 个 Cookie")

    def get_user_status(self, cookie: str) -> Optional[Dict[str, Any]]:
        """获取用户状态信息

        Args:
            cookie: Cookie 字符串

        Returns:
            用户信息字典，包含 email 和 leftDays
        """
        response = requests.get(
            STATUS_URL,
            headers={**HEADERS, "cookie": cookie},
        )
        data = response.json()
        status = data.get("data", {})
        return status

    def get_user_points(self, cookie: str) -> int:
        """获取用户当前积分

        Args:
            cookie: Cookie 字符串

        Returns:
            当前积分，获取失败返回 0
        """
        response = requests.get(
            POINTS_URL,
            headers={**HEADERS, "cookie": cookie},
        )

        data = response.json()
        points = int(float(data.get("points", 0)))
        return points

    def checkin(self, cookie: str) -> str:
        """执行签到

        Args:
            cookie: Cookie 字符串

        Returns:
            签到结果消息
        """
        response = requests.post(
            CHECKIN_URL,
            headers={**HEADERS, "cookie": cookie},
            data=json.dumps(CHECKIN_DATA),
        )

        data = response.json()
        message = data.get("message", "无消息")
        points = data.get("points", 0)

        if "Checkin! Got" in message:
            return f"签到成功，获得 {points} 积分"
        elif "Checkin Repeats!" in message:
            return "重复签到，明天再来"
        else:
            return f"签到失败: {message}"

    def run(self) -> None:
        """执行所有账号签到"""
        self.load_cookies()

        success_count = 0
        for idx, cookie in enumerate(self.cookies, 1):
            try:
                logger.info(f"账号 [{idx}/{len(self.cookies)}]: 签到中...")
                # 签到操作
                result = self.checkin(cookie)
                logger.info(f"账号 {idx}: {result}")

                # 获取用户信息
                status = self.get_user_status(cookie) or {}
                # 获取当前积分
                points = self.get_user_points(cookie) or -1
                email = status["email"]
                leftDays = int(float(status["leftDays"]))
                logger.info(
                    f"账号 {idx}: 邮箱: {email}, 剩余天数: {leftDays}, 当前积分: {points}"
                )
                success_count += 1

            except Exception:
                logger.error(
                    f"账号 {idx}: 签到失败, 错误信息: {traceback.format_exc()}"
                )
            finally:
                logger.info("=" * 40)

        logger.info(f"签到完成: 成功 {success_count}/{len(self.cookies)}")


def main():
    """主函数"""
    client = GladosClient()
    client.run()


if __name__ == "__main__":
    main()
