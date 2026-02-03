#!/usr/bin/env python3
"""
magic666.top 邮箱验证码发送脚本
"""

import requests

# API 配置
BASE_URL = "https://magic666.top"
VERIFICATION_URLS = [
    f"{BASE_URL}/api/verification?email=singingplayer%40163.com&turnstile=",
    f"{BASE_URL}/api/verification?email=zousmdad%40gmail.com&turnstile=",
    f"{BASE_URL}/api/verification?email=singheng1992%40gmail.com&turnstile=",
]

# 请求头
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
    "cache-control": "no-store",
    "new-api-user": "-1",
    "priority": "u=1, i",
    "referer": f"{BASE_URL}/register",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}

# 发送请求
for VERIFICATION_URL in VERIFICATION_URLS:
    response = requests.get(
        VERIFICATION_URL,
        headers=HEADERS,
    )
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
