#!/usr/bin/env python3
"""
996coder签到脚本
https://996coder.com/
"""

import logging
import os
import sys
import traceback
from typing import Optional

import requests
from utils.notify import XizhiNotifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

# 环境变量
ENV_ACCOUNTS = "NINENINESIX_CODER_ACCOUNTS"
# API 配置
BASE_URL = "https://996coder.com"
LOGIN_URL = f"{BASE_URL}/api/user/login"
CHECKIN_URL = f"{BASE_URL}/api/user/checkin"
# 请求头
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
    "cache-control": "no-store",
    "content-type": "application/json",
    "origin": BASE_URL,
    "referer": f"{BASE_URL}/login",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}


class NineNineSixCoderClient:
    """996coder 签到客户端"""

    def __init__(self) -> None:
        """初始化客户端"""
        self.accounts: list[dict[str, str]] = []

    def load_accounts(self) -> None:
        """从环境变量加载账号信息"""
        raw_accounts = os.environ.get(ENV_ACCOUNTS)
        if not raw_accounts:
            logger.error(
                f'请设置 {ENV_ACCOUNTS} 环境变量, 格式: {ENV_ACCOUNTS}="user1:pass1||user2:pass2"'
            )
            sys.exit(1)

        for account in raw_accounts.split("||"):
            account = account.strip()
            if ":" in account:
                username, password = account.split(":", 1)
                self.accounts.append(
                    {"username": username.strip(), "password": password.strip()}
                )
            else:
                logger.warning(f"跳过无效账号格式: {account}")

        logger.info(f"加载了 {len(self.accounts)} 个账号")

    def login(self, username: str, password: str) -> Optional[tuple[str, str]]:
        """登录获取session

        Args:
            username: 用户名
            password: 密码

        Returns:
            (session cookie字符串, user_id)元组，失败返回None
        """
        url = f"{LOGIN_URL}?turnstile="
        response = requests.post(
            url,
            headers=HEADERS,
            json={"username": username, "password": password},
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                # 从响应body获取用户ID
                user_id = str(data.get("data", {}).get("id", ""))

                # 从响应的cookies中获取session
                session_cookie = response.cookies.get("session")
                if session_cookie:
                    return f"session={session_cookie}", user_id
                # 如果cookie在Set-Cookie头中
                for cookie in response.cookies:
                    if cookie.name == "session":
                        return f"session={cookie.value}", user_id

        logger.error(f"登录失败: {response.text}")

    def checkin(self, session_cookie: str, user_id: str) -> str:
        """执行签到

        Args:
            session_cookie: session cookie 字符串
            user_id: 用户ID

        Returns:
            签到结果消息
        """
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
            "cache-control": "no-store",
            "origin": BASE_URL,
            "priority": "u=1, i",
            "referer": f"{BASE_URL}/console/personal",
            "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
            "cookie": session_cookie,
            "new-api-user": user_id,
        }

        response = requests.post(
            CHECKIN_URL,
            headers=headers,
        )

        data = response.json()
        message = data.get("message", "无消息")
        if response.status_code == 200:
            return message
        else:
            return f"签到失败: {message}"

    def run(self) -> None:
        """执行所有账号签到"""
        self.load_accounts()

        success_count = 0
        for idx, account in enumerate(self.accounts, 1):
            try:
                username = account["username"]
                logger.info(f"账号 [{idx}/{len(self.accounts)}] {username}: 登录中...")

                # 登录获取session和user_id
                login_result = self.login(username, account["password"])
                if not login_result:
                    logger.error(f"账号 {idx} {username}: 登录失败")
                    continue

                session_cookie, user_id = login_result
                logger.info(f"账号 {idx} {username}: 登录成功，开始签到...")

                # 签到操作
                result = self.checkin(session_cookie, user_id)
                logger.info(f"账号 {idx} {username}: {result}")
                success_count += 1

            except Exception:
                logger.error(
                    f"账号 {idx}: 签到失败, 错误信息: {traceback.format_exc()}"
                )
                notifier = XizhiNotifier()
                notifier.send(
                    "996coder 签到失败",
                    f"账号 {idx}: 签到失败, 错误信息: {traceback.format_exc()}",
                )
            finally:
                logger.info("=" * 40)

        logger.info(f"签到完成: 成功 {success_count}/{len(self.accounts)}")


def main():
    """主函数"""
    client = NineNineSixCoderClient()
    client.run()


if __name__ == "__main__":
    main()
