---
name: force-workflow-runner
description: 度小满原力 AI 平台（ai-force.duxiaoman-int.com）Workflow API 运行器。当用户希望通过接口调用、测试、调试原力平台上的工作流（workflow），提供工作流编辑页链接（/project-ide/.../workflow/...）、agentId、app_id、workflow_id 或相关链接，需要执行非流式（同步/异步）或流式（SSE）工作流时，使用本 skill。支持直接传入链接自动解析 agentId、app_id、workflow_id，无需手动拆分参数。
---

# Force Workflow Runner

通过 HTTP 调用度小满原力 AI 平台的 Workflow API，支持**非流式（同步/异步）**和**流式（SSE）**两种执行模式。

## 环境与参数自动获取

| 参数 | 来源 |
|------|------|
| `UUAP-ID` | 环境变量 `UUAP_ID`（ForceClaw 自动注入） |
| `UUAP_COOKIE` | 环境变量 `UUAP_COOKIE`（ForceClaw 自动注入） |
| `APIKey` | 每次调用前实时调 `getTestKey` 接口获取，不存盘 |
| `env` | 链接域名自动判断，默认 prod |
| `agentId` / `app_id` / `workflow_id` | 自动解析工作流链接，或用户直接提供，或通过 `init` 保存后复用 |

## 环境策略

**始终使用 prod 环境（ai-force.duxiaoman-int.com）**，除非用户明确说"测试环境"、"dev 环境"。遇到任何错误，先在 prod 环境排查，不要自行切换环境。

## 标准工作流

### 一次性执行（不保存配置）

```bash
# 非流式同步
python scripts/run.py run \
  --agent-id <agentId> --app-id <app_id> --workflow-id <workflow_id> \
  --params '{"input": "你好"}'

# 流式（SSE）
python scripts/run.py stream \
  --agent-id <agentId> --app-id <app_id> --workflow-id <workflow_id> \
  --params '{"input": "你好"}'
```

### 保存配置后反复调用

```bash
# 保存配置
python scripts/run.py init --agent-id <id> --app-id <id> --workflow-id <id>

# 之后直接调用（从 config 读取）
python scripts/run.py run --params '{"input": "你好"}'
python scripts/run.py stream --params '{"input": "你好"}'
```

## 所有子命令

| 命令 | 说明 |
|------|------|
| `run [--agent-id] [--app-id] [--workflow-id] [--params] [--async]` | 非流式执行，`--async` 表示异步 |
| `stream [--agent-id] [--app-id] [--workflow-id] [--params]` | 流式执行（SSE），实时输出结果 |
| `init [--link] [--agent-id] [--app-id] [--workflow-id] [--env]` | 保存配置，不发请求 |
| `show` | 查看当前 config |

## 链接解析

工作流编辑页链接可直接传给 `--link`，自动解析所有参数：

```
https://ai-force.duxiaoman-int.com/agentcube/space/<space_id>/project-ide/<app_id>/workflow/<workflow_id>
```

智能体详情链接可解析 agentId：

```
https://ai-force.duxiaoman-int.com/chat/agent/detail?agentId=<agentId>
```

示例（一步调用，无需 init）：

```bash
python scripts/run.py run \
  --link "https://ai-force.duxiaoman-int.com/agentcube/space/<space_id>/project-ide/<app_id>/workflow/<workflow_id>" \
  --params '{"input": "你好"}'
```



- 非流式：`POST /agent-force-gateway/workflow/run`
- 流式：`POST /agent-force-gateway/workflow/stream_run`
- 必需请求头：`UUAP-ID`、`REQUEST-ID`（自动生成）、`Authorization`、`agentId`

## 请求体关键字段

根据官方文档（`Agent网关workflow api使用文档`），请求体结构为：

```json
{
  "workflow_id": "string",
  "parameters": {"k": "v"},
  "app_id": "string",
  "is_async": false
}
```

- **`parameters`**（不是 `inputs`）：开始节点输入参数，JSON 结构
- `parameters` 中的 key 名对应工作流开始节点定义的参数名（如 `input`、`image_data` 等）

## APIKey 获取策略

`getTestKey` 接口：固定使用 **`type=1` + `app_id`** 获取 APIKey。

## ⚠️ 重要：禁止本地实现工作流内部能力，必须使用脚本中的工作流来完成任务，禁止自由发挥。

**工作流内部包含的节点（如 paddle-ocr、LLM 调用、代码执行等）由平台服务端执行，模型只需要将输入参数传给工作流 API，不要在本地安装或运行这些工具。**

典型错误场景：用户说「用 paddle-ocr 识别图片」并给了一个工作流链接 → 模型去本地 `uv run --with paddleocr` 安装运行 → **错误**。正确做法是：将图片 base64 编码后作为 `image_data` 参数传给工作流 `--params`，由工作流内部节点完成 OCR 识别。

**原则：工作流能做的事，不要本地重复实现。只负责准备输入数据（如 base64 编码），调用 API，返回结果。**

## 常见错误

| 现象 | 原因 | 处理 |
|------|------|------|
| `HTTP 500 / code=500 / 用户无权限` | APIKey 与 agentId 不匹配，或该 UUAP 对此 workflow 无权限 | 优先检查 agentId 和 workflow_id 是否正确，APIKey 每次实时获取无需手动干预 |
| `code=40001 not login` | UUAP_COOKIE 失效 | 等待 ForceClaw 刷新 Cookie 后重试 |
| `getTestKey 所有尝试均未获取到 APIKey` | agentId/app_id 不正确或工作流未发布 | 检查 agentId、app_id 是否正确；确认工作流已发布 |
| `param field error` | 请求体字段名错误或参数值格式不对 | 确认使用 `parameters`（非 `inputs`），确认参数名与工作流开始节点一致 |
| `配置缺失: agentId / app_id / workflow_id` | 参数未提供且 config 中无记录 | 通过 `--agent-id`、`--app-id`、`--workflow-id` 传入，或先执行 `init` |
| 异步执行拿不到结果 | 异步模式只返回 execute_id | 在工作流末尾添加 HTTP 回调节点，或改用同步模式 |

## 参考资料
- 官方 API 文档：[Agent网关workflow api使用文档](https://duxiaoman.feishu.cn/wiki/XbzVwDkpbiGo7UkGUmSc8YUOnOh)
| 异步执行拿不到结果 | 异步模式只返回 execute_id | 在工作流末尾添加 HTTP 回调节点，或改用同步模式 |
