#!/usr/bin/env python3
"""
买单吧（交通银行信用卡）签到脚本
https://creditcardapp.bankcomm.com/
"""

import json
import logging
import os
import sys
import traceback
from typing import Any, Dict, Optional

import requests
import urllib3
from utils.notify import XizhiNotifier

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

# 环境变量
# 格式: cookie#token||cookie#token (多账号用 || 分隔，cookie 和 token 用 # 分隔)
ENV_ACCOUNTS = "MAIDANBA_ACCOUNTS"

# API 配置
BASE_URL = "https://creditcardapp.bankcomm.com/mdlweb"
SIGN_DATA_URL = f"{BASE_URL}/sign/data"
SIGN_URL = f"{BASE_URL}/sign/sign"

# 请求头
HEADERS = {
    "Host": "creditcardapp.bankcomm.com",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "Origin": "https://creditcardapp.bankcomm.com",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7_1 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Mobile/15E148 BoComMDB",
    "Referer": "https://creditcardapp.bankcomm.com/mdlweb/ddySgn/index?channel=00",
}


class MaidanbaClient:
    """买单吧签到客户端"""

    def __init__(self) -> None:
        """初始化客户端"""
        self.accounts: list[Dict[str, str]] = []
        self.task_id: str = ""

    def load_config(self) -> None:
        """从环境变量加载配置"""
        raw_accounts = os.environ.get(ENV_ACCOUNTS)

        if not raw_accounts:
            logger.error(
                f"请设置环境变量:\n"
                f'  {ENV_ACCOUNTS}="cookie1#token1||cookie2#token2"'
            )
            sys.exit(1)

        for account_str in raw_accounts.split("||"):
            account_str = account_str.strip()
            if "#" not in account_str:
                logger.error(f"账号格式错误，应为 cookie#token: {account_str[:20]}...")
                sys.exit(1)
            cookie, token = account_str.split("#", 1)
            self.accounts.append({"cookie": cookie.strip(), "token": token.strip()})

        logger.info(f"加载了 {len(self.accounts)} 个账号")

    def get_sign_data(self, cookie: str, token: str) -> Optional[Dict[str, Any]]:
        """获取签到信息

        Args:
            cookie: Cookie 字符串
            token: Token 字符串

        Returns:
            签到信息字典
        """
        url = f"{SIGN_DATA_URL}?token={token}"
        payload = {"taskShowCd": "00", "taskId": self.task_id}

        response = requests.post(
            url,
            headers={**HEADERS, "Cookie": cookie},
            data=json.dumps(payload),
            verify=False,
        )
        data = response.json()

        if data.get("returnCode") != "000000":
            raise ValueError(f"获取签到信息失败: {data.get('returnMsg')}")

        # 更新 taskId（如果返回了新的）
        result = data.get("data", {})
        if result.get("taskId"):
            self.task_id = result["taskId"]

        return result

    def checkin(self, cookie: str, token: str) -> str:
        """执行签到

        Args:
            cookie: Cookie 字符串
            token: Token 字符串

        Returns:
            签到结果消息
        """
        url = f"{SIGN_URL}?token={token}"
        payload = {"taskShowCd": "00", "taskId": self.task_id}

        response = requests.post(
            url,
            headers={**HEADERS, "Cookie": cookie},
            data=json.dumps(payload),
            verify=False,
        )
        data = response.json()

        return_code = data.get("returnCode")
        return_msg = data.get("returnMsg", "无消息")

        if return_code == "000000":
            result = data.get("data", {})
            points = result.get("itgBal", 0)
            return f"签到成功，获得 {points} 积分"
        else:
            raise ValueError(f"签到失败: {return_msg}")

    def run(self) -> None:
        """执行所有账号签到"""
        self.load_config()

        success_count = 0
        for idx, account in enumerate(self.accounts, 1):
            cookie = account["cookie"]
            token = account["token"]

            try:
                logger.info(f"账号 [{idx}/{len(self.accounts)}]: 签到中...")

                # 获取签到信息（同时更新 taskId）
                sign_data = self.get_sign_data(cookie, token) or {}
                total_days = sign_data.get("totalDays", 0)
                sign_sts = sign_data.get("signSts", "0")

                if sign_sts == "1":
                    logger.info(f"账号 {idx}: 今日已签到，累计签到 {total_days} 天")
                    success_count += 1
                    continue

                # 执行签到
                result = self.checkin(cookie, token)
                logger.info(f"账号 {idx}: {result}")

                # 再次获取签到信息
                sign_data = self.get_sign_data(cookie, token) or {}
                total_days = sign_data.get("totalDays", 0)
                logger.info(f"账号 {idx}: 累计签到 {total_days} 天")
                success_count += 1

            except Exception:
                logger.error(
                    f"账号 {idx}: 签到失败, 错误信息: {traceback.format_exc()}"
                )
                notifier = XizhiNotifier()
                notifier.send(
                    "买单吧签到失败",
                    f"账号 {idx}: 签到失败, 错误信息: {traceback.format_exc()}",
                )
            finally:
                logger.info("=" * 40)

        logger.info(f"签到完成: 成功 {success_count}/{len(self.accounts)}")


def main():
    """主函数"""
    client = MaidanbaClient()
    client.run()


if __name__ == "__main__":
    main()
