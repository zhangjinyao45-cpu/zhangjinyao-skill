---
name: force-agent-runner
description: 度小满原力 AI 平台（ai-force.duxiaoman-int.com / dxm-agent.duxiaoman-int.com）智能体 API 运行器。当用户提供原力平台的智能体链接（agentId=... 或 /space/.../bot/...）或直接给出 agentId / bot_id，希望通过接口调用、测试、调试该智能体，进行对话、多轮聊天、查询/清空/删除会话，或需要获取 APIKey 时，使用本 skill。支持 dev（dxm-agent.duxiaoman-int.com）和 prod（ai-force.duxiaoman-int.com）双环境自动切换。
---

# Force Agent Runner

通过 HTTP 调用度小满原力 AI 平台智能体，完成 **获取 APIKey → 创建会话 → 多轮 chat** 完整流程。

## 环境与参数自动获取

| 参数 | 自动来源 |
|------|---------|
| `UUAP-ID` | 环境变量 `UUAP_ID` |
| `UUAP_COOKIE` | 环境变量 `UUAP_COOKIE` |
| `APIKey` | 每次调用前实时调 `getTestKey` 接口获取，不存盘 |
| `env` | 链接域名自动判断：`dxm-agent.*` → dev，`ai-force.*` → prod，默认 prod |
| `agentId` / `bot_id` | 正则解析链接，或用户直接提供 |

## 标准工作流

### 首次使用

```bash
# 直接 auto，APIKey 自动实时获取（需要 UUAP_COOKIE 环境变量）
python scripts/run.py auto "https://ai-force.duxiaoman-int.com/agentcube/space/.../bot/..." "你好"
```

### 已有 APIKey

```bash
# auto：解析链接 → 创建会话 → chat（bot_id 也可直接传）
python scripts/run.py auto "<链接或bot_id>" "问题"

# 多轮对话（复用已有 conversation_id）
python scripts/run.py chat "第二个问题"
```

### 手动分步

```bash
python scripts/run.py init --link "<url>" [--api-key <key>] [--env dev|prod]
python scripts/run.py create
python scripts/run.py chat "问题"
```

## 所有子命令

| 命令 | 说明 |
|------|------|
| `auto <url或id> "问题"` | 一键：解析 → 实时获取 APIKey → 创建会话 → chat |
| `init [--link] [--agent-id] [--bot-id] [--env]` | 保存配置，不发请求 |
| `create` | 创建新会话 |
| `chat "文本"` | 向当前会话发消息 |
| `list` | 查询当前会话历史消息 |
| `conversations` | 查询 bot 的所有会话 |
| `clear` | 清空当前会话上下文 |
| `delete` | 删除当前会话 |
| `show` | 查看配置（APIKey / Cookie 打码） |

## 链接格式

- 智能体详情链接：`https://ai-force.duxiaoman-int.com/chat/agent/detail?agentId=<19位>`
- 智能体调试链接：`https://ai-force.duxiaoman-int.com/agentcube/space/<space_id>/bot/<bot_id>`
- dev 环境：域名替换为 `dxm-agent.duxiaoman-int.com`，env 自动识别为 dev

## 环境策略

**始终使用 prod 环境（ai-force.duxiaoman-int.com）**，除非用户明确说"测试环境"、"dev 环境"。

遇到任何错误，先在 prod 环境排查，不要自行切换环境。

## 常见错误

| 现象 | 原因 | 处理 |
|------|------|------|
| `HTTP 500 / code=500 / 用户无权限` | **APIKey 与 bot_id 不匹配**，或该 UUAP 对此 bot 无权限 | 优先检查 APIKey 是否对应当前 bot：重新执行一次（APIKey 每次实时获取），若仍失败则确认 bot_id 是否正确，或联系 bot 管理员确认权限 |
| `code=40001 not login` | UUAP_COOKIE 失效 | 等待 ForceClaw 刷新 Cookie 后重试 |
| `getTestKey 未找到 APIKey` | 接口响应结构变化 | 查看原始响应确认字段路径 |
| `UUAP_COOKIE 缺失` | 环境变量未注入 | ForceClaw 已自动注入，检查是否重启生效 |
| `conversation not found` | conversation_id 与 bot_id 不匹配 | 执行 `create` 重建会话 |

## 安全要求

- APIKey 和 UUAP_COOKIE **不回显完整值**，`show` 命令自动打码
- config.json 权限锁定为 600
- 拒绝使用他人 UUAP 或 Cookie 调用无权限的 bot
