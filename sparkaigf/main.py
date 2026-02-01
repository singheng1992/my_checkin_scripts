#!/usr/bin/env python3
"""
SparkAI 签到脚本
https://ai.sparkaigf.com/
"""

import logging
import os
import sys
import traceback
from typing import Any

import requests
from utils.notify import XizhiNotifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

# 环境变量
# 格式: username#password||username#password (多账号用 || 分隔，用户名和密码用 # 分隔)
ENV_ACCOUNTS = "SPARKAIGF_ACCOUNTS"

# API 配置
BASE_URL = "https://ai.sparkaigf.com/api"
LOGIN_URL = f"{BASE_URL}/auth/login"
SIGN_URL = f"{BASE_URL}/signin/sign"
SIGN_LOG_URL = f"{BASE_URL}/signin/signinLog"

# 请求头
HEADERS = {
    "Host": "ai.sparkaigf.com",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://ai.sparkaigf.com",
    "Referer": "https://ai.sparkaigf.com/chatai",
    "X-Website-Domain": "ai.sparkaigf.com",
    "Fingerprint": "1058487584",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}


class SparkAIClient:
    """SparkAI 签到客户端"""

    def __init__(self) -> None:
        """初始化客户端"""
        self.accounts: list[dict[str, str]] = []

    def load_config(self) -> None:
        """从环境变量加载配置"""
        raw_accounts = os.environ.get(ENV_ACCOUNTS)

        if not raw_accounts:
            logger.error(
                f'请设置环境变量:\n  {ENV_ACCOUNTS}="username1#password1||username2#password2"'
            )
            sys.exit(1)

        for account_str in raw_accounts.split("||"):
            account_str = account_str.strip()
            if ":" not in account_str:
                logger.error(
                    f"账号格式错误，应为 username:password: {account_str[:20]}..."
                )
                sys.exit(1)
            username, password = account_str.split(":", 1)
            self.accounts.append(
                {"username": username.strip(), "password": password.strip()}
            )

        logger.info(f"加载了 {len(self.accounts)} 个账号")

    def login(self, username: str, password: str) -> str:
        """登录获取 Token

        Args:
            username: 用户名
            password: 密码

        Returns:
            Authorization Token
        """
        payload = {"username": username, "password": password}
        response = requests.post(LOGIN_URL, headers=HEADERS, json=payload)
        data = response.json()

        if data.get("code") != 200:
            raise ValueError(f"登录失败: {data.get('message')}")

        token = data.get("data", "")
        if not token:
            raise ValueError("登录成功但未获取到 Token")

        return token

    def get_sign_log(self, token: str) -> list[dict[str, Any]]:
        """获取签到记录

        Args:
            token: Authorization Token

        Returns:
            签到记录列表
        """
        headers = {**HEADERS, "Authorization": f"Bearer {token}"}
        response = requests.get(SIGN_LOG_URL, headers=headers)
        data = response.json()

        if data.get("code") != 200:
            raise ValueError(f"获取签到记录失败: {data.get('message')}")

        return data.get("data", [])

    def checkin(self, token: str) -> str:
        """执行签到

        Args:
            token: Authorization Token

        Returns:
            签到结果消息
        """
        headers = {**HEADERS, "Authorization": f"Bearer {token}"}
        response = requests.post(SIGN_URL, headers=headers, json={})
        data = response.json()

        if data.get("code") == 200:
            return data.get("data", "签到成功")
        else:
            return data.get("message", "签到失败")

    def count_signed_days(self, sign_log: list[dict[str, Any]]) -> int:
        """统计已签到天数

        Args:
            sign_log: 签到记录列表

        Returns:
            已签到天数
        """
        return sum(1 for item in sign_log if item.get("isSigned"))

    def is_today_signed(self, sign_log: list[dict[str, Any]]) -> bool:
        """检查今日是否已签到

        Args:
            sign_log: 签到记录列表

        Returns:
            今日是否已签到
        """
        if not sign_log:
            return False
        # 签到记录按日期排序，第一条是今天
        return sign_log[0].get("isSigned", False)

    def run(self) -> None:
        """执行所有账号签到"""
        self.load_config()

        success_count = 0
        for idx, account in enumerate(self.accounts, 1):
            username = account["username"]
            password = account["password"]

            try:
                logger.info(f"账号 [{idx}/{len(self.accounts)}] {username}: 登录中...")

                # 登录获取 Token
                token = self.login(username, password)
                logger.info(f"账号 {idx}: 登录成功")

                # 执行签到
                result = self.checkin(token)
                logger.info(f"账号 {idx}: {result}")

                # 再次获取签到记录
                sign_log = self.get_sign_log(token)
                signed_days = self.count_signed_days(sign_log)
                logger.info(f"账号 {idx}: 本月累计签到 {signed_days} 天")
                success_count += 1

            except Exception:
                logger.error(
                    f"账号 {idx} ({username}): 签到失败, 错误信息: {traceback.format_exc()}"
                )
                notifier = XizhiNotifier()
                notifier.send(
                    "SparkAI 签到失败",
                    f"账号 {idx} ({username}): 签到失败, 错误信息: {traceback.format_exc()}",
                )
            finally:
                logger.info("=" * 40)

        logger.info(f"签到完成: 成功 {success_count}/{len(self.accounts)}")


def main():
    """主函数"""
    client = SparkAIClient()
    client.run()


if __name__ == "__main__":
    main()
