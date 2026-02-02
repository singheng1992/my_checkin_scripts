#!/usr/bin/env python3
"""
B站签到脚本
https://www.bilibili.com
"""

import logging
import os
import sys
import traceback
from typing import Any, Union

import requests
from utils.notify import XizhiNotifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

# 环境变量
ENV_COOKIES = "BILIBILI_COOKIES"

# API 配置
USER_INFO_URL = "https://api.bilibili.com/x/web-interface/nav"
DYNAMIC_VIDEOS_URL = (
    "https://api.bilibili.com/x/web-interface/dynamic/region?ps=5&rid=1"
)
RANKING_VIDEOS_URL = (
    "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
)
COIN_STATUS_URL = "https://api.bilibili.com/x/web-interface/archive/coins?bvid={}"
COIN_ADD_URL = "https://api.bilibili.com/x/web-interface/coin/add"
SHARE_VIDEO_URL = "https://api.bilibili.com/x/web-interface/share/add"
WATCH_VIDEO_URL = "https://api.bilibili.com/x/click-interface/web/heartbeat"
LIVE_SIGN_URL = "https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign"
MANGA_SIGN_URL = "https://manga.bilibili.com/twirp/activity.v1.Activity/ClockIn"

# 默认配置
# DEFAULT_TASK_CONFIG = "live_sign,manga_sign,share_video,add_coin"
DEFAULT_TASK_CONFIG = "share_video,add_coin"
DEFAULT_COIN_ADD_NUM = "1"
DEFAULT_COIN_SELECT_LIKE = "1"
DEFAULT_COIN_VIDEO_SOURCE = "dynamic"

# 忽略失败关键字
IGNORE_FAIL_KEYWORDS = ["未配置", "跳过", "已下线"]

# 默认视频（用于分享和观看）
DEFAULT_BVID = "BV1GJ411x7h7"


