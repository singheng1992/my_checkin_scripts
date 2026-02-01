# 买单吧签到

交通银行信用卡「买单吧」App 每日签到脚本

## 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `MAIDANBA_ACCOUNTS` | 是 | 账号信息，格式：`cookie#token`，多账号用 `\|\|` 分隔 |

## 获取 Cookie 和 Token

1. 使用 Proxyman / Charles 等抓包工具
2. 打开买单吧 App，进入签到页面
3. 抓取 `https://creditcardapp.bankcomm.com/mdlweb/sign/data` 请求
4. 从请求中提取：
   - `Cookie` 请求头 → cookie 部分
   - URL 参数 `?token=xxx` → token 部分

## 本地调试

```bash
export MAIDANBA_ACCOUNTS="JSESSIONID=xxx#token值"
python -m maidanba.main
```

## 多账号配置

```bash
export MAIDANBA_ACCOUNTS="cookie1#token1||cookie2#token2"
```

## 签到奖励

- 每日签到可获得 10 积分
- 连续签到 7 天有额外奖励
