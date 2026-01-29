# 使用说明
什么值得买：https://www.smzdm.com/，定时签到脚本

## 环境变量
- `SMZDM_COOKIES`：多个 cookie，用 `||` 分隔，格式为：c1||c2||c3||c4，其中 c1 为账号1的cookie，c2 为账号2的cookie，以此类推

## 本地调试
```
export SMZDM_COOKIES="c1||c2"
python main.py
```

## 参考
https://github.com/Sitoi/dailycheckin/tree/main/dailycheckin/smzdm

https://sitoi.github.io/dailycheckin/settings/smzdm/