class BilibiliClient:
    """B站签到客户端"""

    def __init__(self, cookie: str) -> None:
        """初始化客户端

        Args:
            cookie: B站 Cookie 字符串
        """
        self.cookie = cookie
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.bilibili.com/",
            "Cookie": cookie,
        }
        self.csrf = self._get_csrf()

    def _get_csrf(self) -> Union[str, None]:
        """从 Cookie 中提取 CSRF token（bili_jct）

        Returns:
            CSRF token 字符串，未找到返回 None
        """
        for item in self.cookie.split(";"):
            if item.strip().startswith("bili_jct"):
                return item.split("=")[1]
        return None

    def _make_request(
        self, url: str, method: str = "GET", data: Union[dict[str, Any], None] = None
    ) -> dict[str, Any]:
        """统一请求方法

        Args:
            url: 请求 URL
            method: 请求方法（GET 或 POST）
            data: POST 请求数据

        Returns:
            响应 JSON 数据
        """
        if method.upper() == "GET":
            res = requests.get(url, headers=self.headers, params=data)
        else:
            res = requests.post(url, headers=self.headers, data=data)
        res.raise_for_status()
        return res.json()

    def get_user_info(self) -> Union[dict[str, Any], None]:
        """获取用户信息

        Returns:
            用户信息字典，失败返回 None
        """
        data = self._make_request(USER_INFO_URL)
        if data and data.get("code") == 0:
            return data.get("data")
        logger.warning(
            f"获取用户信息失败: {data.get('message') if data else '网络错误'}"
        )
        return None

    def get_dynamic_videos(self) -> list[str]:
        """获取动态视频列表

        Returns:
            视频 bvid 列表
        """
        data = self._make_request(DYNAMIC_VIDEOS_URL)
        if data and data.get("code") == 0:
            return [video["bvid"] for video in data.get("data", {}).get("archives", [])]
        return []

    def get_ranking_videos(self) -> list[str]:
        """获取排行榜视频列表

        Returns:
            视频 bvid 列表
        """
        data = self._make_request(RANKING_VIDEOS_URL)
        if data and data.get("code") == 0:
            return [video["bvid"] for video in data.get("data", {}).get("list", [])]
        return []

    def check_video_coin_status(self, bvid: str) -> bool:
        """检查视频是否已投币

        Args:
            bvid: 视频 bvid

        Returns:
            已投币返回 True，否则返回 False
        """
        data = self._make_request(COIN_STATUS_URL.format(bvid))
        if data and data.get("code") == 0:
            return data.get("data", {}).get("multiply", 0) > 0
        return False

    def add_coin(
        self, bvid: str, num: int = 1, select_like: int = 1
    ) -> tuple[bool, str]:
        """为视频投币

        Args:
            bvid: 视频 bvid
            num: 投币数量
            select_like: 是否同时点赞（1 是，0 否）

        Returns:
            (是否成功, 消息)
        """
        if not self.csrf:
            return False, "Bili_jct(csrf) 未找到"

        payload = {
            "bvid": bvid,
            "multiply": num,
            "select_like": select_like,
            "csrf": self.csrf,
        }
        data = self._make_request(COIN_ADD_URL, method="POST", data=payload)
        if data and data.get("code") == 0:
            return True, "投币成功"
        return False, data.get("message", "投币失败") if data else "网络错误"

    def share_video(self, bvid: str) -> tuple[bool, str]:
        """分享视频

        Args:
            bvid: 视频 bvid

        Returns:
            (是否成功, 消息)
        """
        if not self.csrf:
            return False, "Bili_jct(csrf) 未找到"

        payload = {"bvid": bvid, "csrf": self.csrf}
        data = self._make_request(SHARE_VIDEO_URL, method="POST", data=payload)
        if data and data.get("code") == 0:
            return True, "分享成功"
        return False, data.get("message", "分享失败") if data else "网络错误"

    def watch_video(self, bvid: str) -> tuple[bool, str]:
        """观看视频

        Args:
            bvid: 视频 bvid

        Returns:
            (是否成功, 消息)
        """
        payload = {"bvid": bvid, "played_time": 30, "csrf": self.csrf}
        data = self._make_request(WATCH_VIDEO_URL, method="POST", data=payload)
        if data and data.get("code") == 0:
            return True, "观看成功"
        return False, data.get("message", "观看失败") if data else "网络错误"

    def live_sign(self) -> tuple[bool, str]:
        """直播签到

        Returns:
            (是否成功, 消息)
        """
        data = self._make_request(LIVE_SIGN_URL)
        if data and data.get("code") == 0:
            return True, data.get("data", {}).get("text", "直播签到成功")
        return False, data.get("message", "直播签到失败") if data else "网络错误"

    def manga_sign(self) -> tuple[bool, str]:
        """漫画签到

        Returns:
            (是否成功, 消息)
        """
        payload = {"platform": "ios"}
        data = self._make_request(MANGA_SIGN_URL, method="POST", data=payload)
        if data and data.get("code") == 0:
            return True, "漫画签到成功"
        return False, data.get("message", "漫画签到失败") if data else "网络错误"

    def execute_coin_task(
        self,
        user_info: dict[str, Any],
        coin_add_num: int,
        select_like: int,
        video_source: str,
    ) -> tuple[bool, str]:
        """执行投币任务

        Args:
            user_info: 用户信息
            coin_add_num: 投币数量
            select_like: 是否同时点赞
            video_source: 视频来源（dynamic 或 ranking）

        Returns:
            (是否成功, 消息)
        """
        if coin_add_num <= 0:
            return True, "配置为0，跳过"

        coin_balance = user_info.get("money", 0)
        if coin_balance < 1:
            return True, f"硬币不足({coin_balance})，跳过"

        coin_add_num = min(coin_add_num, int(coin_balance), 5)

        if video_source == "ranking":
            video_list = self.get_ranking_videos()
            logger.info("获取排行榜视频作为投币目标")
        else:
            video_list = self.get_dynamic_videos()
            logger.info("获取动态视频作为投币目标")

        if not video_list:
            return False, "无法获取视频列表"

        added_coins = 0
        for bvid in video_list:
            if added_coins >= coin_add_num:
                break

            success, msg = self.add_coin(bvid, 1, select_like)
            if success:
                added_coins += 1
                logger.info(f"为视频 {bvid} 投币成功")
            elif "已达到" in msg:
                logger.warning("今日投币上限已满，终止投币")
                break
            else:
                logger.warning(f"为视频 {bvid} 投币失败: {msg}")
                if "硬币不足" in msg:
                    break

        return True, f"尝试投币，最终成功 {added_coins} 枚"

    @staticmethod
    def mask_string(s: str) -> str:
        """脱敏字符串

        Args:
            s: 原始字符串

        Returns:
            脱敏后的字符串（首字符 + 星号）
        """
        if not isinstance(s, str) or len(s) == 0:
            return "*"
        return s[0] + "*" * (len(s) - 1)

    @staticmethod
    def mask_uid(uid: Union[str, int]) -> str:
        """脱敏 UID

        Args:
            uid: 用户 ID

        Returns:
            脱敏后的 UID（前两位 + 星号）
        """
        uid_str = str(uid)
        if len(uid_str) <= 2:
            return uid_str[0] + "*"
        return uid_str[:2] + "*" * (len(uid_str) - 2)


