# MindVideo 签到脚本

自动签到 [MindVideo](https://www.mindvideo.ai/) 平台。

## 功能特性

- 支持多账号签到
- 自动生成请求签名
- 签到失败时通过息知推送通知

## 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `MINDVIDEO_ACCOUNTS` | 是 | 账号信息，格式: `email:password`，多账号用 `\|\|` 分隔 |
| `XIZHI_KEY` | 否 | 息知推送 Key，用于签到失败通知 |

## 账号格式说明

密码需要使用 MD5 加密后的值，格式示例：

```
email@example.com:md5_password||email2@example.com:md5_password2
```

## 本地运行

```bash
export MINDVIDEO_ACCOUNTS="your_email:your_md5_password"
python -m mindvideo.main
```

## GitHub Actions

1. 在仓库 Settings -> Secrets and variables -> Actions 中添加 `MINDVIDEO_ACCOUNTS`
2. 可选添加 `XIZHI_KEY` 用于失败通知
3. 工作流每天 UTC 0:00 (北京时间 8:00) 自动执行，也可手动触发
