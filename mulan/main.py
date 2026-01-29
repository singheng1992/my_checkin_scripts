#!/usr/bin/env python3
"""
木兰签到脚本
https://mulan.pro
"""

import logging
import os
import sys
import traceback

import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_accounts(accounts_str: str) -> list[tuple[str, str]]:
    """解析账号列表字符串

    Args:
        accounts_str: 账号字符串，格式: "email1:password1||email2:password2"

    Returns:
        账号列表，每个元素为 (email, password) 元组

    Raises:
        SystemExit: 当账号格式不正确时退出程序
    """
    if not accounts_str:
        logger.error("请设置 MULAN_ACCOUNTS 环境变量")
        logger.error('格式: MULAN_ACCOUNTS="email1:password1||email2:password2"')
        sys.exit(1)

    accounts = []
    for account in accounts_str.split("||"):
        account = account.strip()
        if ":" not in account:
            logger.error(f"账号格式不正确: {account}")
            logger.error("正确格式: email:password")
            sys.exit(1)
        email, password = account.split(":", 1)
        accounts.append((email.strip(), password.strip()))

    return accounts


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
        logger.error(f"登录失败: {result}")
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


def get_projects(token):
    """获取项目列表"""
    url = "https://api3.mulan.pro/api/studio_manager/projects/recents"
    headers = {"authorization": f"Bearer {token}"}
    params = {"limit": 999999, "offset": 0, "order_by": "create_at"}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    data = result.get("data", {})
    projects = data.get("items", [])
    return projects


def get_flow_info(token, project_id):
    """获取项目工作流信息"""
    url = f"https://api3.mulan.pro/api/studio_manager/flow/{project_id}/"
    headers = {"authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    result = response.json()
    return result.get("data", {})


def run_workflow(token, task_data):
    """执行工作流任务"""
    url = "https://api3.mulan.pro/api/manage/v1/workflows/run"
    headers = {
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    response = requests.post(url, json=task_data, headers=headers)
    response.raise_for_status()

    result = response.json()
    return result


def main():
    # 从环境变量获取并解析账号列表
    accounts_str = os.environ.get("MULAN_ACCOUNTS", "")
    accounts = parse_accounts(accounts_str)

    # 遍历所有账号
    success_count = 0
    for i, (email, password) in enumerate(accounts, 1):
        logger.info(f"{'=' * 40}")
        logger.info(f"账号 [{i}/{len(accounts)}]: {email}")

        try:
            # 登录获取 access_token
            token = login(email, password)
            logger.info("登录成功")

            # 获取用户信息
            user_info = get_user_info(token)
            nickname = user_info.get("nickname", "未知")
            balance = user_info.get("balance", 0)
            free_balance = user_info.get("free_balance", 0)
            logger.info(f"用户: {nickname}, 积分: {balance} (免费: {free_balance})")

            # # 获取项目列表（取最后一个项目）
            # projects = get_projects(token)
            # if not projects:
            #     logger.info("暂无项目，跳过签到任务")
            #     success_count += 1
            #     continue

            # last_project = projects[-1]
            # project_id = last_project.get("short_url_id")
            # project_name = last_project.get("name", "未命名")
            # logger.info(f"获取到项目: {project_name} (ID: {project_id})")

            # # 获取工作流信息，提取任务参数
            # flow_data = get_flow_info(token, project_id)
            # workflows = flow_data.get("workflows", [])
            # if not workflows:
            #     logger.info("工作流为空，跳过签到任务")
            #     success_count += 1
            #     continue

            # nodes = workflows[0].get("data", {}).get("nodes", [])
            # run_task = None
            # for node in nodes:
            #     if node.get("data", {}).get("run_task"):
            #         run_task = node["data"]["run_task"]
            #         break

            # if not run_task:
            #     logger.info("未找到可执行任务，跳过签到任务")
            #     success_count += 1
            #     continue

            # # 执行任务
            # logger.info("开始执行生图任务...")
            # result = run_workflow(token, run_task)
            # logger.info(f"执行生图任务结果：{result}")

            success_count += 1
        except Exception:
            logger.error(f"账号 {email} 签到失败: {traceback.format_exc()}")
            continue
        logger.info("=" * 40)

    logger.info(f"签到完成: 成功 {success_count}/{len(accounts)}")


if __name__ == "__main__":
    main()