class TaskRunner:
    """任务执行器"""

    def __init__(
        self,
        client: BilibiliClient,
        task_config: str,
        coin_add_num: int,
        coin_select_like: int,
        coin_video_source: str,
    ) -> None:
        """初始化任务执行器

        Args:
            client: B站客户端
            task_config: 任务配置
            coin_add_num: 投币数量
            coin_select_like: 是否同时点赞
            coin_video_source: 视频来源
        """
        self.client = client
        self.tasks_to_run = [
            task.strip() for task in task_config.split(",") if task.strip()
        ]
        if not self.tasks_to_run:
            self.tasks_to_run = ["live_sign", "manga_sign", "share_video", "add_coin"]
        self.coin_add_num = coin_add_num
        self.coin_select_like = coin_select_like
        self.coin_video_source = coin_video_source

    def run(self) -> tuple[dict[str, tuple[bool, str]], Union[dict[str, Any], None]]:
        """执行所有任务

        Returns:
            (任务结果字典, 用户信息)
        """
        user_info = self.client.get_user_info()
        if not user_info:
            return {"登录检查": (False, "Cookie失效或网络问题")}, None

        masked_uname = self.client.mask_string(user_info.get("uname", ""))
        logger.info(f"账号名称: {masked_uname}")

        tasks_result: dict[str, tuple[bool, str]] = {}

        # 获取用于分享和观看的视频
        video_list = self.client.get_dynamic_videos()
        bvid_for_task = video_list[0] if video_list else DEFAULT_BVID

        # 执行各项任务
        if "share_video" in self.tasks_to_run:
            tasks_result["分享视频"] = self.client.share_video(bvid_for_task)
        if "live_sign" in self.tasks_to_run:
            tasks_result["直播签到"] = self.client.live_sign()
        if "manga_sign" in self.tasks_to_run:
            tasks_result["漫画签到"] = self.client.manga_sign()
        if "add_coin" in self.tasks_to_run:
            tasks_result["投币任务"] = self.client.execute_coin_task(
                user_info,
                self.coin_add_num,
                self.coin_select_like,
                self.coin_video_source,
            )

        # 观看视频（始终执行）
        tasks_result["观看视频"] = self.client.watch_video(bvid_for_task)

        return tasks_result, user_info


