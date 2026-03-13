# my_checkin_scripts

基于 GitHub Actions 的多平台签到脚本集合，支持自动签到并推送通知。

## 目录结构

```
my_checkin_scripts/
├── glados/           # GLaDOS 梯子网站签到
├── music163/         # 网易云音乐签到
├── smzdm/            # 什么值得买签到
├── maidanba/         # 交通银行买单吧签到
├── sparkaigf/        # 通义千问 Spark AI 签到
├── mindvideo/        # 思维视频签到
├── bilibili/         # B 站签到
├── 996coder/         # 996Coder 签到
├── dawclaudecode/    # DawClaudeCode 签到
├── duckcoding/       # DuckCoding 签到
├── linkapi/          # LinkAPI 签到
├── magic666/         # Magic666 签到
├── mulan/            # 木兰图片编辑签到
└── utils/            # 通用工具模块
    └── notify.py     # 消息通知工具
```

## 功能模块

### 梯子服务

| 模块 | 平台 | 状态 |
|------|------|------|
| glados | [GLaDOS](https://glados.cloud) | ✅ |

### 视频娱乐

| 模块 | 平台 | 状态 |
|------|------|------|
| bilibili | [B站](https://bilibili.com) | 🔴 已禁用 |
| music163 | [网易云音乐](https://music.163.com) | ✅ |

### 信用卡金融

| 模块 | 平台 | 状态 |
|------|------|------|
| maidanba | 交通银行买单吧 | 🔴 已禁用 |
| smzdm | [什么值得买](https://www.smzdm.com) | ✅ |

| 模块 | 平台 | 状态 |
|------|------|------|
| 996coder | [996Coder](https://996coder.com) | ✅ |
| mulan | [木兰](https://mulan.pro) | ✅ |
| dawclaudecode | DawClaudeCode | ✅ |
| duckcoding | DuckCoding | ✅ |
| linkapi | LinkAPI | ✅ |
| magic666 | Magic666 | ✅ |
| mindvideo | 思维视频 | ✅ |
| sparkaigf | 通义千问 Spark AI | ✅ |

## 快速开始

### 环境要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) - Python 包管理器

### 安装依赖

```bash
uv sync
```

### 通用环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `XIZHI_KEY` | 否 | [息知](https://xz.ma) 推送通知密钥 |

### 本地调试

```bash
# 设置环境变量
export XIZHI_KEY="your_xizhi_key"

# 运行指定模块
uv run python -m glados.main
uv run python -m bilibili.main
```

## 抓包工具

### Proxyman MCP 服务

推荐使用 [Proxyman MCP](https://docs.proxyman.com/mcp) 服务进行抓包：

1. 安装 Proxyman：https://proxyman.io
2. 配置 MCP 服务
3. 抓取目标请求的 Cookie 和 Token

### 其他工具

- Charles
- Fiddler

## 配置说明

各模块详细配置请查看对应目录下的 README.md：

- [GLaDOS 配置](./glados/README.md)
- [B站 配置](./bilibili/README.md)
- [买单吧 配置](./maidanba/README.md)
- [996Coder 配置](./996coder/README.md)
- [木兰 配置](./mulan/README.md)

## 注意事项

1. **Cookie 有效期**：部分平台的 Cookie 会过期，需要定期更新
2. **多账号配置**：使用 `||` 分隔多个账号
3. **账号安全**：建议使用 GitHub Actions Secrets 存储敏感信息

## 许可证

MIT License
