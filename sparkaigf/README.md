# SparkAI 签到

https://ai.sparkaigf.com/

## 环境变量

| 变量名 | 说明 | 格式 |
|--------|------|------|
| `SPARKAIGF_ACCOUNTS` | 账号信息 | `用户名:密码` |
| `XIZHI_KEY` | 息知推送 Key（可选） | `key` |

## 配置示例

```bash
# 单账号
SPARKAIGF_ACCOUNTS="username:password"

# 多账号（使用 || 分隔）
SPARKAIGF_ACCOUNTS="user1:pass1||user2:pass2"
```

## 本地运行

```bash
SPARKAIGF_ACCOUNTS="username:password" python -m sparkaigf.main
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/login` | POST | 登录获取 Token |
| `/api/signin/sign` | POST | 执行签到 |
| `/api/signin/signinLog` | GET | 获取签到记录 |