class App:
    """B站签到应用"""

    def __init__(self) -> None:
        """初始化应用"""
        self.cookies: list[str] = []
        self.task_config = DEFAULT_TASK_CONFIG
        self.coin_add_num = int(DEFAULT_COIN_ADD_NUM)
        self.coin_select_like = int(DEFAULT_COIN_SELECT_LIKE)
        self.coin_video_source = DEFAULT_COIN_VIDEO_SOURCE

    def load_config(self) -> None:
        """从环境变量加载配置"""
        raw_cookies = os.environ.get(ENV_COOKIES, "")
        if not raw_cookies:
            logger.error(f'请设置 {ENV_COOKIES} 环境变量, {ENV_COOKIES}="c1||c2"')
            sys.exit(1)

        for cookie in raw_cookies.split("||"):
            cookie = cookie.strip()
            self.cookies.append(cookie)
        logger.info(f"加载了 {len(self.cookies)} 个账号")

    def print_user_info(self, user_info: dict[str, Any], account_index: int) -> None:
        """打印用户信息

        Args:
            user_info: 用户信息字典
            account_index: 账号索引
        """
        logger.info(f"=== 账号{account_index} 用户信息 ===")
        logger.info(f"用户名: {BilibiliClient.mask_string(user_info.get('uname', ''))}")
        logger.info(f"UID: {BilibiliClient.mask_uid(user_info.get('mid', ''))}")
        logger.info(f"等级: {user_info.get('level_info', {}).get('current_level', 0)}")
        logger.info(f"经验: {user_info.get('level_info', {}).get('current_exp', 0)}")
        logger.info(f"硬币: {user_info.get('money', 0)}")

    def run_account(self, cookie: str, account_index: int) -> bool:
        """运行单个账号的任务

        Args:
            cookie: Cookie 字符串
            account_index: 账号索引

        Returns:
            是否全部成功
        """
        logger.info(f"=== 账号{account_index} 任务完成情况 ===")

        client = BilibiliClient(cookie)
        runner = TaskRunner(
            client,
            self.task_config,
            self.coin_add_num,
            self.coin_select_like,
            self.coin_video_source,
        )

        tasks_result, user_info = runner.run()
        final_user_info = client.get_user_info() if user_info else None

        # 统计结果
        account_failed = False
        valid_task_count = 0
        valid_success_count = 0
        masked_account_name = None

        # 输出任务日志
        for task_name, (success, msg) in tasks_result.items():
            if "push" in task_name or "推送" in task_name:
                continue

            masked_account_name = (
                BilibiliClient.mask_string(final_user_info.get("uname", ""))
                if final_user_info
                else f"账号{account_index}"
            )

            # 跳过包含忽略关键字的任务
            if msg and any(k in msg for k in IGNORE_FAIL_KEYWORDS):
                logger.info(f"[账号{account_index}] {task_name}: 跳过，原因: {msg}")
                continue

            valid_task_count += 1
            if success:
                valid_success_count += 1
                logger.info(f"[账号{account_index}] {task_name}: 成功")
            else:
                logger.error(f"[账号{account_index}] {task_name}: 失败，原因: {msg}")

        # 判断账号是否失败
        if not user_info or valid_task_count == 0 or valid_success_count == 0:
            account_failed = True

        # 输出用户信息
        if final_user_info:
            self.print_user_info(final_user_info, account_index)
        else:
            logger.error("用户信息获取失败")

        logger.info(f"--- 账号 {masked_account_name} 任务执行完毕 ---")
        logger.info("-" * 40)

        return not account_failed

    def run(self) -> None:
        """运行所有账号任务"""
        self.load_config()

        success_count = 0
        for idx, cookie in enumerate(self.cookies, 1):
            try:
                self.run_account(cookie, idx)
                success_count += 1

            except Exception:
                logger.error(
                    f"账号 {idx}: 签到失败, 错误信息: {traceback.format_exc()}"
                )
                notifier = XizhiNotifier()
                notifier.send(
                    "bilibili 签到失败",
                    f"账号 {idx}: 签到失败, 错误信息: {traceback.format_exc()}",
                )
            finally:
                logger.info("=" * 40)

        logger.info(f"签到完成: 成功 {success_count}/{len(self.cookies)}")


def main() -> None:
    """主函数"""
    app = App()
    app.run()


if __name__ == "__main__":
    main()
