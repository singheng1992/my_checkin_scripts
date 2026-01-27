#!/usr/bin/env python3
"""
木兰签到脚本
https://mulan.pro
"""

import logging
import os
import sys

import requests


def login(email, password):
    """登录获取 token"""
    url = "https://api3.mulan.pro/api/auth/sign-in"
    headers = {"Content-Type": "application/json"}
    data = {"email": email, "password": password}

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()

    result = response.json()
    access_token = result.get("data", {}).get("access_token")

    if not access_token:
        logging.error(f"登录失败: {result}")
        sys.exit(1)

    return access_token


def get_user_info(token):
    """获取用户信息"""
    url = "https://api3.mulan.pro/api/user/protected/userinfo/fresh"
    headers = {"authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    result = response.json()
    return result.get("data", {})


def main():
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 从环境变量获取账号，格式: email:password||email2:password2
    accounts_str = os.environ.get("MULAN_ACCOUNTS", "")

    if not accounts_str:
        logging.error("请设置 MULAN_ACCOUNTS 环境变量")
        logging.error('格式: MULAN_ACCOUNTS="email1:password1||email2:password2"')
        sys.exit(1)

    # 解析账号列表
    accounts = []
    for account in accounts_str.split("||"):
        account = account.strip()
        if ":" not in account:
            logging.error(f"账号格式不正确: {account}")
            logging.error("正确格式: email:password")
            sys.exit(1)
        email, password = account.split(":", 1)
        accounts.append((email.strip(), password.strip()))

    # 遍历所有账号
    success_count = 0
    for i, (email, password) in enumerate(accounts, 1):
        logging.info(f"{'=' * 40}")
        logging.info(f"账号 [{i}/{len(accounts)}]: {email}")
        logging.info("=" * 40)

        try:
            # 登录
            token = login(email, password)
            # 获取用户信息
            user_info = get_user_info(token)
            nickname = user_info.get("nickname", "未知")
            balance = user_info.get("balance", 0)
            free_balance = user_info.get("free_balance", 0)
            logging.info(f"用户: {nickname}")
            logging.info(f"积分: {balance} (免费: {free_balance})")
            success_count += 1
        except Exception as e:
            logging.error(f"账号 {email} 签到失败: {e}")
            continue

    logging.info(f"签到完成: 成功 {success_count}/{len(accounts)}")


if __name__ == "__main__":
    main()
