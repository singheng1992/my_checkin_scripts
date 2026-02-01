#!/usr/bin/env python3
"""
MindVideo 签到脚本
https://www.mindvideo.ai/
"""

import hashlib
import json
import logging
import os
import random
import string
import sys
import time
import traceback
from base64 import b64encode

import requests

from utils.notify import XizhiNotifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

# 环境变量
# 格式: email:password||email:password (多账号用 || 分隔，邮箱和密码用 : 分隔)
ENV_ACCOUNTS = "MINDVIDEO_ACCOUNTS"

# API 配置
BASE_URL = "https://api.mindvideo.ai/api"
LOGIN_URL = f"{BASE_URL}/login"
CHECKIN_URL = f"{BASE_URL}/checkin"

# 请求头
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/json",
    "Origin": "https://www.mindvideo.ai",
    "Referer": "https://www.mindvideo.ai/",
    "i-lang": "zh-CN",
    "i-version": "1.0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}


def generate_nonce(length: int = 16) -> str:
    """生成随机 nonce 字符串"""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def generate_sign(nonce: str, timestamp: int) -> str:
    """生成签名

    Args:
        nonce: 随机字符串
        timestamp: 时间戳（毫秒）

    Returns:
        签名字符串
    """
    # 根据分析，签名是 md5(nonce + timestamp)
    sign_str = f"{nonce}{timestamp}"
    return hashlib.md5(sign_str.encode()).hexdigest()


def generate_i_sign() -> str:
    """生成 i-sign 请求头

    Returns:
        base64 编码的 JSON 字符串
    """
    nonce = generate_nonce()
    timestamp = int(time.time() * 1000)
    sign = generate_sign(nonce, timestamp)

    sign_data = {"nonce": nonce, "timestamp": timestamp, "sign": sign}

    return b64encode(json.dumps(sign_data).encode()).decode()


class MindVideoClient:
    """MindVideo 签到客户端"""

    def __init__(self) -> None:
        """初始化客户端"""
        self.accounts: list[dict[str, str]] = []

    def load_config(self) -> None:
        """从环境变量加载配置"""
        raw_accounts = os.environ.get(ENV_ACCOUNTS)

        if not raw_accounts:
            logger.error(
                f'请设置环境变量:\n  {ENV_ACCOUNTS}="email1:password1||email2:password2"'
            )
            sys.exit(1)

        for account_str in raw_accounts.split("||"):
            account_str = account_str.strip()
            if ":" not in account_str:
                logger.error(
                    f"账号格式错误，应为 email:password: {account_str[:20]}..."
                )
                sys.exit(1)
            email, password = account_str.split(":", 1)
            self.accounts.append({"email": email.strip(), "password": password.strip()})

        logger.info(f"加载了 {len(self.accounts)} 个账号")

    def login(self, email: str, password: str) -> str:
        """登录获取 Token

        Args:
            email: 邮箱
            password: 密码（MD5 加密后的）

        Returns:
            Authorization Token
        """
        headers = {**HEADERS, "i-sign": generate_i_sign()}
        payload = {"email": email, "password": password}

        response = requests.post(LOGIN_URL, headers=headers, json=payload, timeout=30)
        data = response.json()
        if data.get("code") != 0:
            raise ValueError(f"登录失败: {data.get('message', data)}")

        token = data.get("data", {}).get("access_token", "")
        if not token:
            raise ValueError("登录成功但未获取到 Token")

        return token

    def checkin(self, token: str) -> str:
        """执行签到

        Args:
            token: Authorization Token

        Returns:
            签到结果消息
        """
        headers = {
            **HEADERS,
            "Authorization": f"Bearer {token}",
            "i-sign": generate_i_sign(),
        }

        response = requests.post(CHECKIN_URL, headers=headers, timeout=30)
        data = response.json()
        if data.get("code") == 0:
            return data.get("message", "签到成功")
        else:
            return f"签到失败: {data.get('message', data)}"

    def run(self) -> None:
        """执行所有账号签到"""
        self.load_config()

        success_count = 0
        for idx, account in enumerate(self.accounts, 1):
            email = account["email"]
            password = account["password"]
            password = hashlib.md5(password.encode()).hexdigest()

            try:
                logger.info(f"账号 [{idx}/{len(self.accounts)}] {email}: 登录中...")

                # 登录获取 Token
                token = self.login(email, password)
                logger.info(f"账号 {idx}: 登录成功")

                # 执行签到
                result = self.checkin(token)
                logger.info(f"账号 {idx}: {result}")
                success_count += 1

            except Exception:
                logger.error(
                    f"账号 {idx} ({email}): 签到失败, 错误信息: {traceback.format_exc()}"
                )
                try:
                    notifier = XizhiNotifier()
                    notifier.send(
                        "MindVideo 签到失败",
                        f"账号 {idx} ({email}): 签到失败, 错误信息: {traceback.format_exc()}",
                    )
                except Exception:
                    logger.warning("发送通知失败")
            finally:
                logger.info("=" * 40)

        logger.info(f"签到完成: 成功 {success_count}/{len(self.accounts)}")


def main():
    """主函数"""
    client = MindVideoClient()
    client.run()


if __name__ == "__main__":
    main()
