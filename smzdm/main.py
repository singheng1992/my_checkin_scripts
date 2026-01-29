#!/usr/bin/env python3
"""
什么值得买签到脚本
https://www.smzdm.com/
"""

import hashlib
import logging
import os
import re
import sys
import time
import traceback

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

# 环境变量
ENV_COOKIES = "SMZDM_COOKIES"

# API 配置
ROBOT_TOKEN_URL = "https://user-api.smzdm.com/robot/token"
CHECKIN_URL = "https://user-api.smzdm.com/checkin"
USER_INFO_URL = "https://zhiyou.smzdm.com/user/"
LOTTERY_URL = "https://zhiyou.smzdm.com/user/lottery/jsonp_draw"
LOTTERY_INFO_URL = "https://zhiyou.smzdm.com/user/lottery/jsonp_get_active_info"

# 签到签名密钥
SIGN_KEY = "apr1$AwP!wRRT$gJ/q.X24poeBInlUJC"


# 请求头
USER_API_HEADERS = {
    "Host": "user-api.smzdm.com",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "smzdm_android_V10.4.1 rv:841 (22021211RC;Android12;zh)smzdmapp",
}

ZHIYOU_HEADERS = {
    "Host": "zhiyou.smzdm.com",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/smzdm 10.4.6 rv:130.1 (iPhone 13; iOS 15.6; zh_CN)/iphone_smzdmapp/10.4.6/wkwebview/jsbv_1.0.0",
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Referer": "https://m.smzdm.com/",
    "Accept-Encoding": "gzip, deflate, br",
}


class SmzdmClient:
    """什么值得买签到客户端"""

    def __init__(self) -> None:
        """初始化客户端"""
        self.cookies: list[str] = []

    def load_cookies(self) -> None:
        """从环境变量加载 cookies"""
        raw_cookies = os.environ.get(ENV_COOKIES)
        if not raw_cookies:
            logger.error(f"请设置 {ENV_COOKIES} 环境变量")
            logger.error('格式: ENV_COOKIES="cookie1||cookie2"')
            sys.exit(1)

        for cookie in raw_cookies.split("||"):
            cookie = cookie.strip()
            self.cookies.append(cookie)

        logger.info(f"加载了 {len(self.cookies)} 个账号")

    def _get_robot_token(self, cookie: str) -> str:
        """获取 robot token

        Args:
            cookie: Cookie 字符串

        Returns:
            robot token 字符串
        """
        ts = round(time.time() * 1000)
        sign_str = f"f=android&time={ts}&v=10.4.1&weixin=1&key={SIGN_KEY}"
        sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()

        data = {
            "f": "android",
            "v": "10.4.1",
            "weixin": 1,
            "time": ts,
            "sign": sign,
        }

        headers = {**USER_API_HEADERS, "Cookie": cookie}
        response = requests.post(ROBOT_TOKEN_URL, headers=headers, data=data)
        result = response.json()
        return result["data"]["token"]

    def checkin(self, cookie: str, token: str) -> str:
        """执行签到

        Args:
            cookie: Cookie 字符串
            token: robot token

        Returns:
            签到结果消息
        """
        time_stamp = round(time.time() * 1000)
        sk = "ierkM0OZZbsuBKLoAgQ6OJneLMXBQXmzX+LXkNTuKch8Ui2jGlahuFyWIzBiDq/L"
        sign_str = f"f=android&sk={sk}&time={time_stamp}&token={token}&v=10.4.1&weixin=1&key={SIGN_KEY}"
        sign = hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()

        data = {
            "f": "android",
            "v": "10.4.1",
            "sk": sk,
            "weixin": 1,
            "time": time_stamp,
            "token": token,
            "sign": sign,
        }

        headers = {**USER_API_HEADERS, "Cookie": cookie}
        resp = requests.post(CHECKIN_URL, headers=headers, data=data)
        return resp.json()["error_msg"]

    def _get_user_info(self, cookie: str) -> dict:
        """获取用户信息

        Args:
            cookie: Cookie 字符串

        Returns:
            包含用户信息的字典
        """
        headers = {**ZHIYOU_HEADERS, "Cookie": cookie}

        # 获取用户信息页面
        info_html = requests.get(USER_INFO_URL, headers=headers).text

        # 解析用户信息
        name_match = re.findall(
            r'<a href="https://zhiyou.smzdm.com/user"> (.*?) </a>', info_html, re.S
        )
        name = name_match[0] if name_match else "未知"

        level_match = re.findall(
            r'<img src="https://res.smzdm.com/h5/h5_user/dist/assets/level/(.*?).png\?v=1">',
            info_html,
            re.S,
        )
        level = level_match[0] if level_match else "未知"

        gold_match = re.findall(
            r'<div class="assets-part assets-gold">\s+(.*?)</span>', info_html, re.S
        )
        gold = (
            gold_match[0]
            .replace('<span class="assets-part-element assets-num">', "")
            .replace("'", "")
            if gold_match
            else "未知"
        )

        silver_match = re.findall(
            r'<div class="assets-part assets-prestige">\s+(.*?)</span>', info_html, re.S
        )
        silver = (
            silver_match[0]
            .replace('<span class="assets-part-element assets-num">', "")
            .replace("'", "")
            if silver_match
            else "未知"
        )

        return {
            "level": level,
            "name": name,
            "gold": gold,
            "silver": silver,
        }

    def run(self) -> None:
        """执行所有账号签到"""
        self.load_cookies()

        success_count = 0
        for idx, cookie in enumerate(self.cookies, 1):
            try:
                logger.info(f"账号 [{idx}/{len(self.cookies)}]: 签到中...")

                # 获取用户信息
                user_info = self._get_user_info(cookie)
                logger.info(f"  昵称: {user_info['name']}")
                logger.info(f"  等级: {user_info['level']}")
                logger.info(f"  金币: {user_info['gold']}")
                logger.info(f"  碎银: {user_info['silver']}")

                # 获取 robot token
                token = self._get_robot_token(cookie)
                logger.info("  获取 robot token 成功")

                # 执行签到
                checkin_result = self.checkin(cookie, token)
                logger.info(f"  签到: {checkin_result}")
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
    client = SmzdmClient()
    client.run()


if __name__ == "__main__":
    main()
