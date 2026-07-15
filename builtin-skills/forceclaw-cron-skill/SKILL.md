---
name: forceclaw-cron-skill
description: |
  [MANDATORY - MUST LOAD] 凡是涉及定时/提醒/闹钟/周期执行/打卡/签到/cron/schedule/remind 等需求，以及修改/编辑/更新/暂停/恢复/删除/取消推送/改推送目标等已有定时任务的操作，必须读取本 skill，严禁凭记忆猜测参数。
metadata: {"openclaw": {"emoji": "⚙️"}}
---

### cron — 定时任务

> 🚨 **[MANDATORY]** 用户提到「提醒/定时/每天X点/X分钟后/周期/重复/打卡/签到」等时，**必须创建 cron 任务**，口头承诺无效。

#### 第一步：判断「推送目标」

> 🚨 **[MANDATORY] 默认就在用户当前所处渠道提醒，禁止主动反问"推送到哪里"**。
> 用户说「提醒我 / 叫我 / 告诉我 / 让我」等**自指代**表达 → 推送目标 = **当前会话渠道**，不要追问。
> 仅当用户**显式**说"推到飞书/发到飞书"等**他指代**时，才切换到飞书渠道。

| 当前会话入口 | 推送目标 | mode |
|-------------|---------|------|
| App 内聊天（`openclaw-control-ui`） | 本地（不投递，直接渲染回复） | **`none`** |
| 飞书（`feishu`） | 飞书 | **`announce`** |
| App 内 + 用户说"推到飞书" | 飞书 | **`announce`**（先读 `~/.forceclaw/channel-defaults.json` 取 `to`） |

#### 第二步：判断创建方式

| 场景 | 方式 |
|------|------|
| App 内（`openclaw-control-ui`） | **A：内置 `cron` 工具**（toolCall，JSON 参数） |
| 飞书渠道 session 内（`feishu`） | **B：`openclaw cron add` CLI**（通过 `exec`，飞书 session 中 cron 工具被 ownerOnly 策略过滤，LLM 不可见） |
| App 内但推送到飞书 | **B：CLI**（先读 `~/.forceclaw/channel-defaults.json` 取 `to`） |

> 🚨 **[MANDATORY] 飞书渠道 `to` 获取规则**：
> - **飞书 session 有 `sender_id`** → 直接用作 `to`
> - **App 内推送到飞书（无 `sender_id`）** → 必须读 `~/.forceclaw/channel-defaults.json`，在 `json[当前agentId].feishu` 中查找 `to`
> - **找不到 `to`** → ⛔ 禁止创建，告知用户：「请先在飞书里给机器人发一条消息，之后再来创建定时任务」

> 🚨 **[MANDATORY] agent 隔离原则**：
> `~/.forceclaw/channel-defaults.json` 按 agentId 分桶存储。当前 agent=X 时，**只能读 `json[X]`**，禁止跨 agent 取值。找不到就中止并提示用户去飞书发一条消息。

#### 第三步：时间类型

- 具体时刻 / X分钟后 / 无周期词 → **一次性**（`deleteAfterRun:true` / `--delete-after-run`）
- 每天/每小时/每X分钟 → **周期任务**
- **绝对时间必须先 `date +%z` 获取时区**（`+0800`→`+08:00`），禁止硬编码

#### 第四步：时间参数速查

| 用户说法 | schedule（JSON） | CLI 参数 |
|---------|-----------------|----------|
| 每30分钟 | `{"kind":"every","everyMs":1800000}` | `--every 30m` |
| 每2小时 | `{"kind":"every","everyMs":7200000}` | `--every 2h` |
| 每天早上9点 | `{"kind":"cron","cron":"0 9 * * *"}` | `--cron "0 9 * * *"` |
| 每周一10点 | `{"kind":"cron","cron":"0 10 * * 1"}` | `--cron "0 10 * * 1"` |
| 工作日18点 | `{"kind":"cron","cron":"0 18 * * 1-5"}` | `--cron "0 18 * * 1-5"` |
| 今天下午3点 | `{"kind":"at","at":"2026-04-09T15:00:00+08:00"}` | `--at "..." --delete-after-run` |
| 10分钟后 | `{"kind":"at","at":"<now+10min ISO>"}` | `--at "..." --delete-after-run` |

> cron 表达式：`分 时 日 月 星期`，0=周日，1-5=周一至五。

#### 公共规则

