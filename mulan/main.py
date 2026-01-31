#!/usr/bin/env python3
"""
木兰签到脚本
https://mulan.pro
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
ENV_ACCOUNTS = "MULAN_ACCOUNTS"

# API 配置
LOGIN_URL = "https://api3.mulan.pro/api/auth/sign-in"
USER_INFO_URL = "https://api3.mulan.pro/api/user/protected/userinfo/fresh"
PROJECTS_URL = "https://api3.mulan.pro/api/studio_manager/projects/recents"
FLOW_INFO_URL = "https://api3.mulan.pro/api/studio_manager/flow/{}/"
WORKFLOW_RUN_URL = "https://api3.mulan.pro/api/manage/v1/workflows/run"

# 请求头
HEADERS = {"Content-Type": "application/json"}


class Account:
    """账号信息"""

    def __init__(self, email: str, password: str) -> None:
        """初始化账号信息

        Args:
            email: 邮箱
            password: 密码
        """
        self.email = email
        self.password = password
        self.token: str = ""

    def __repr__(self) -> str:
        return f"Account(email={self.email})"


class MulanClient:
    """木兰签到客户端"""

    def __init__(self) -> None:
        """初始化客户端"""
        self.accounts: list[Account] = []

    def load_accounts(self) -> None:
        """从环境变量加载账号列表"""
        accounts_str = os.environ.get(ENV_ACCOUNTS, "")
        if not accounts_str:
            logger.error(
                f'请设置 {ENV_ACCOUNTS} 环境变量, 格式: {ENV_ACCOUNTS}="email1:password1||email2:password2"'
            )
            sys.exit(1)

        for account in accounts_str.split("||"):
            account = account.strip()
            if ":" not in account:
                logger.error(f"账号格式不正确: {account}, 正确格式: email:password")
                continue
            email, password = account.split(":", 1)
            self.accounts.append(Account(email.strip(), password.strip()))

        logger.info(f"加载了 {len(self.accounts)} 个账号")

    def login(self, account: Account) -> None:
        """登录获取 token

        Args:
            account: 账号对象

        Raises:
            RuntimeError: 登录失败时抛出异常
        """
        response = requests.post(
            LOGIN_URL,
            json={"email": account.email, "password": account.password},
            headers=HEADERS,
        )
        response.raise_for_status()

        result = response.json()
        access_token = result.get("data", {}).get("access_token")

        if not access_token:
            raise RuntimeError(f"登录失败: {result}")

        account.token = access_token

    def get_user_info(self, token: str) -> dict[str, Any]:
        """获取用户信息

        Args:
            token: 访问令牌

        Returns:
            用户信息字典
        """
        response = requests.get(
            USER_INFO_URL,
            headers={"authorization": f"Bearer {token}"},
        )
        response.raise_for_status()

        result = response.json()
        return result.get("data", {})

    def get_projects(self, token: str) -> list[dict[str, Any]]:
        """获取项目列表

        Args:
            token: 访问令牌

        Returns:
            项目列表
        """
        response = requests.get(
            PROJECTS_URL,
            headers={"authorization": f"Bearer {token}"},
            params={"limit": 999999, "offset": 0, "order_by": "create_at"},
        )
        response.raise_for_status()

        result = response.json()
        data = result.get("data", {})
        return data.get("items", [])

    def get_flow_info(self, token: str, project_id: str) -> dict[str, Any]:
        """获取项目工作流信息

        Args:
            token: 访问令牌
            project_id: 项目 ID

        Returns:
            工作流信息字典
        """
        response = requests.get(
            FLOW_INFO_URL.format(project_id),
            headers={"authorization": f"Bearer {token}"},
        )
        response.raise_for_status()

        result = response.json()
        return result.get("data", {})

    def run_workflow(self, token: str, task_data: dict[str, Any]) -> dict[str, Any]:
        """执行工作流任务

        Args:
            token: 访问令牌
            task_data: 任务数据

        Returns:
            执行结果字典
        """
        response = requests.post(
            WORKFLOW_RUN_URL,
            json=task_data,
            headers={
                "authorization": f"Bearer {token}",
                "content-type": "application/json",
            },
        )
        response.raise_for_status()

        return response.json()

    def run(self) -> None:
        """执行所有账号签到"""
        self.load_accounts()

        success_count = 0
        for idx, account in enumerate(self.accounts, 1):
            logger.info(
                f"账号 [{idx}/{len(self.accounts)}]: {account.email}, 签到中..."
            )

            try:
                # 登录
                self.login(account)
                logger.info(f"账号 {idx}: 登录成功")

                # 获取用户信息
                user_info = self.get_user_info(account.token)
                nickname = user_info.get("nickname", "未知")
                balance = user_info.get("balance", 0)
                logger.info(f"账号 {idx}: 用户: {nickname}, 现有积分: {balance}")

                # 获取项目列表（取最后一个项目）
                projects = self.get_projects(account.token)
                if not projects:
                    logger.info("暂无项目，跳过签到任务")
                    success_count += 1
                    continue

                last_project = projects[-1]
                project_id = last_project.get("short_url_id")
                project_name = last_project.get("name", "未命名")
                logger.info(f"获取到项目: {project_name} (ID: {project_id})")

                # 获取工作流信息，提取任务参数
                flow_data = self.get_flow_info(account.token, project_id)
                workflows = flow_data.get("workflows", [])
                if not workflows:
                    logger.info("工作流为空，跳过签到任务")
                    success_count += 1
                    continue

                nodes = workflows[0].get("data", {}).get("nodes", [])
                run_task = None
                for node in nodes:
                    if node.get("data", {}).get("run_task"):
                        run_task = node["data"]["run_task"]
                        break

                if not run_task:
                    logger.info("未找到可执行任务，跳过签到任务")
                    success_count += 1
                    continue

                # 执行任务
                logger.info("开始执行生图任务...")
                result = self.run_workflow(account.token, run_task)
                logger.info(f"执行生图任务结果：{result}")

                success_count += 1
            except Exception:
                logger.error(
                    f"账号 {idx}: 签到失败, 错误信息: {traceback.format_exc()}"
                )
                notifier = XizhiNotifier()
                notifier.send(
                    "mulan 签到失败",
                    f"账号 {idx}: 签到失败, 错误信息: {traceback.format_exc()}",
                )
            finally:
                logger.info("=" * 40)

        logger.info(f"签到完成: 成功 {success_count}/{len(self.accounts)}")


def main() -> None:
    """主函数"""
    client = MulanClient()
    client.run()


if __name__ == "__main__":
    main()
