# 使用说明
duckcoding定时签到脚本：https://duckcoding.com

## 环境变量
- `DUCKCODING_ACCOUNTS`：多个账号密码，用 `||` 分隔，格式为 `email:password`，例如：email1:password1||email2:password2"

## 本地调试
```
export DUCKCODING_ACCOUNTS="email1:password1||email2:password2"
export XIZHI_KEY="your_xizhi_key"
uv run python -m duckcoding.main
```