> 🚨 **[MANDATORY] message 行为约束**：`payload.message`（方式A）/ `--message`（方式B）末尾**必须**加：
> `要求：(1) 不要回复 HEARTBEAT_OK (2) 不要调用 message 工具 (3) 直接输出提醒文字 (4) 控制在 2-3 句话以内`

> 🚨 **[MANDATORY] agentId 必传**：从 sessionKey（`agent:【agentId】:session-xxx` → 取第二段）或 cwd（`workspace-agent-xxx` → 取最后一段）提取；以上均无才传 `"main"`。禁止复用历史对话中的 agentId。

> 🚨 **[MANDATORY] mode 必须显式传入**：App 内 → `"none"`；飞书/推送到飞书 → `"announce"`。

**delivery 值速查：**

| 场景 | delivery |
|------|----------|
| App 内本地提醒 | `{"mode":"none"}` |
| 飞书推送 | `{"mode":"announce","channel":"feishu","to":"<sender_id>"}` |

**禁止事项：**
- 🚫 禁止指定执行 model（插件强制剥离；创建成功后在回复中追加一句「⚠️ 任务创建成功，但目前不支持通过对话指定执行 model，请手动在管理页面进行修改」）
- 🚫 禁止指定 `timeoutSeconds`（插件强制剥离；不告知用户，不出现"超时"字样）

#### 方式 A：App 内 — cron 工具模板

> 🚨 调用 toolName=`cron`，参数为 JSON 对象。

**周期任务**：
```json
{
  "action": "add",
  "job": {
    "name": "<任务名>", "agentId": "<agentId>",
    "schedule": {"kind":"every","everyMs":1800000},
    "sessionTarget": "isolated",
    "payload": {"kind":"agentTurn","message":"你是一个暖心的提醒助手。请用温暖、有趣的方式提醒用户：{内容}。要求：(1) 不要回复 HEARTBEAT_OK (2) 不要调用 message 工具 (3) 直接输出提醒文字 (4) 控制在 2-3 句话以内"},
    "delivery": {"mode":"none"}
  }
}
```
**一次性**：schedule→`{"kind":"at","at":"<ISO+时区>"}`，加 `"deleteAfterRun":true`

#### 方式 B：飞书 — openclaw cron add CLI

```bash
openclaw cron add \
  --name "<任务名>" --every 30m --session isolated --agent <agentId> \
  --message "你是一个暖心的提醒助手。请用温暖、有趣的方式提醒用户：{内容}。要求：(1) 不要回复 HEARTBEAT_OK (2) 不要调用 message 工具 (3) 直接输出提醒文字 (4) 控制在 2-3 句话以内" \
  --announce --channel feishu --to <sender_id>
```
**一次性**：`--every 30m` → `--at "<ISO+时区>" --delete-after-run`

> 🚨 命令失败最多重试一次，仍失败直接告知用户。

#### 管理命令

> 暂停/停止 ≠ 删除。"暂停/禁用"→disable，"删除"→remove。

**内置工具**：列表 `{"action":"list"}` / 暂停 `{"action":"update","jobId":"<id>","patch":{"enabled":false}}` / 恢复 `…{"enabled":true}` / 删除 `{"action":"remove","jobId":"<id>"}` / 执行 `{"action":"run","jobId":"<id>"}`

**CLI**：`openclaw cron list` / `edit <id> --enabled false/true` / `remove <id>` / `run <id>`

#### 🚨 修改任务专用规则

**规则 1：patch 是增量覆盖，不是整体替换**

> 🚨 `patch.delivery` 仅覆盖**显式传入的字段**。想清掉某字段必须**显式传空串**：`{"channel":"","to":""}`。**不传 ≠ 清除！**

**规则 2：取消推送的唯一正确方式**

> 用户说「取消推送 / 改回本地提醒」→ 统一识别为取消推送：
> - **tool 路径**：`patch.delivery = {"mode":"none","channel":"","to":""}`
> - **CLI 路径**：`openclaw cron edit <id> --no-deliver`

**修改速查表：**

| 用户表达 | 内置工具（patch.delivery） | CLI |
|---------|---------------------------|-----|
| "取消推送" / "改回本地提醒" | `{"mode":"none","channel":"","to":""}` | `--no-deliver` |
| "改成推送到飞书" | `{"mode":"announce","channel":"feishu","to":"<to>"}` | `--announce --channel feishu --to <to>` |

#### 回复模板

一次性：`⏰ 好的，{时间}提醒你{内容}~` | 周期：`⏰ 收到，{周期}提醒你{内容}~` | 取消：`✅ 已取消"{名称}"`

> 飞书渠道只输出确认话术，严禁输出推理过程。