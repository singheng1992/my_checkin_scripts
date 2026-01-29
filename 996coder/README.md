# 使用说明
996coder：https://996coder.com/，定时签到脚本

## 环境变量
- `NINENINESIX_CODER_ACCOUNTS`：多个 cookie，用 `||` 分隔，格式为：c1||c2||c3||c4，其中 c1 为账号1的cookie，c2 为账号2的cookie，以此类推

## 本地调试
```
export NINENINESIX_CODER_ACCOUNTS="email1:password1||email2:password2"
python main.py
```

## 参考
