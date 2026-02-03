#!/usr/bin/env python3
"""
magic666.top 用户注册脚本
"""

import requests

# API 配置
BASE_URL = "https://magic666.top"
REGISTER_URL = f"{BASE_URL}/api/user/register?turnstile="

# 请求头
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
    "cache-control": "no-store",
    "content-type": "application/json",
    "new-api-user": "-1",
    "origin": BASE_URL,
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

# 注册数据
payload = [
    {
        "username": "singingplayer",
        "password": "SingHeng@1992",
        "password2": "SingHeng@1992",
        "email": "singingplayer@163.com",
        "verification_code": "",
        "wechat_verification_code": "",
        "aff_code": None,
    },
    {
        "username": "zousmdad",
        "password": "SingHeng@1992",
        "password2": "SingHeng@1992",
        "email": "zousmdad@gmail.com",
        "verification_code": "4c412f",
        "wechat_verification_code": "",
        "aff_code": None,
    },
    {
        "username": "singheng1992",
        "password": "SingHeng@1992",
        "password2": "SingHeng@1992",
        "email": "singheng1992@gmail.com",
        "verification_code": "ae385f",
        "wechat_verification_code": "",
        "aff_code": None,
    },
]

# 发送请求
for each in payload:
    response = requests.post(
        REGISTER_URL,
        headers=HEADERS,
        json=each,
    )

    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
