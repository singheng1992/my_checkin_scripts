#!/usr/bin/env python3
"""
glados签到脚本
https://glados.cloud/
"""

import json
import logging
import os

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 环境变量
ENV_COOKIES = "GLADOS_COOKIES"

# API 配置
CHECKIN_URL = "https://glados.cloud/api/user/checkin"
CHECKIN_DATA = {"token": "glados.cloud"}
HEADERS = {
    "referer": "https://glados.cloud/console/checkin",
    "origin": "https://glados.cloud",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
    "content-type": "application/json;charset=UTF-8",
}


def load_cookies() -> list[str]:
    """从环境变量加载 cookies"""
    raw_cookies = os.environ.get(ENV_COOKIES)
    if not raw_cookies:
        raise ValueError(f"环境变量 '{ENV_COOKIES}' 未设置")

    cookies_list = [
        cookie.strip() for cookie in raw_cookies.split("&") if cookie.strip()
    ]
    if not cookies_list:
        raise ValueError(f"环境变量 '{ENV_COOKIES}' 未包含有效的 Cookie")

    logger.info(f"加载了 {len(cookies_list)} 个 Cookie")
    return cookies_list


def checkin(cookie: str) -> str:
    """执行签到"""
    try:
        response = requests.post(
            CHECKIN_URL,
            headers={**HEADERS, "cookie": cookie},
            data=json.dumps(CHECKIN_DATA),
        )

        if not response.ok:
            return f"签到失败: HTTP {response.status_code}"

        data = response.json()
        message = data.get("message", "无消息")
        points = data.get("points", 0)

        if "Checkin! Got" in message:
            return f"签到成功，获得 {points} 积分"
        elif "Checkin Repeats!" in message:
            return "重复签到，明天再来"
        else:
            return f"签到失败: {message}"

    except requests.RequestException as e:
        return f"网络请求失败: {e}"
    except json.JSONDecodeError:
        return f"响应解析失败: {response.text}"
    except Exception as e:
        return f"签到异常: {e}"


def main():
    try:
        cookies = load_cookies()
        for idx, cookie in enumerate(cookies, 1):
            logger.info(f"账号 {idx} 签到中...")
            result = checkin(cookie)
            logger.info(f"账号 {idx}: {result}")
    except Exception as e:
        logger.error(f"程序执行错误: {e}")
        exit(1)


if __name__ == "__main__":
    main()
