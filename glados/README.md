# 使用说明
梯子网站：https://glados.cloud/，定时签到脚本

## 环境变量
- `GLADOS_COOKIES`：多个账号，用 `&` 分隔，格式为：c1&c3&c3&c4，其中 c1 为账号1的cookie，c2 为账号2的cookie，以此类推

## 本地调试
```
export GLADOS_COOKIES="c1||c2"
python main.py
```

## 参考
https://github.com/Devilstore/Gladoscheckin

https://github.com/chinesedfan/daily-checkin-bot