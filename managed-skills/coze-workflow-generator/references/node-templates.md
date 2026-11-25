# 原力平台工作流节点完整参考

本文件包含所有已知节点类型的完整 JSON 模板，供 AI 生成工作流时参考。

## 目录

1. 通用：异常处理 settingOnError
2. 通用：object/list[object] 输出 schema
3. 大模型 (type=3)
4. 插件调用 (type=4)
5. 代码 (type=5)
6. 知识库检索 (type=6)
7. 选择器 (type=8)
8. 工作流调用 (type=9)
9. SQL自定义 (type=12)
10. 输出 (type=13, 已废弃)
11. 文本处理 (type=15)
12. 问答 (type=18)
13. 循环 (type=21)
14. 意图识别 (type=22)
15. 知识库写入 (type=27)
16. 批处理 (type=28)
17. 输入 (type=30)
18. 变量聚合 (type=32)
19. 变量赋值 (type=40)
20. 数据库节点通用说明
21. 更新数据 (type=42)
22. 查询数据 (type=43)
23. 删除数据 (type=44)
24. HTTP请求 (type=45)
25. 新增数据 (type=46)
26. JSON序列化 (type=58)
27. 连线 (Edge)
28. rawMeta.type 映射参考
29. 模型映射表

---

## ⚠️ 通用：异常处理 settingOnError 配置模板

大多数执行类节点都支持 `settingOnError`。**当 processType=2（返回设定内容）时，必须严格按以下完整格式配置，缺少任何字段都会导致异常处理不生效。**

### processType=1（默认：中断流程）

```json
"settingOnError": { "processType": 1, "timeoutMs": 60000, "retryTimes": 0 }
```

### processType=2（返回设定内容 — 最常出错）

#### ❌ 错误写法（只写了 processType=2，漏掉必需字段）

```json
"settingOnError": { "processType": 2, "timeoutMs": 60000, "retryTimes": 0 }
```

#### ✅ 正确写法（必须包含 switch + dataOnErr）

```json
"settingOnError": {
  "processType": 2,
  "switch": true,
  "timeoutMs": 60000,
  "retryTimes": 0,
  "dataOnErr": "{\n    \"output_var1\": \"\",\n    \"output_var2\": \"0\"\n}"
}
```

#### outputs 必须额外附加 errorBody 和 isSuccess

```json
"outputs": [
  { "type": "string", "name": "output_var1" },
  { "type": "integer", "name": "output_var2" },
  {
    "type": "object",
    "name": "errorBody",
    "schema": [
      { "type": "string", "name": "errorMessage", "readonly": true },
      { "type": "string", "name": "errorCode", "readonly": true }
    ],
    "readonly": true
  },
  { "type": "boolean", "name": "isSuccess", "readonly": true }
]
```

**`dataOnErr` 是 JSON 字符串**，键名必须与节点的 outputs 中每个业务输出变量名完全对应（不含 errorBody/isSuccess）。

### processType=3（执行异常流程）

```json
"settingOnError": { "processType": 3, "timeoutMs": 60000, "retryTimes": 0 }
```
节点会多出一个异常端口，需要额外连线到异常处理节点。**异常端口的 sourcePortID = `"branch_error"`**：
```json
{ "sourceNodeID": "异常源节点ID", "targetNodeID": "异常处理节点ID", "sourcePortID": "branch_error", "targetPortID": "" }
```

---

## ⚠️ 通用：object/list[object] 输出必须显式定义子变量 schema

当节点输出类型为 `object` 或 `list` + `schema.type: "object"` 时，**必须**在 `schema` 中列出所有子字段的 `name` 和 `type`。否则下游节点无法通过 `变量名.key` 引用子字段。

### ✅ 正确写法（展开子字段）

```json
// object 输出
{"type": "object", "name": "result", "schema": [
  {"type": "string", "name": "summary"},
  {"type": "integer", "name": "score"},
  {"type": "boolean", "name": "is_valid"}
]}

// list[object] 输出
{"type": "list", "name": "task_items", "schema": {"type": "object", "schema": [
  {"type": "integer", "name": "index"},
  {"type": "string", "name": "dimension"},
  {"type": "string", "name": "objective"}
]}}
```

### ❌ 错误写法（缺少子字段，下游无法引用 key）

```json
// ❌ 只写 type 不展开子字段
{"type": "object", "name": "result"}
{"type": "list", "name": "items", "schema": {"type": "object"}}
```

> 默认对所有 object 类型输出都配齐子变量。LLM 节点 responseFormat=2 (JSON) 的每个 object 输出也需要。

---

## 大模型

type=3, 调用 LLM 生成回复。

### 基础模板

```json
{
  "id": "{{NODE_ID}}",
  "type": "3",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "{{LLM_TITLE}}",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-LLM-v2.jpg",
      "description": "调用大模型来处理文本信息",
      "mainColor": "#5C62FF",
      "subTitle": "大模型"
    },
    "inputs": {
      "inputParameters": [
        {
          "name": "{{VAR_NAME}}",
          "input": {
            "type": "string",
            "value": {
              "type": "ref",
              "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{SOURCE_OUTPUT_NAME}}" },
              "rawMeta": { "type": 1 }
            }
          }
        }
      ],
      "llmParam": [
        { "name": "modleName", "input": { "type": "string", "value": { "type": "literal", "content": "GLM-5.1", "rawMeta": { "type": 1 } } } },
        { "name": "modelType", "input": { "type": "integer", "value": { "type": "literal", "content": "80014", "rawMeta": { "type": 2 } } } },
        { "name": "generationDiversity", "input": { "type": "string", "value": { "type": "literal", "content": "default_val", "rawMeta": { "type": 1 } } } },
        { "name": "temperature", "input": { "type": "float", "value": { "type": "literal", "content": "0.8", "rawMeta": { "type": 4 } } } },
        { "name": "maxTokens", "input": { "type": "integer", "value": { "type": "literal", "content": "65536", "rawMeta": { "type": 2 } } } },
        { "name": "topP", "input": { "type": "float", "value": { "type": "literal", "content": "0.95", "rawMeta": { "type": 4 } } } },
        { "name": "responseFormat", "input": { "type": "integer", "value": { "type": "literal", "content": "2", "rawMeta": { "type": 2 } } } },
        { "name": "thinking", "input": { "type": "integer", "value": { "type": "literal", "content": "0", "rawMeta": { "type": 2 } } } },
        { "name": "systemPrompt", "input": { "type": "string", "value": { "type": "literal", "content": "{{SYSTEM_PROMPT_TEXT}}", "rawMeta": { "type": 1 } } } },
        { "name": "prompt", "input": { "type": "string", "value": { "type": "literal", "content": "{{USER_PROMPT_TEXT}}", "rawMeta": { "type": 1 } } } },
        { "name": "enableChatHistory", "input": { "type": "boolean", "value": { "type": "literal", "content": false, "rawMeta": { "type": 3 } } } },
        { "name": "chatHistoryRound", "input": { "type": "integer", "value": { "type": "literal", "content": "3", "rawMeta": { "type": 2 } } } }
      ],
      "settingOnError": { "processType": 1, "timeoutMs": 300000, "retryTimes": 0 }
    },
    "outputs": [
      { "type": "string", "name": "output" },
      { "type": "string", "name": "reasoning_content" }
    ],
    "version": "3"
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 189.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-LLM-v2.jpg",
      "description": "调用大模型来处理文本信息",
      "title": "大模型",
      "mainColor": "#5C62FF"
    }
  }
}
```

### 关键规则

1. **prompt 和 systemPrompt 必须用 `literal` 类型**，绝对不能用 `ref`！否则画布显示 `[object Object]`
2. 要引用其他节点的输出，必须在 `inputParameters` 中用 `ref` 声明变量，然后在 prompt 的 literal content 中用 `{{变量名}}` 插值
3. **responseFormat 只有 3 个值**：`"0"`=文本，`"1"`=Markdown，`"2"`=JSON。不存在 3 或 4。优先使用 `"2"`
4. **LLM 默认输出包含 `output` 和 `reasoning_content` 两个固定变量**
5. `timeoutMs` 应设为 180000~600000（3~10分钟），过短容易超时

### ⚠️ 模型标识三件套（致命级，缺一不可）

模型选择**必须同时**包含以下 3 个字段，否则节点无法运行：

| 字段名 | 说明 | 注意事项 |
|--------|------|---------|
| `modleName` | 模型名称 | **注意拼写**：是 `modleName`（少一个 `e`），不是 `modelName`。这是平台历史拼写问题，已成为接口规范 |
| `modelType` | 模型类型编号 | 如 `"80009"` |
| `generationDiversity` | 生成多样性策略 | 默认 `"default_val"` |

```
❌ {"name": "modelName", ...}     ← 拼写错误，平台无法识别！
✅ {"name": "modleName", ...}     ← 正确拼写
```

### llmParam 标准字段清单

| 序号 | 字段名 | 类型 | 必填 | 说明 |
|------|--------|------|------|------|
| 1 | `modleName` | string | ✅ | 模型名称（注意拼写） |
| 2 | `modelType` | integer | ✅ | 模型类型编号 |
| 3 | `generationDiversity` | string | ✅ | 生成多样性策略 |
| 4 | `temperature` | float | ✅ | 0.1~1.0 |
| 5 | `maxTokens` | integer | ✅ | 1024~16384 |
| 6 | `topP` | float | ✅ | 一般 0.95 |
| 7 | `responseFormat` | integer | ✅ | 0/1/2 |
| 8 | `thinking` | integer | ✅ | 0=关闭, 1=开启思考模式 |
| 9 | `systemPrompt` | string | ✅ | 系统提示词（literal） |
| 10 | `prompt` | string | ✅ | 用户提示词（literal） |
| 11 | `enableChatHistory` | boolean | 建议 | 是否启用对话历史 |
| 12 | `chatHistoryRound` | integer | 建议 | 对话历史轮数 |
| ~~-~~ | ~~`modelName`~~ | | ❌ | ~~错误字段名，禁止使用~~ |
| ~~-~~ | ~~`frequencyPenalty`~~ | | ❌ | ~~平台不支持，不要生成~~ |
| ~~-~~ | ~~`presencePenalty`~~ | | ❌ | ~~平台不支持，不要生成~~ |

### LLM 参数调优说明

- `temperature`：0.1~0.3 用于分类/判断，0.5~0.7 通用，0.8~1.0 创意写作
- `maxTokens`：1024~16384，根据输出长度调整
- `topP`：一般保持 0.95 默认值
- `thinking`：复杂推理任务设为 1，简单任务设为 0
- `timeoutMs`：180000~600000（3~10分钟）

### generationDiversity 四种预设模式

| 模式值 | 含义 | temperature | thinking | maxTokens | 适用场景 |
|--------|------|-------------|----------|-----------|---------|
| `"precise"` | 精确模式 | 0.3 | 0(关闭) | 按需 | 分类/判断/结构化输出 |
| `"balance"` | 均衡模式 | 0.8 | 0(关闭) | 按需 | 通用问答/常规分析（**推荐默认**） |
| `"creative"` | 创意模式 | 1.0 | 0(关闭) | 按需 | 创意写作/头脑风暴 |
| `"default_val"` | 自定义模式 | 手动设置 | 手动设置 | 手动设置 | 需精确控制所有参数时 |

> ⚠️ **四种预设模式默认都不开启深度思考**（thinking=0）。使用预设时 temperature 仍需显式填写对应值（平台不会自动覆盖 llmParam 中的值）。如需开启深度思考，请使用 `"default_val"` 模式并手动设置 `thinking=1`。
>
> 示例：使用 `"precise"` 模式时 → `"generationDiversity": "precise"`, `"temperature": "0.3"`, `"thinking": "0"`
>
> 某些模型可能有特殊 maxTokens（如 GLM-5.1 最大 65536），用 `"default_val"` 模式手动设置。

### LLM 节点插件调用（fcParam）

**仅 DeepSeek-V3.2(80009) 和 GLM-5.1(80014) 支持在 LLM 节点中配置插件**（Function Calling）。其他模型不支持此功能。

插件配置放在 `inputs.fcParam` 中，与 `llmParam` 同级。同时需要在 `_temp.externalData.skills` 中镜像插件列表（用于 GUI 展示）。

#### fcParam 结构

```json
"fcParam": {
  "pluginFCParam": {
    "pluginList": [
      {
        "plugin_id": "7573626799205122048",
        "api_id": "7573626799226093568",
        "api_name": "web_search",
        "plugin_version": "",
        "is_draft": false
      }
    ]
  }
}
```

#### _temp.externalData.skills 镜像（必须同步）

```json
"_temp": {
  "externalData": {
    "skills": [
      {
        "type": 1,
        "pluginId": "7573626799205122048",
        "apiId": "7573626799226093568",
        "apiName": "web_search",
        "pluginName": "博查搜索",
        "icon": "..."
      }
    ]
  }
}
```

> ⚠️ `fcParam.pluginFCParam.pluginList` 和 `_temp.externalData.skills` 必须保持一致：每个插件在两处都要出现。`skills` 中额外包含 `type:1`、`pluginName`、`icon` 用于 GUI 展示。

#### 平台可用插件速查表

| 插件名 | plugin_id | api_name | api_id | 用途 |
|--------|-----------|----------|--------|------|
| **博查搜索** | 7573626799205122048 | `web_search` | 7573626799226093568 | 联网搜索 |
| **百度智能搜索** | 23 | `baidu_web_search` | 230001 | 百度联网搜索 |
| **内容读取** | 7571060527728689152 | `LinkReader` | 7571060688051765248 | 读取 URL 内容 |
| **scrape网页抓取** | 7574332670541299712 | `Scrape` | 7574332892591947776 | 抓取网页内容 |
| **时间类工具包** | 7615195917427146752 | `get_current_time` | 7615196041205252096 | 获取当前时间 |
| **get_time** | 7582200654681079808 | `timevar` | 7582200654702051328 | 时间变量 |
| **天眼查** | 7574339980458196992 | `search` | 7574341193824206848 | 搜索企业 |
| **天眼查** | 7574339980458196992 | `company_detail` | 7574340684258213888 | 企业详情 |
| **天眼查** | 7574339980458196992 | `news` | 7574341674122346496 | 企业新闻 |
| **天眼查** | 7574339980458196992 | `change_log` | 7574340065812283392 | 企业变更记录 |
| **天眼查** | 7574339980458196992 | `abnormal_operation` | 7574342457173737472 | 经营异常 |
| **ChatPPT** | 7574335254391947264 | `ChatPPT` | 7574335388232187904 | 生成 PPT |
| **图表大师** | 7579108916546502656 | `any_charts` | 7579108916571668480 | 通用图表 |
| **图表大师** | 7579108916546502656 | `bar_charts` | 7579108916571684864 | 柱状图 |
| **图表大师** | 7579108916546502656 | `line_charts` | 7579108916575862784 | 折线图 |
| **图表大师** | 7579108916546502656 | `pie_charts` | 7579108916575879168 | 饼图 |
| **图表大师** | 7579108916546502656 | `radar_charts` | 7579193859146514432 | 雷达图 |
| **飞书消息** | 15 | `send_webhook_message` | 150004 | 发送飞书 Webhook |
| **飞书电子表格** | 17 | `add_cols` | 170001 | 新增列 |
| **飞书电子表格** | 17 | `add_rows` | 170002 | 新增行 |
| **飞书电子表格** | 17 | `create_spreadsheet` | 170003 | 创建电子表格 |
| **飞书电子表格** | 17 | `read_table` | 170010 | 读取行列数据 |
| **飞书电子表格** | 17 | `read_rows` | 170009 | 读取行 |
| **飞书电子表格** | 17 | `search_spreadsheet` | 170011 | 搜索表格 |
| **飞书多维表格** | 16 | `add_records` | 160002 | 新增记录 |
| **飞书多维表格** | 16 | `search_record` | 160012 | 查询记录 |
| **飞书多维表格** | 16 | `update_records` | 160014 | 更新记录 |
| **飞书多维表格** | 16 | `create_base` | 160003 | 创建多维表格 |
| **飞书多维表格** | 16 | `create_table` | 160004 | 创建数据表 |
| **飞书多维表格** | 16 | `list_tables` | 160010 | 列出数据表 |
| **飞书知识库** | 20 | `search_wiki` | 200001 | 搜索Wiki |
| **飞书任务** | 18 | `create_task` | 180001 | 创建任务 |
| **飞书任务** | 18 | `list_tasks` | 180003 | 列取任务 |
| **飞书云文档** | 19 | `create_document` | 190001 | 创建文档 |
| **飞书云文档** | 19 | `get_document_content` | 190002 | 获取文档内容 |
| **飞书云文档** | 19 | `write_document` | 190007 | 写入文档 |
| **飞书云文档** | 19 | `search_document` | 190005 | 搜索文档 |
| **飞书日历** | 21 | `create_event` | 210001 | 创建日程 |
| **飞书日历** | 21 | `list_events` | 210004 | 获取日程列表 |
| **飞书日历** | 21 | `search_events` | 210005 | 搜索日程 |
| **飞书认证** | 14 | `get_tenant_access_token` | 140001 | 获取凭证 |

#### 插件场景选型

| 场景 | 推荐插件 |
|------|---------|
| 需要实时信息/新闻 | `web_search`(博查) 或 `baidu_web_search`(百度) |
| 读取指定 URL | `LinkReader` 或 `Scrape` |
| 获取当前时间 | `get_current_time` 或 `timevar` |
| 企业信息查询 | 天眼查系列（`search` → `company_detail` → `news`） |
| 生成图表 | 图表大师（`any_charts` 通用，或指定 `bar_charts`/`line_charts`/`pie_charts`/`radar_charts`） |
| 生成 PPT | `ChatPPT` |
| 通知 | `send_webhook_message`(飞书) |

### JSON 多输出变量（核心设计模式）

**当 responseFormat=2（JSON）时，可以配置多个输出变量，平台会自动将 JSON 响应的各字段映射到对应的输出变量上。**

```json
"outputs": [
  { "type": "boolean", "name": "is_sensitive" },
  { "type": "string", "name": "risk_level" },
  { "type": "integer", "name": "confidence" },
  { "type": "string", "name": "analysis" },
  { "type": "string", "name": "reasoning_content" }
]
```

- `reasoning_content` 始终保留
- 其他输出变量名必须与 Prompt 中指定的 JSON 字段名完全一致
- Prompt 末尾必须包含 `# Output Format (JSON Only)` 段落

### LLM 节点 processType=2 完整示例

```json
{
  "inputs": {
    "settingOnError": {
      "processType": 2,
      "switch": true,
      "timeoutMs": 300000,
      "retryTimes": 1,
      "dataOnErr": "{\n    \"is_sensitive\": false,\n    \"risk_level\": \"\",\n    \"confidence\": 0,\n    \"analysis\": \"\",\n    \"reasoning_content\": \"\"\n}"
    }
  },
  "outputs": [
    { "type": "boolean", "name": "is_sensitive" },
    { "type": "string", "name": "risk_level" },
    { "type": "integer", "name": "confidence" },
    { "type": "string", "name": "analysis" },
    { "type": "string", "name": "reasoning_content" },
    {
      "type": "object",
      "name": "errorBody",
      "schema": [
        { "type": "string", "name": "errorMessage", "readonly": true },
        { "type": "string", "name": "errorCode", "readonly": true }
      ],
      "readonly": true
    },
    { "type": "boolean", "name": "isSuccess", "readonly": true }
  ],
  "ext": {
    "backupLLmParam": "{\"temperature\":1,\"maxTokens\":65536,\"topP\":0.95,\"responseFormat\":2,\"thinking\":0,\"modleName\":\"GLM-5.1\",\"modelType\":80014,\"generationDiversity\":\"default_val\"}"
  }
}
```

- 当 `retryTimes >= 1` 时，**必须**配置 `ext.backupLLmParam`（JSON 字符串，包含重试模型参数）
- `backupLLmParam` 内部的模型名称字段同样是 **`modleName`**（不是 `modelName`）
- `dataOnErr` 必须覆盖所有业务输出变量（含 `reasoning_content`）
- `errorBody` 需声明 `schema` 子字段（`errorMessage` + `errorCode`）

---

## 插件调用

type=4, 调用已发布插件 API。插件既可以作为**独立节点**使用，也可以挂载到 **LLM 节点的技能(fcParam)**中。

### 🔴 spaceId 必填提醒

> **插件节点(type=4)必须包含 `spaceId` 字段**（位于节点顶层），否则粘贴到画布后运行会报权限错误。spaceId 来自用户的工作空间，**必须在 Phase 1 向用户索要**。用户可直接粘贴原力平台工作空间的 URL，从中提取 `space/` 后的数字串即为 spaceId。
>
> ```json
> {
>   "id": "{{NODE_ID}}",
>   "type": "4",
>   "spaceId": "{{SPACE_ID}}",   // ← 必填！向用户索要
>   ...
> }
> ```

> 📖 **完整插件目录见 `references/plugin-catalog.md`**，包含 29 个可用插件的 pluginID/apiID、输入输出参数、apiParam 配置片段、插件选型决策树等。

```json
{
  "id": "{{NODE_ID}}",
  "type": "4",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "{{PLUGIN_TITLE}}",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Plugin-v2.jpg",
      "subtitle": "{{PLUGIN_NAME}}:{{API_NAME}}",
      "description": "{{PLUGIN_DESCRIPTION}}"
    },
    "inputs": {
      "apiParam": [
        { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "{{API_ID}}", "rawMeta": { "type": 1 } } } },
        { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "{{API_NAME}}", "rawMeta": { "type": 1 } } } },
        { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "{{PLUGIN_ID}}", "rawMeta": { "type": 1 } } } },
        { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "{{PLUGIN_NAME}}", "rawMeta": { "type": 1 } } } },
        { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
        { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
        { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
      ],
      "inputParameters": [],
      "settingOnError": { "processType": 1, "timeoutMs": 180000, "retryTimes": 0 }
    },
    "outputs": []
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 137.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Plugin-v2.jpg",
      "description": "{{PLUGIN_DESCRIPTION}}",
      "title": "插件",
      "mainColor": "#CA61FF"
    }
  }
}
```

### 已知插件速查表（完整列表见 plugin-catalog.md）

| 类别 | 插件名 | pluginID | apiID | title | 用途 |
|------|--------|----------|-------|-------|------|
| 搜索 | 博查搜索 | `7573626799205122048` | `7628887759360360448` | web_search | 全网搜索 |
| 搜索 | 百度智能搜索(AI生成) | `23` | `230002` | baidu_ai_search_chat | AI搜索+总结 |
| 搜索 | 百度智能搜索(网页) | `23` | `230001` | baidu_web_search | 网页搜索 |
| 搜索 | 百度智能搜索(媒体热榜) | `23` | `230004` | baidu_medium_trending | 热榜查询 |
| 搜索 | 百度智能搜索(垂类热榜) | `23` | `230003` | baidu_vertical_trending | 垂类热榜 |
| 搜索 | 搜狐热闻 | `6` | `60001` | top_news | 每日热闻 |
| 内容 | 内容读取 | `7571060527728689152` | `7571060688051765248` | LinkReader | 网页/文档内容 |
| 内容 | scrape网页抓取 | `7574332670541299712` | `7574332892591947776` | Scrape | 网页抓取(含视频) |
| 声量 | 品牌社媒声量查询 | `7574343510795485184` | `7574343814039470080` | queryPayCozeData | 品牌声量趋势 |
| OCR | 身份证OCR | `7623329737498165248` | `7623329907291979776` | idcardOcr | 身份证识别 |
| OCR | 完税证明OCR | `7618108655488991232` | `7618109840727998464` | taxCertificateOcr | 完税证明识别 |
| OCR | 学历学位证书OCR | `7618104615392772096` | `7618104758322069504` | degreeOcr | 学历学位识别 |
| OCR | 芝麻分OCR | `7618061944372592640` | `7618062010151862272` | zmscoreOcr | 芝麻分识别 |
| OCR | 微信分OCR | `7618058253791920128` | `7618058405197905920` | wechatScoreOcr | 微信分识别 |
| OCR | 竞品offer OCR | `7618052370265538560` | `7618052440264278016` | competingOfferOcr | 竞品offer(含篡改检测) |
| OCR | 个税OCR | `7618046187114856448` | `7618107264729088000` | incomeTaxOcr | 个税识别 |
| OCR | 发票OCR | `7617781476133699584` | `7617781625987792896` | invoiceOcr | 发票识别 |
| 语音 | TTS | `7613690331657142272` | `7613690491376238592` | tts | 文本→语音 |
| 语音 | ASR | `7576911113934077952` | `7576911152265822208` | ASR | 语音→文字 |
| 语音 | AED | `7615143939246391296` | `7615144026299170816` | AED | 声学事件识别 |
| 语音 | speech_meeting | `7615588752462708736` | `7615589030188548096` | speech_meeting | 会议纪要 |
| 语音 | 语音播客 | `7574334109489561600` | `7574334202070433792` | genPodcastURL | 生成播客音频 |
| 时间 | 时间类工具包 | `7615195917427146752` | `7615196041205252096` | get_current_time | 获取当前时间 |
| 时间 | get_time | `7582200654681079808` | `7582200654702051328` | timevar | 日期变量计算 |
| 创作 | Doubao图像生成 | `7574338924361809920` | `7574339044948049920` | gen_image | AI生成图片 |
| 创作 | ChatPPT | `7574335254391947264` | `7574335388232187904` | ChatPPT | 一句话生成PPT |
| 数据 | mysql_reader | `7584044147057623040` | `7584044379061354496` | mysql_reader | MySQL查询 |
| 数据 | 鸿鹄插件 | `7584382198875160576` | `7584382223629942784` | doris_query | Doris查询 |
| 代码 | SpecCoder | `7571072544216711168` | `7571072544229294080` | analyze_code | 代码分析问答 |
| 飞书 | 飞书电子表格 | `17` | `170001` | add_cols | 新增列 |
| 飞书 | 飞书电子表格 | `17` | `170002` | add_rows | 新增行 |
| 飞书 | 飞书电子表格 | `17` | `170003` | create_spreadsheet | 创建表格 |
| 飞书 | 飞书电子表格 | `17` | `170006` | get_spreadsheet | 获取表格信息 |
| 飞书 | 飞书电子表格 | `17` | `170009` | read_rows | 读取行 |
| 飞书 | 飞书电子表格 | `17` | `170010` | read_table | 读取行列数据 |
| 飞书 | 飞书电子表格 | `17` | `170011` | search_spreadsheet | 搜索表格 |
| 飞书 | 飞书多维表格 | `16` | `160002` | add_records | 新增记录 |
| 飞书 | 飞书多维表格 | `16` | `160003` | create_base | 创建多维表格 |
| 飞书 | 飞书多维表格 | `16` | `160004` | create_table | 创建数据表 |
| 飞书 | 飞书多维表格 | `16` | `160006` | delete_records | 删除记录 |
| 飞书 | 飞书多维表格 | `16` | `160010` | list_tables | 列出数据表 |
| 飞书 | 飞书多维表格 | `16` | `160012` | search_record | 查询记录 |
| 飞书 | 飞书多维表格 | `16` | `160014` | update_records | 更新记录 |
| 飞书 | 飞书知识库 | `20` | `200001` | search_wiki | 搜索Wiki |
| 飞书 | 飞书消息 | `15` | `150001` | get_chat_messages | 获取群聊/单聊历史 |
| 飞书 | 飞书消息 | `15` | `15002` | get_thread_messages | 获取话题历史 |
| 飞书 | 飞书消息 | `15` | `150003` | send_bot_message | 机器人发消息 |
| 飞书 | 飞书任务 | `18` | `180001` | create_task | 创建任务 |
| 飞书 | 飞书任务 | `18` | `180002` | delete_task | 删除任务 |
| 飞书 | 飞书任务 | `18` | `180003` | list_tasks | 列取任务 |
| 飞书 | 飞书任务 | `18` | `180004` | update_task | 更新任务 |
| 飞书 | 飞书云文档 | `19` | `190001` | create_document | 创建文档 |
| 飞书 | 飞书云文档 | `19` | `190002` | get_document_content | 获取文档内容 |
| 飞书 | 飞书云文档 | `19` | `190005` | search_document | 搜索文档 |
| 飞书 | 飞书云文档 | `19` | `190007` | write_document | 写入文档 |
| 飞书 | 飞书云文档 | `19` | `190008` | download_media | 下载素材 |
| 飞书 | 飞书云文档 | `19` | `190009` | upload_media | 上传素材 |
| 飞书 | 飞书日历 | `21` | `210001` | create_event | 创建日程 |
| 飞书 | 飞书日历 | `21` | `210004` | list_events | 获取日程列表 |
| 飞书 | 飞书日历 | `21` | `210005` | search_events | 搜索日程 |
| 飞书 | 飞书日历 | `21` | `210006` | update_event | 更新日程 |
| 飞书 | 飞书认证 | `14` | `140001` | get_tenant_access_token | 获取凭证 |

### 时间类工具包完整模板（获取当前时间必须用此插件）

**需要获取当前时间时必须用此插件，不要让 LLM 自行输出时间。**

```json
{
  "id": "{{NODE_ID}}",
  "type": "4",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "get_current_time",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Plugin-v2.jpg",
      "subtitle": "时间类工具包:get_current_time",
      "description": "获取当前时间"
    },
    "inputs": {
      "apiParam": [
        { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7615196041205252096", "rawMeta": { "type": 1 } } } },
        { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "时间类工具包", "rawMeta": { "type": 1 } } } },
        { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7615195917427146752", "rawMeta": { "type": 1 } } } },
        { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "时间类工具包", "rawMeta": { "type": 1 } } } },
        { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
        { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
        { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
      ],
      "inputParameters": [],
      "settingOnError": { "processType": 1, "timeoutMs": 180000, "retryTimes": 0 }
    },
    "outputs": [
      { "type": "integer", "name": "code", "description": "返回码，0：正常，其他：异常" },
      { "type": "string", "name": "message", "description": "格式化后的当前时间" }
    ]
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 137.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Plugin-v2.jpg",
      "apiName": "时间类工具包",
      "pluginID": "7615195917427146752",
      "pluginProductStatus": 0,
      "pluginProductUnlistType": 0,
      "pluginType": 1,
      "spaceID": "{{SPACE_ID}}",
      "inputs": [
        { "name": "format", "type": "string", "description": "时间格式，默认yyyy-MM-dd HH:mm:ss" },
        { "name": "timeZone", "type": "string", "description": "时区，默认UTC+8" }
      ],
      "outputs": [
        { "name": "code", "type": "integer", "description": "返回码，0：正常，其他：异常" },
        { "name": "message", "type": "string", "description": "格式化后的当前时间" }
      ],
      "updateTime": 0,
      "versionName": "v1.0.1",
      "description": "提供获取当前时间等各种时间相关的工具",
      "title": "时间类工具包",
      "mainColor": "#CA61FF"
    }
  }
}
```

### 插件选型建议（完整决策树见 plugin-catalog.md）

| 需求场景 | 推荐插件 | 说明 |
|---------|---------|------|
| 全网搜索 | 博查搜索 / 百度智能搜索 | 博查搜索更简洁；百度支持AI总结/深度搜索 |
| 热榜/趋势 | 百度智能搜索(媒体热榜/垂类热榜) | 按平台或垂类查热榜 |
| 每日新闻 | 搜狐热闻 | 获取搜狐热闻 |
| 获取网页/文档内容 | 内容读取(LinkReader) | 支持网页、PDF、DOCX、XLSX、CSV、TXT |
| 抓取网页（含视频） | scrape网页抓取 | 支持视频平台解析 |
| 获取当前时间 | 时间类工具包 | 支持自定义格式和时区 |
| 日期计算(T-N等) | get_time | 日期变量计算 |
| 身份证识别 | 身份证OCR | 正反面识别+风险检测 |
| 发票识别 | 发票OCR | 提取发票全部字段 |
| 个税/完税证明 | 个税OCR / 完税证明OCR | 税务相关文档识别 |
| 学历学位证书 | 学历学位证书OCR | 含PS检测 |
| 芝麻分/微信分 | 芝麻分OCR / 微信分OCR | 信用分截图识别 |
| 竞品offer | 竞品offer OCR | 额度/利率识别+篡改检测 |
| 文字→语音 | TTS | 返回音频URL |
| 语音→文字 | ASR | 支持mp3/m4a/wav/pcm/ogg |
| 会议纪要 | speech_meeting | 多说话人日志识别 |
| 生成播客 | 语音播客 | 文本→双人播客音频 |
| 声学事件识别 | AED | 铃声类型等 |
| 生成图片 | Doubao图像生成 | AI文生图 |
| 生成 PPT | ChatPPT | 一句话生成完整 PPT |
| MySQL查询 | mysql_reader | 单次最多10000条 |
| Doris查询 | 鸿鹄插件 | Doris集群SQL |
| 品牌声量分析 | 品牌社媒声量查询 | 近30天社媒声量 |
| 代码分析 | SpecCoder | 代码库问答，支持多轮 |
| 飞书电子表格-创建 | 飞书电子表格:create_spreadsheet | 创建新的电子表格 |
| 飞书电子表格-读取 | 飞书电子表格:read_table / read_rows / read_cols | 读取表格数据 |
| 飞书电子表格-写入 | 飞书电子表格:add_rows / add_cols | 新增行列数据 |
| 飞书电子表格-删除 | 飞书电子表格:delete_rows / delete_cols | 删除行列 |
| 飞书电子表格-搜索 | 飞书电子表格:search_spreadsheet | 搜索电子表格文档 |
| 飞书多维表格-创建 | 飞书多维表格:create_base / create_table | 创建多维表格/数据表 |
| 飞书多维表格-查询 | 飞书多维表格:search_record | 查询记录(单次最多500条) |
| 飞书多维表格-写入 | 飞书多维表格:add_records | 新增记录(单次最多500条) |
| 飞书多维表格-更新 | 飞书多维表格:update_records | 批量更新(单次最多500条) |
| 飞书多维表格-删除 | 飞书多维表格:delete_records / delete_tables | 删除记录或数据表 |
| 飞书多维表格-字段 | 飞书多维表格:add_field / update_field / delete_field / list_fields | 字段管理(增删改查) |
| 飞书知识库搜索 | 飞书知识库:search_wiki | 搜索Wiki文档列表 |
| 飞书发消息(Webhook) | 飞书消息:send_webhook_message | 自定义机器人Webhook发送 |
| 飞书发消息(机器人) | 飞书消息:send_bot_message | 应用机器人发消息，需tenant_access_token |
| 飞书消息历史 | 飞书消息:get_chat_messages / get_thread_messages | 获取群聊/话题消息历史 |
| 飞书任务管理 | 飞书任务:create/update/delete/list_tasks | 创建/更新/删除/列取任务 |
| 飞书创建/写入文档 | 飞书云文档:create_document / write_document | 支持markdown格式 |
| 飞书读取文档 | 飞书云文档:get_document_content | 返回markdown或纯文本 |
| 飞书搜索文档/PPT | 飞书云文档:search_document / search_slides | 关键字搜索 |
| 飞书素材上传下载 | 飞书云文档:upload_media / download_media | 上传返回file_token |
| 飞书日程管理 | 飞书日历:create/update/delete_event | 创建/更新/删除日程 |
| 飞书查询日程 | 飞书日历:list_events / search_events | 列表/关键字搜索 |
| 飞书获取凭证 | 飞书认证及授权:get_tenant_access_token | 获取tenant_access_token，2h有效期 |

---

## 代码

type=5, 编写 Python 代码处理输入变量来生成返回值。

```json
{
  "id": "{{NODE_ID}}",
  "type": "5",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "{{CODE_TITLE}}",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Code-v2.jpg",
      "description": "通过编写代码处理输入变量来生成返回值",
      "mainColor": "#00B2B2",
      "subTitle": "代码"
    },
    "inputs": {
      "inputParameters": [
        {
          "name": "{{INPUT_VAR}}",
          "input": {
            "type": "string",
            "value": {
              "type": "ref",
              "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{SOURCE_OUTPUT_NAME}}" },
              "rawMeta": { "type": 1 }
            }
          }
        }
      ],
      "language": 3,
      "code": "async def main(args: Args) -> Output:\n    params = args.params\n    # your code here\n    ret = {\"result\": params[\"{{INPUT_VAR}}\"]}\n    return ret\n",
      "settingOnError": { "processType": 1, "timeoutMs": 60000, "retryTimes": 0 }
    },
    "outputs": [
      { "type": "string", "name": "result" }
    ]
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 113.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Code-v2.jpg",
      "description": "通过编写代码处理输入变量来生成返回值",
      "title": "代码",
      "mainColor": "#00B2B2"
    }
  }
}
```

### 关键规则

1. **`language` 必须为 `3`**（Python），不能写 `"codeLanguage": "python3"`
2. **网络库可用但推荐用 HTTP 节点**：代码节点实际可 import requests/aiohttp/httpx 等网络库，但**建议仍优先使用 HTTP 请求节点(type=45)**，因为 HTTP 节点支持 GUI 配置鉴权、重试、超时等，更易维护
3. 可用标准库：json、re、math、datetime、hashlib、base64、random、collections、requests、aiohttp、httpx 等
4. 代码函数签名：`async def main(args: Args) -> Output:`
5. 通过 `args.params["变量名"]` 获取输入参数

---

## 知识库检索

type=6, 在选定的知识库中根据输入变量召回匹配信息。

> ⚠️ **inputParameters 参数名固定为 `"Query"`（大写 Q）**，不能用 `"query"` / `"search_query"` 等自定义名称，这是平台硬编码的。
> ⚠️ **outputs 固定为 `outputList: list[object]`**，schema 固定为 `[{output: string}, {documentId: string}]`，不可自定义、不可修改。
> ⚠️ **datasetParam 中的 topK/useRerank/useRewrite/isPersonalOnly 不要预设 content 值**（如 `"content":"5"`），由用户在 GUI 中配置。

```json
{
  "id": "{{NODE_ID}}",
  "type": "6",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "知识库检索",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-KnowledgeQuery-v2.jpg",
      "description": "在选定的知识中,根据输入变量召回最匹配的信息,并以列表形式返回",
      "mainColor": "#FF811A",
      "subTitle": "知识库检索"
    },
    "outputs": [
      { "type": "list", "name": "outputList", "schema": { "type": "object", "schema": [{ "type": "string", "name": "output" }, { "type": "string", "name": "documentId" }] } }
    ],
    "inputs": {
      "datasetParam": [
        { "name": "datasetList", "input": { "type": "list", "schema": { "type": "string" }, "value": { "type": "literal", "content": [] } } },
        { "name": "topK", "input": { "type": "integer", "value": { "type": "literal" } } },
        { "name": "useRerank", "input": { "type": "boolean", "value": { "type": "literal", "rawMeta": { "type": 3 } } } },
        { "name": "useRewrite", "input": { "type": "boolean", "value": { "type": "literal", "rawMeta": { "type": 3 } } } },
        { "name": "isPersonalOnly", "input": { "type": "boolean", "value": { "type": "literal", "rawMeta": { "type": 3 } } } }
      ],
      "inputParameters": [
        {
          "name": "Query",
          "input": {
            "type": "string",
            "value": {
              "type": "ref",
              "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{SOURCE_OUTPUT_NAME}}" },
              "rawMeta": { "type": 1 }
            }
          }
        }
      ]
    }
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 139.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-KnowledgeQuery-v2.jpg",
      "description": "在选定的知识中,根据输入变量召回最匹配的信息",
      "title": "知识库检索",
      "mainColor": "#FF811A"
    }
  }
}
```

注意：`datasetList` 生成时写空数组 `[]`，用户粘贴后在 GUI 中手动选择知识库。若预填了不存在的知识库 ID，粘贴时节点可能被丢弃。

### 检索策略 strategy 字段

| strategy 值 | 检索模式 | 说明 |
|:---:|:---|:---|
| **0** | 语义检索 | 基于向量相似度 |
| **1** | 混合检索 | 语义+全文结合（推荐） |
| **20** | 全文检索 | 基于关键词匹配 |

### 其他可配置字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `topK` | integer | 召回数量，默认 5 |
| `minScore` | float | 最低相似度分数，默认 0.5 |
| `useRerank` | boolean | 是否启用重排序 |
| `useRewrite` | boolean | 是否启用查询改写 |
| `isPersonalOnly` | boolean | 是否仅检索个人知识库 |
| `strategy` | integer | 检索策略：0/1/20 |

---

## 选择器

type=8, 条件分支 if/else 判断。支持多分支，每个分支可配置多个条件组合。

### 核心结构说明

#### left 和 right 结构对称

`left` 和 `right` 的 JSON 结构**完全相同**，都有 `{"input":{...}}` 包装层：

```json
{
  "left": {
    "input": {
      "type": "string",
      "value": {
        "type": "ref",
        "content": { "source": "block-output", "blockID": "601001", "name": "status" },
        "rawMeta": { "type": 1 }
      }
    }
  },
  "operator": 1,
  "right": {
    "input": {
      "type": "string",
      "value": {
        "type": "literal",
        "content": "success",
        "rawMeta": { "type": 1 }
      }
    }
  }
}
```

#### 操作符完整映射表

| operator | 含义 | 需要 right | 适用类型 |
|---------|------|-----------|---------|
| 1 | 等于 | ✅ | 所有 |
| 2 | 不等于 | ✅ | 所有 |
| 3 | 长度大于 | ✅ | string（right 为 integer） |
| 4 | 长度大于等于 | ✅ | string（right 为 integer） |
| 5 | 长度小于 | ✅ | string（right 为 integer） |
| 6 | 长度小于等于 | ✅ | string（right 为 integer） |
| 7 | 包含 | ✅ | string/object |
| 8 | 不包含 | ✅ | string/object |
| 9 | 为空 | ❌ | 所有（一元操作符） |
| 10 | 不为空 | ❌ | 所有（一元操作符） |
| 11 | 为true | ❌ | boolean（一元操作符） |
| 12 | 为false | ❌ | boolean（一元操作符） |
| 13 | 大于 | ✅ | integer/float |
| 14 | 大于等于 | ✅ | integer/float |
| 15 | 小于 | ✅ | integer/float |
| 16 | 小于等于 | ✅ | integer/float |

#### logic 字段

- `1` = OR（任一条件满足）
- `2` = AND（所有条件同时满足）

### 完整模板

> ⚠️ 选择器**始终使用 `branches` 数组**（无论单分支还是多分支）。

```json
{
  "id": "{{NODE_ID}}",
  "type": "8",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "{{SELECTOR_TITLE}}",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Condition-v2.jpg",
      "description": "连接多个下游分支，若设定的条件成立则仅运行对应的分支，若均不成立则只运行\"否则\"分支",
      "mainColor": "#00B2B2",
      "subTitle": "选择器"
    },
    "inputs": {
      "branches": [
        {
          "condition": {
            "logic": 2,
            "conditions": [
              {
                "operator": 1,
                "left": {
                  "input": {
                    "type": "string",
                    "value": {
                      "type": "ref",
                      "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{VAR_NAME}}" }
                    }
                  }
                },
                "right": {
                  "input": {
                    "type": "string",
                    "value": {
                      "type": "literal",
                      "content": "{{COMPARE_VALUE}}",
                      "rawMeta": { "type": 1 }
                    }
                  }
                }
              }
            ]
          }
        }
      ]
    },
    "outputs": []
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 139.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Condition-v2.jpg",
      "description": "连接多个下游分支，若设定的条件成立则仅运行对应的分支，若均不成立则只运行\"否则\"分支",
      "title": "选择器",
      "mainColor": "#00B2B2"
    }
  }
}
```

### 连线端口说明（⚠️ 关键纠正）

| 分支数 | sourcePortID | 说明 |
|--------|-------------|------|
| 单分支(1 branch) | `"true"` + `"false"` | 第一个分支 + 否则 |
| 双分支(2 branches) | `"true"` + `"true_1"` + `"false"` | 第一个 + 第二个 + 否则 |
| 三分支(3 branches) | `"true"` + `"true_1"` + `"true_2"` + `"false"` | 依此类推 |
| N分支 | `"true"`, `"true_1"` ... `"true_N-1"` + `"false"` | 第一个用 `"true"`，后续加下标 |

> ⚠️ **不是** `"branch-0"`, `"branch-1"` 等！第一个分支端口是 `"true"`，第二个是 `"true_1"`，第三个是 `"true_2"`...否则分支始终是 `"false"`。

### 多分支示例（2 个分支 + 否则）

```json
"inputs": {
  "branches": [
    {
      "condition": {
        "logic": 2,
        "conditions": [
          {
            "operator": 1,
            "left": { "input": { "type": "string", "value": { "type": "ref", "content": { "source": "global_variable_app", "path": ["API_KEY"], "blockID": "", "name": "" } } } },
            "right": { "input": { "type": "string", "value": { "type": "literal", "content": "1", "rawMeta": { "type": 1 } } } }
          }
        ]
      }
    },
    {
      "condition": {
        "logic": 2,
        "conditions": [
          {
            "operator": 1,
            "left": { "input": { "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "601001", "name": "key0" } } } },
            "right": { "input": { "type": "string", "value": { "type": "literal", "content": "1", "rawMeta": { "type": 1 } } } }
          }
        ]
      }
    }
  ]
}
```
对应连线：
```json
{ "sourceNodeID": "选择器ID", "targetNodeID": "A", "sourcePortID": "true" }
{ "sourceNodeID": "选择器ID", "targetNodeID": "B", "sourcePortID": "true_1" }
{ "sourceNodeID": "选择器ID", "targetNodeID": "C", "sourcePortID": "false" }
```

### 一元操作符示例（无 right 字段）

```json
{
  "left": {
    "input": {
      "type": "boolean",
      "value": {
        "type": "ref",
        "content": { "source": "block-output", "blockID": "601005", "name": "is_valid" },
        "rawMeta": { "type": 3 }
      }
    }
  },
  "operator": 11
}
```

### 数值比较示例

```json
{
  "left": {
    "input": {
      "type": "integer",
      "value": {
        "type": "ref",
        "content": { "source": "block-output", "blockID": "601003", "name": "score" },
        "rawMeta": { "type": 2 }
      }
    }
  },
  "operator": 14,
  "right": {
    "input": {
      "type": "integer",
      "value": {
        "type": "literal",
        "content": 60,
        "rawMeta": { "type": 2 }
      }
    }
  }
}
```

---

## 工作流调用

type=9, 调用另一个已发布的子工作流。

```json
{
  "id": "{{NODE_ID}}",
  "type": "9",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "{{WORKFLOW_NAME}}",
      "description": "{{WORKFLOW_DESCRIPTION}}",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Workflow-v2.jpg",
      "isImageflow": false
    },
    "inputs": {
      "workflowId": "{{TARGET_WORKFLOW_ID}}",
      "spaceId": "{{SPACE_ID}}",
      "workflowVersion": "",
      "inputDefs": [],
      "type": 0,
      "inputParameters": [],
      "settingOnError": {}
    },
    "outputs": []
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 113.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Workflow-v2.jpg",
      "description": "{{WORKFLOW_DESCRIPTION}}",
      "title": "工作流调用",
      "mainColor": "#00B83E"
    }
  }
}
```

注意：`workflowId` 和 `spaceId` 为平台资源 ID，需要用户提供。`spaceId` 与顶层 `source.spaceId` 一致。

---

## SQL自定义

type=12, 自定义 SQL 语句增删改查。适用于多表 JOIN、子查询、聚合统计等复杂 SQL 场景。简单的 CRUD 操作应优先使用对应的图形化节点(43/46/42/44)。

### 核心规则

1. **SQL 中的变量插值 `{{变量名}}` 只能引用 `inputParameters` 中声明的变量名**，不能直接引用上游 blockID
2. 需要引用上游输出时，先在 `inputParameters` 中声明变量并用 ref 引用上游节点，再在 SQL 中用 `{{变量名}}` 引用
3. `databaseInfoList` 若用户提供了表ID则填 `[{"databaseInfoID": "表ID"}]`，否则写空数组 `[]`（详见上方 🔴 格式说明）
4. 默认输出 `outputList`(list) 和 `rowNum`(integer)。**注意**：SQL 自定义(12)和图形化查询数据(43)的 `rowNum` 均不可用（始终为 null），判断是否有数据应**用选择器(8)直接判断 `outputList` 不为空(operator=10)**。而图形化的更新(42)/新增(46)/删除(44)节点的 `rowNum` 正常返回影响行数，可直接用于分支判断

### 完整模板

```json
{
  "id": "{{NODE_ID}}",
  "type": "12",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "SQL自定义",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Database-v2.jpg",
      "description": "基于用户自定义的 SQL 完成对数据库的增删改查操作",
      "mainColor": "#FF811A",
      "subTitle": "SQL自定义"
    },
    "inputs": {
      "inputParameters": [
        {
          "name": "domain_value",
          "input": {
            "type": "string",
            "value": {
              "type": "ref",
              "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "domain_value" },
              "rawMeta": { "type": 1 }
            }
          }
        }
      ],
      "databaseInfoList": [{ "databaseInfoID": "{{TABLE_ID}}" }],
      "sql": "SELECT * FROM domain_whitelist WHERE domain = '{{domain_value}}' LIMIT 1"
    },
    "outputs": [
      { "type": "list", "name": "outputList", "schema": { "type": "object", "schema": [] } },
      { "type": "integer", "name": "rowNum" }
    ]
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 142.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Database-v2.jpg",
      "description": "基于用户自定义的 SQL 完成对数据库的增删改查操作",
      "title": "SQL自定义",
      "mainColor": "#FF811A"
    }
  }
}
```

### SQL 变量引用对比

```
❌ 错误：SQL 中直接引用上游 blockID
"sql": "SELECT * FROM users WHERE name = '{{block_output_601001.name}}'"

✅ 正确：先在 inputParameters 中声明变量引用上游，SQL 中用变量名
"inputParameters": [
  { "name": "user_name", "input": { "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "601001", "name": "name" }, "rawMeta": { "type": 1 } } } }
],
"sql": "SELECT * FROM users WHERE name = '{{user_name}}'"
```

### SQL INSERT 示例

INSERT 语句必须显式包含 `uuid` 列：

```
✅ "sql": "INSERT INTO my_table (uuid, domain, status) VALUES (UUID(), '{{domain_value}}', 1)"

❌ "sql": "INSERT INTO my_table (domain, status) VALUES ('{{domain_value}}', 1)"
   → 报错: expected N+1 arguments, got N
```

---

## 输出（已废弃 ⚠️）

type=13, 消息输出节点。**此节点已废弃，不要在生成的工作流中使用！**

---

## 文本处理

type=15, 字符串拼接/分割处理。

```json
{
  "id": "{{NODE_ID}}",
  "type": "15",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "{{TEXT_TITLE}}",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-TextProcessing-v2.jpg",
      "description": "用于对文本信息的处理，包括文本拼接和文本分割",
      "mainColor": "#3071F2",
      "subTitle": "文本处理"
    },
    "inputs": {
      "inputParameters": [],
      "textParam": {
        "type": "combine",
        "combineContent": [
          { "type": "literal", "content": "前缀文本：" },
          { "type": "ref", "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{VAR_NAME}}" } }
        ]
      }
    },
    "outputs": [
      { "type": "string", "name": "output" }
    ]
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 113.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-TextProcessing-v2.jpg",
      "description": "用于对文本信息的处理",
      "title": "文本处理",
      "mainColor": "#3071F2"
    }
  }
}
```

---

## 问答

type=18, 中间过程向用户提问。

> ⚠️ **问答节点仅在 Agent 模式中可用，工作流模式不可使用此节点！** 如需在工作流中收集信息，请使用"输入"节点(type=30)。

```json
{
  "id": "{{NODE_ID}}",
  "type": "18",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "{{QA_TITLE}}",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-QA-v2.jpg",
      "description": "用于在流程中间通过直接回答/选择回答两种方式收集更多用户信息",
      "mainColor": "#3071F2",
      "subTitle": "问答"
    },
    "inputs": {
      "inputParameters": [],
      "qaParam": {
        "type": "direct",
        "content": { "type": "literal", "content": "请输入您的问题" }
      }
    },
    "outputs": [
      { "type": "string", "name": "output" }
    ]
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 165.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-QA-v2.jpg",
      "description": "用于在流程中间收集更多用户信息",
      "title": "问答",
      "mainColor": "#3071F2"
    }
  }
}
```

---

## 循环（容器节点）

type=21, 循环执行任务。**这是一个容器节点**，内部嵌套子节点(blocks)和子连线(edges)。工作流中如需重复执行逻辑，**必须**使用此节点或批处理(type=28)，**禁止**用 edge 回连形成循环。

### 循环三种模式

| loopType | 模式 | inputParameters | 说明 |
|----------|------|----------------|------|
| `"array"` | 数组循环 | ✅ 必须有 `input`(list) | 遍历数组，内部可用 item/index |
| `"count"` | 指定次数 | ❌ 不需要 | 按 loopCount 次数循环，自动提供 `index` 变量（无需在 variableParameters 声明） |
| `"infinite"` | 无限循环 | ❌ 不需要 | **必须**在内部放"终止循环"(type=19)节点退出 |

#### count 模式内置变量 `index`

count 模式自动提供迭代索引变量 `index`（从 0 开始），**无需在 variableParameters 中声明**。内部节点引用方式：
```json
{ "type": "ref", "content": { "source": "block-output", "blockID": "{{循环容器ID}}", "name": "index" }, "rawMeta": { "type": 2 } }
```

#### count 模式输出为 list

count 模式循环的 output 类型应声明为 `type="list"`，`schema.type` 匹配内部节点的输出元素类型。每轮迭代的输出会自动收集成列表。

### 基础结构

⚠️ **`blocks` 和 `edges` 必须在节点顶层**，与 `data`/`meta`/`_temp` 同级！放在 `data` 内部会导致内部节点不渲染！

```json
{
  "id": "{{LOOP_NODE_ID}}",
  "type": "21",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} },
    "canvasPosition": { "x": {{X}}, "y": {{Y_PLUS_200}} }
  },
  "data": {
    "nodeMeta": {
      "title": "{{LOOP_TITLE}}",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Loop-v2.jpg",
      "description": "用于通过设定循环次数和逻辑，重复执行一系列任务",
      "mainColor": "#00B2B2",
      "subTitle": "循环"
    },
    "inputs": {
      "loopType": "array",
      "loopCount": { "type": "integer", "value": { "type": "literal", "content": "10" } },
      "variableParameters": [
        {
          "name": "var_state",
          "input": {
            "type": "object",
            "schema": [{ "type": "string", "name": "key" }],
            "value": {
              "type": "ref",
              "content": { "source": "block-output", "blockID": "{{上游节点ID}}", "name": "{{上游变量名}}" },
              "rawMeta": { "type": 6 }
            }
          }
        }
      ],
      "inputParameters": [
        {
          "name": "input",
          "input": {
            "type": "list",
            "schema": { "type": "string" },
            "value": {
              "type": "ref",
              "content": { "source": "block-output", "blockID": "{{上游节点ID}}", "name": "{{上游输出变量名}}" },
              "rawMeta": { "type": 99 }
            }
          }
        }
      ]
    },
    "outputs": [
      {
        "name": "output",
        "input": {
          "type": "list",
          "schema": { "type": "string" },
          "value": {
            "type": "ref",
            "content": { "source": "block-output", "blockID": "{{最后一个内部节点ID}}", "name": "{{内部节点输出变量名}}" },
            "rawMeta": { "type": 1 }
          }
        }
      }
    ]
  },
  "blocks": [],
  "edges": [],
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 139.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Loop-v2.jpg",
      "description": "用于通过设定循环次数和逻辑，重复执行一系列任务",
      "title": "循环",
      "mainColor": "#00B2B2"
    }
  }
}
```

> ⚠️ **`schema.type` 必须与上游 list 输出的 `schema.type` 完全一致，且与代码实际返回的元素类型对应**（dict→object, str→string）。**必须**使用 `object` 直接传 dict（Object-First 原则），禁止不必要的 json.dumps/json.loads。
>
> ⚠️ **rawMeta.type 必须与 list 的元素类型匹配**：list[string]=**99**, list[integer]=100, list[boolean]=101, list[float]=102, list[object]=**103**。不要所有 list 都写 103！

### variableParameters（中间变量/跨迭代状态）

`variableParameters` 用于定义**跨迭代持久化**的变量。每轮迭代可通过"设置变量"(type=20)节点更新其值，下一轮自动获取更新后的值。

```json
"variableParameters": [
  {
    "name": "var_state",
    "input": {
      "type": "object",
      "schema": [{ "type": "string", "name": "key" }],
      "value": {
        "type": "ref",
        "content": { "source": "block-output", "blockID": "上游节点ID", "name": "state" },
        "rawMeta": { "type": 6 }
      }
    }
  }
]
```

**引用中间变量的格式**：`blockID` = 循环节点自身 ID，`name` = `"var_state.key"`（变量名.字段名）：
```json
{ "type": "ref", "content": { "source": "block-output", "blockID": "循环节点ID", "name": "var_state.key" }, "rawMeta": { "type": 1 } }
```

#### object 子字段 dot notation 引用规则

容器内部节点**可以**用 `变量名.子字段名` 引用 object 的子字段，但有**三个前提**：

1. **上游节点 outputs** 的 object/list[object] 必须有**显式 schema 声明所有子字段**（含 name 和 type）
2. **循环 variableParameters** 中的 schema 必须与上游**完全一致**（字段名、字段类型）
3. 子字段引用的 `input.type` 和 `rawMeta.type` 匹配的是**子字段的类型**，不是父对象的类型

```
× 错误: 上游输出是 string，却在 variableParameter 中强套 object schema → 子字段引用全部失败
✓ 正确: 上游输出本身就是 object 且声明了子字段 schema → dot notation 正常工作
```

**全链路 schema 一致性**：

```
上游 outputs.schema  ═══一致═══►  variableParameters.schema  ═══dot═══►  内部节点引用
```

三段 schema 声明必须完全一致。不能凭空给 string 类型源套 object schema。

### 循环内部专用节点（仅在循环体内可用）

| type | 名称 | 说明 | icon |
|------|------|------|------|
| **19** | 终止循环(Break) | 立即跳出循环体 | icon-Break-v2.jpg |
| **20** | 设置变量(Loop Set Variable) | 重置 variableParameters 的值供下一轮使用 | icon-LoopSetVariable-v2.jpg |
| **29** | 继续循环(Continue) | 跳过本轮后续，执行下一轮 | icon-Continue-v2.jpg |

```json
// 终止循环 (type=19)
{
  "id": "{{NODE_ID}}", "type": "19",
  "meta": { "position": { "x": {{X}}, "y": {{Y}} } },
  "data": {
    "nodeMeta": { "title": "终止循环", "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Break-v2.jpg", "description": "用于立即终止当前所在的循环，跳出循环体", "mainColor": "#00B2B2", "subTitle": "终止循环" }
  },
  "_temp": { "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 67.9 }, "externalData": { "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Break-v2.jpg", "description": "用于立即终止当前所在的循环，跳出循环体", "title": "终止循环", "mainColor": "#00B2B2" } }
}

// 设置变量 (type=20) — 用于更新 variableParameters
// ⚠️ 使用 left/right 赋值结构，不是 name/input 结构！
{
  "id": "{{NODE_ID}}", "type": "20",
  "meta": { "position": { "x": {{X}}, "y": {{Y}} } },
  "data": {
    "inputs": {
      "inputParameters": [
        {
          "left": {
            "type": "string",
            "value": {
              "type": "ref",
              "content": { "source": "block-output", "blockID": "{{循环容器ID}}", "name": "{{variableParameter变量名}}" },
              "rawMeta": { "type": 1 }
            }
          },
          "right": {
            "type": "string",
            "value": {
              "type": "ref",
              "content": { "source": "block-output", "blockID": "{{内部节点ID}}", "name": "{{内部节点输出变量名}}" },
              "rawMeta": { "type": 1 }
            }
          }
        }
      ]
    },
    "nodeMeta": { "title": "设置变量", "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-LoopSetVariable-v2.jpg", "description": "用于重置循环变量的值，使其下次循环使用重置后的值", "mainColor": "#00B2B2", "subTitle": "设置变量" }
  },
  "_temp": { "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 87.9 }, "externalData": { "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-LoopSetVariable-v2.jpg", "description": "用于重置循环变量的值，使其下次循环使用重置后的值", "title": "设置变量", "mainColor": "#00B2B2" } }
}

// ⚠️ 设置变量关键说明：
// - left → ref 到循环容器的 variableParameter（blockID=容器ID, name=变量名）
// - right → ref 到内部节点的输出（blockID=内部节点ID, name=输出变量名）
// - left/right 的 type 和 rawMeta.type 必须与目标变量类型一致
// - 如果是 object 类型：type="object", rawMeta.type=6
// - 可以有多个 left/right 对，分别赋值不同的 variableParameter

// 继续循环 (type=29) — 跳到下一轮迭代
{
  "id": "{{NODE_ID}}", "type": "29",
  "meta": { "position": { "x": {{X}}, "y": {{Y}} } },
  "data": {
    "nodeMeta": { "title": "继续循环", "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Continue-v2.jpg", "description": "用于终止当前循环，执行下次循环", "mainColor": "#00B2B2", "subTitle": "继续循环" }
  },
  "_temp": { "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 67.9 }, "externalData": { "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Continue-v2.jpg", "description": "用于终止当前循环，执行下次循环", "title": "继续循环", "mainColor": "#00B2B2" } }
}
```

### Object-First 完整示例（推荐模式）

**上游代码节点**：直接返回 list[dict]
```python
async def main(args: Args) -> Output:
    params = args.params
    names = params.get('names', [])
    items = []
    for name in names:
        items.append({'name': name, 'score': 0, 'status': 'pending'})  # ✅ 直接 append dict
    return {'items': items}
```
outputs 声明：`{"type": "list", "name": "items", "schema": {"type": "object", "schema": [{"type": "string", "name": "name"}, {"type": "integer", "name": "score"}, {"type": "string", "name": "status"}]}}`

> ⚠️ **必须在 schema 中列出全部子字段**（name + type），否则下游节点无法用 `items.name`、`items.score` 引用子字段。只写 `"schema": {"type": "object"}` 而不展开子字段是**常见错误**，会导致下游引用失败。

**循环/批处理输入**：schema 与上游一致（含子字段）
```json
"inputParameters": [{
  "name": "input",
  "input": {
    "type": "list",
    "schema": {"type": "object", "schema": [{"type": "string", "name": "name"}, {"type": "integer", "name": "score"}, {"type": "string", "name": "status"}]},
    "value": {"type": "ref", "content": {"source": "block-output", "blockID": "上游ID", "name": "items"}, "rawMeta": {"type": 103}}
  }
}]
```

**容器内部首个代码节点**：直接使用 dict，无需 json.loads
```python
async def main(args: Args) -> Output:
    params = args.params
    item = params.get('item_obj', {})
    if isinstance(item, str):  # 健壮性 fallback
        import json
        item = json.loads(item)
    name = item.get('name', '')
    return {'result': {'name': name, 'processed': True}}  # ✅ 返回 dict
```
input 声明：`"type": "object"`，output 声明：`{"type": "object", "name": "result", "schema": [{"type": "string", "name": "name"}, {"type": "boolean", "name": "processed"}]}`

> ⚠️ object 类型输出**必须**展开 schema 子字段，否则下游无法引用 `result.name`。

**容器输出**：schema 与内部最后节点一致（含子字段）
```json
"outputs": [{
  "name": "output",
  "input": {
    "type": "list",
    "schema": {"type": "object", "schema": [{"type": "string", "name": "name"}, {"type": "boolean", "name": "processed"}]},
    "value": {"type": "ref", "content": {"source": "block-output", "blockID": "内部最后节点ID", "name": "result"}, "rawMeta": {"type": 6}}
  }
}]
```

### 循环节点关键说明

1. **⚠️ `blocks`/`edges` 在节点顶层**：与 `data`/`meta`/`_temp` 同级，**不在** `data` 内部！
2. **循环(21)内部端口用 `loop-` 前缀**：入口 `sourcePortID = "loop-function-inline-output"`，出口 `targetPortID = "loop-function-inline-input"`
3. **循环(21)外部输出端口**：循环容器 → 下一个外部节点的连线用 `sourcePortID = "loop-output"`
4. **批处理(28)内部端口用 `batch-` 前缀**：入口 `sourcePortID = "batch-function-inline-output"`，出口 `targetPortID = "batch-function-inline-input"`
5. **批处理(28)外部输出端口**：批处理容器 → 下一个外部节点的连线用 `sourcePortID = "batch-output"`
6. **内部 item 类型是元素类型，不是 list**：输入 `list[object]` → 内部每次迭代收到 `object`，内部节点 inputParameters 声明 `"type": "object"`
7. **无限循环(infinite)必须有"终止循环"(type=19)节点**：否则永远不会退出

---

## 意图识别

type=22, 用 LLM 做用户意图分类。

> ⚠️ **意图识别节点的 `llmParam` 是 object（不是 array）**，且模型字段用 **`modelName`**（不是 `modleName`）。这与 LLM 节点(type=3)不同！

```json
{
  "id": "{{NODE_ID}}",
  "type": "22",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "{{INTENT_TITLE}}",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Intent-v2.jpg",
      "description": "用于用户输入的意图识别，并将其与预设意图选项进行匹配。",
      "mainColor": "#00B2B2",
      "subTitle": "意图识别"
    },
    "inputs": {
      "chatHistorySetting": { "enableChatHistory": false, "chatHistoryRound": 3 },
      "inputParameters": [
        {
          "name": "query",
          "input": {
            "type": "string",
            "value": {
              "type": "ref",
              "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{SOURCE_OUTPUT_NAME}}" },
              "rawMeta": { "type": 1 }
            }
          }
        }
      ],
      "llmParam": {
        "modelType": 80014,
        "modelName": "GLM-5.1",
        "generationDiversity": "balance",
        "temperature": 0.8,
        "maxTokens": 4096,
        "topP": 0.95,
        "responseFormat": 2,
        "thinking": 0,
        "prompt": { "type": "string", "value": { "type": "literal", "content": "{{query}}" } },
        "systemPrompt": { "type": "string", "value": { "type": "literal", "content": "根据用户输入判断其意图类别。" } },
        "enableChatHistory": false,
        "chatHistoryRound": 3
      },
      "intents": [
        { "name": "意图1" },
        { "name": "意图2" },
        { "name": "意图3" }
      ],
      "mode": "all",
      "settingOnError": { "processType": 1, "timeoutMs": 60000, "retryTimes": 0 }
    },
    "outputs": [
      { "type": "integer", "name": "classificationId" },
      { "type": "string", "name": "reason" }
    ]
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 263.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Intent-v2.jpg",
      "description": "用于用户输入的意图识别，并将其与预设意图选项进行匹配。",
      "title": "意图识别",
      "mainColor": "#00B2B2"
    }
  }
}
```

### 意图识别 vs LLM 节点关键差异

| 差异项 | LLM 节点(type=3) | 意图识别(type=22) |
|--------|-----------------|-----------------|
| llmParam 类型 | **Array** | **Object** |
| 模型名称字段 | `modleName`（少一个e） | `modelName`（标准拼写） |
| 额外字段 | — | `chatHistorySetting`, `intents`, `mode` |
| 固定输出 | `output`, `reasoning_content` | `classificationId`(integer), `reason`(string) |

### 连线端口说明

意图分支端口用 `branch_N` 格式，默认"其他"分支用 `default`：

| 端口 | 说明 |
|------|------|
| `"branch_0"` | 第 1 个意图 |
| `"branch_1"` | 第 2 个意图 |
| `"branch_N"` | 第 N+1 个意图 |
| `"default"` | "其他"兜底分支（始终存在） |

> ⚠️ **不是** `"0"`, `"1"`, `"2"`！是 `"branch_0"`, `"branch_1"` ... 加 `"default"`。
> ⚠️ 意图数量 = `intents` 数组长度，连线数量 = 意图数 + 1（含 default）。

---

## 知识库写入

type=27, 向知识库写入文本。

> ⚠️ **`inputParameters` 固定为空数组 `[]`**。节点只接受 Doc 或 File 类型的输入（在 GUI 中配置上游文件变量），不能通过 inputParameters 传入 string 文本。
> ⚠️ **`strategyParam` 必须包含三个策略**：`parsingStrategy`、`chunkStrategy`、`indexStrategy`，缺少任何一个都会导致写入异常。
> ⚠️ **`datasetList` 中只能放一个知识库 ID，且必须是文本类型的知识库**。

```json
{
  "id": "{{NODE_ID}}",
  "type": "27",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "知识库写入",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-KnowledgeWriting-v2.jpg",
      "description": "写入节点可以添加文本类型的知识库，仅可以添加一个知识库",
      "mainColor": "#FF811A",
      "subTitle": "知识库写入"
    },
    "outputs": [
      { "type": "string", "name": "documentId" },
      { "type": "string", "name": "fileName" },
      { "type": "string", "name": "fileUrl" }
    ],
    "inputs": {
      "inputParameters": [],
      "datasetParam": [
        { "name": "datasetList", "input": { "type": "list", "schema": { "type": "string" }, "value": { "type": "literal", "content": [] } } }
      ],
      "strategyParam": {
        "parsingStrategy": { "parsingType": "fast" },
        "chunkStrategy": { "chunkType": "default" },
        "indexStrategy": {}
      }
    }
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 139.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-KnowledgeWriting-v2.jpg",
      "description": "写入节点可以添加文本类型的知识库",
      "title": "知识库写入",
      "mainColor": "#FF811A"
    }
  }
}
```

注意：知识库写入是异步的，写完立即检索可能检索不到。`datasetList` 生成时写空数组，用户粘贴后在 GUI 手动选择**一个文本类型的知识库**。

---

## 批处理（容器节点）

type=28, 批量循环处理列表数据。**这是一个容器节点**，结构与循环节点(type=21)类似，内部嵌套子节点(blocks)和子连线(edges)。额外支持并发(`concurrentSize`)和批量大小(`batchSize`)配置。

```json
{
  "id": "{{NODE_ID}}",
  "type": "28",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} },
    "canvasPosition": { "x": {{X}}, "y": {{CANVAS_Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "批处理",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Batch-v2.jpg",
      "description": "通过设定批量运行次数和逻辑，运行批处理体内的任务",
      "mainColor": "#00B2B2",
      "subTitle": "批处理"
    },
    "inputs": {
      "concurrentSize": { "type": "integer", "value": { "type": "literal", "content": "10" } },
      "batchSize": { "type": "integer", "value": { "type": "literal", "content": "100" } },
      "inputParameters": [
        {
          "name": "input",
          "input": {
            "type": "list",
            "schema": { "type": "{{ITEM_TYPE}}" },
            "value": {
              "type": "ref",
              "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{SOURCE_OUTPUT_NAME}}" },
              "rawMeta": { "type": "{{LIST_RAW_META}}" }
            }
          }
        }
      ]
    },
    "outputs": [
      {
        "name": "{{字段名}}_list",
        "input": {
          "type": "list",
          "schema": { "type": "{{ITEM_ELEMENT_TYPE}}" },
          "value": {
            "type": "ref",
            "content": { "source": "block-output", "blockID": "{{内部子节点ID}}", "name": "{{内部节点输出字段名}}" },
            "rawMeta": { "type": "{{ELEMENT_RAW_META}}" }
          }
        }
      }
    ]
  },
  "blocks": [],
  "edges": [],
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 139.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Batch-v2.jpg",
      "description": "通过设定批量运行次数和逻辑，运行批处理体内的任务",
      "title": "批处理",
      "mainColor": "#00B2B2"
    }
  }
}
```

> ⚠️ **Object-First 原则**：代码节点构建 list 时**必须**直接 `append` dict → `schema:{"type":"object"}`，**禁止** `json.dumps(dict)` 再 append。代码返回值类型、上游 outputs 声明、批处理 input schema 三者必须一致。完整示例见上方循环节点的「Object-First 完整示例」。
>
> ⚠️ **rawMeta 必须与 ITEM_TYPE 匹配**：`{{LIST_RAW_META}}` = list[string]→99, list[object]→103, list[integer]→100, list[float]→102。

> ### ⚠️⚠️⚠️ 批处理/循环 outputs 结构 vs 普通节点 outputs 结构（致命差异）
>
> **普通节点**（LLM/代码/HTTP/文本处理等）outputs 是扁平声明：
> ```json
> "outputs": [ { "type": "string", "name": "result" } ]
> ```
>
> **容器节点**（循环 type=21 / 批处理 type=28）outputs **必须用 `{name, input:{...}}` 包装结构**：
> ```json
> "outputs": [ { "name": "result_list", "input": { "type": "list", "schema": {...}, "value": {...} } } ]
> ```
>
> **同理，容器节点的 `concurrentSize`/`batchSize`/`loopCount` 等参数也必须用 typed value 结构**：
> ```json
> ✅ "concurrentSize": { "type": "integer", "value": { "type": "literal", "content": "10" } }
> ❌ "concurrentSize": 10
> ```
> **绝不允许写裸数值！** 所有容器节点参数都遵循 `{ "type": "xxx", "value": { "type": "literal"/"ref", ... } }` 标准结构。

批处理特殊说明：
- `blocks`/`edges` 在节点**顶层**（与 `data` 同级）
- 引用批处理循环变量: `blockID` = 批处理节点 ID, `name` = "input.字段名"
- **内部 item 类型是元素类型，不是 list**：输入 `list[object]` → 内部每次迭代收到 `object`；内部节点 inputParameters 声明为 `"type": "object"`，不能是 `"type": "list"`
- 内部连线到批处理: `targetPortID = "batch-function-inline-input"`
- 批处理到外部: `sourcePortID = "batch-function-inline-output"`

### ⚠️ 批处理输出设计（致命级，最常犯错）

**核心认知：输出是"多列并行 list"，不是"一个 object list"。**

```
❌ 错误理解：
  output = [ {dimension: "...", analysis: "...", confidence: 80}, {...}, {...} ]
  → 一个 list[object]，每个 object 包含所有字段

✅ 正确理解：
  dimension_list   = ["维度A", "维度B", "维度C"]        → list[string]
  analysis_list    = ["分析A", "分析B", "分析C"]        → list[string]
  confidence_list  = [80, 75, 90]                       → list[integer]
  → 多个独立的 list，通过 index 对齐
```

每个输出变量独立收集内部子节点该字段在每次迭代中的值，组成一个 list。需要几个字段就声明几个输出变量。

#### 批处理输出声明示例

假设内部 LLM 节点有 3 个业务输出（`dimension`, `analysis`, `confidence`），批处理节点声明 3 个输出：

```json
"outputs": [
  {
    "name": "dimension_list",
    "input": {
      "type": "list",
      "schema": { "type": "string" },
      "value": {
        "type": "ref",
        "content": { "source": "block-output", "blockID": "{{内部LLM节点ID}}", "name": "dimension" },
        "rawMeta": { "type": 1 }
      }
    }
  },
  {
    "name": "analysis_list",
    "input": {
      "type": "list",
      "schema": { "type": "string" },
      "value": {
        "type": "ref",
        "content": { "source": "block-output", "blockID": "{{内部LLM节点ID}}", "name": "analysis" },
        "rawMeta": { "type": 1 }
      }
    }
  },
  {
    "name": "confidence_list",
    "input": {
      "type": "list",
      "schema": { "type": "integer" },
      "value": {
        "type": "ref",
        "content": { "source": "block-output", "blockID": "{{内部LLM节点ID}}", "name": "confidence" },
        "rawMeta": { "type": 2 }
      }
    }
  }
]
```

> ⚠️ **命名建议**：批处理输出变量用 `{原字段名}_list` 后缀命名，与内部节点的单值输出做明确区分。

#### rawMeta 双层区分（极易出错）

| 位置 | rawMeta.type 含义 | string | integer | float | object |
|------|-------------------|--------|---------|-------|--------|
| **批处理输出声明**中（ref 引用内部节点单个输出） | 元素原始类型 | 1 | 2 | 4 | 6 |
| **下游节点输入引用**批处理输出时 | list 整体类型 | 99 | 100 | 102 | 103 |

#### 下游代码节点解析模式（必须按 index 对齐）

```python
# ❌ 错误写法：把批处理输出当 list[object] 遍历
for r in batch_results:
    dim = r.get('dimension', '')      # ← 运行时 r 是 string，不是 dict！
    analysis = r.get('analysis', '')  # ← 报错 AttributeError

# ✅ 正确写法：接收多个独立 list，按 index 对齐
dimension_list = args.params.get('dimension_list', [])
analysis_list = args.params.get('analysis_list', [])
confidence_list = args.params.get('confidence_list', [])

count = len(dimension_list)
results = []
for i in range(count):
    dim = dimension_list[i] if i < len(dimension_list) else '未知'
    analysis = analysis_list[i] if i < len(analysis_list) else ''
    confidence = confidence_list[i] if i < len(confidence_list) else 50
    results.append(f"【{dim}】(置信度:{confidence})\n{analysis}")
```

> ⚠️ **不需要输出 `reasoning_content`**：这是 LLM 节点的思考过程日志，通常不需传递给下游业务逻辑，批处理输出中可以省略。

---

## 输入

type=30, 中间过程信息输入。

```json
{
  "id": "{{NODE_ID}}",
  "type": "30",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "{{INPUT_TITLE}}",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Input-v2.jpg",
      "description": "用于中间过程信息输入",
      "mainColor": "#5C62FF",
      "subTitle": "输入"
    },
    "inputs": { "inputParameters": [] },
    "outputs": [
      { "type": "string", "name": "output" }
    ]
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 113.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-Input-v2.jpg",
      "description": "用于中间过程信息输入",
      "title": "输入",
      "mainColor": "#5C62FF"
    }
  }
}
```

---

## 变量聚合

type=32, 聚合多分支输出，取多分支中第一个非空值。

```json
{
  "id": "{{NODE_ID}}",
  "type": "32",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "{{MERGE_TITLE}}",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/VariableMerge-icon.jpg",
      "description": "用于对多条通道传入的变量信息进行合并处理",
      "mainColor": "#00B2B2",
      "subTitle": "变量聚合"
    },
    "inputs": {
      "mergeGroups": [
        {
          "name": "final_result",
          "variables": [
            { "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "{{BRANCH_A_NODE_ID}}", "name": "result" }, "rawMeta": { "type": 1 } } },
            { "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "{{BRANCH_B_NODE_ID}}", "name": "result" }, "rawMeta": { "type": 1 } } }
          ]
        }
      ]
    },
    "outputs": [
      { "type": "string", "name": "final_result" }
    ]
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 87.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/VariableMerge-icon.jpg",
      "description": "用于对多条通道传入的变量信息进行合并处理",
      "title": "变量聚合",
      "mainColor": "#00B2B2"
    }
  }
}
```

### 关键规则

1. `mergeGroups[].variables[]` 中每个变量的 `blockID` 必须是实际上游分支节点 ID
2. `outputs` 数组**不能为空**，必须为每个 mergeGroup 声明一个输出变量
3. `mergeGroups[].name` 与 `outputs[].name` 必须一一对应
4. **组名长度不超过 20 个字符**
5. 保留原始变量类型，不要合并成 string

---

## 变量赋值

type=40, 给变量赋值。结构包含 `left`(目标变量) + `input`(赋值源) + `variableTypeMap` 三段式。

```json
{
  "id": "{{NODE_ID}}",
  "type": "40",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "{{ASSIGN_TITLE}}",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-VariableAssign-v2.jpg",
      "description": "用于给支持写入的变量赋值，包括应用变量、用户变量",
      "mainColor": "#FF811A",
      "subTitle": "变量赋值"
    },
    "inputs": {
      "inputParameters": [
        {
          "name": "{{TARGET_VAR_NAME}}",
          "left": {
            "type": "string",
            "value": {
              "type": "ref",
              "content": { "source": "global_variable_app", "path": ["{{TARGET_VAR_NAME}}"], "blockID": "", "name": "" }
            }
          },
          "input": {
            "type": "string",
            "value": {
              "type": "ref",
              "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{SOURCE_OUTPUT_NAME}}" },
              "rawMeta": { "type": 1 }
            }
          }
        }
      ],
      "variableTypeMap": { "{{TARGET_VAR_NAME}}": "global_variable_app" }
    },
    "outputs": [
      { "name": "isSuccess", "type": "boolean" }
    ]
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 137.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/Variable.jpg",
      "description": "用于给支持写入的变量赋值，包括应用变量、用户变量",
      "title": "变量赋值",
      "mainColor": "#FF811A"
    }
  }
}
```

### 关键说明

- `left`：赋值**目标**（要写入的全局变量），source 为 `global_variable_app`
- `input`：赋值**源**（要赋的值），可以是 ref 引用上游节点输出或 literal 固定值
- `variableTypeMap`：声明每个目标变量的来源类型（`"global_variable_app"`）
- 输出固定为 `isSuccess`(boolean)

---

## 数据库节点通用说明

### 平台图形化数据库（非 MySQL）

原力平台提供的是**图形化数据库组件**，用户通过 GUI 界面创建表和字段，**不是自建 MySQL 库**。除非用户明确说明使用自建 MySQL，否则默认使用平台图形化数据库。

### 🔴 databaseInfoList 格式（极其重要）

`databaseInfoList` 是告诉节点要操作哪张表的唯一方式。**格式只有一种**：

```json
// ✅ 正确格式 — 用户提供了表ID时直接填入
"databaseInfoList": [{ "databaseInfoID": "7631171667347111936" }]

// ✅ 用户未提供表ID时写空数组，粘贴后 GUI 手动选择
"databaseInfoList": []

// ❌ 错误格式 — AI 自行猜测的结构，平台完全不认
"databaseInfoList": [{ "tableID": "...", "fields": [...] }]
"databaseInfoList": [{ "tableName": "my_table" }]
```

> ⚠️ 如果用户明确提供了 `databaseInfoID`，直接填入即可；否则写空数组让用户在 GUI 中选择。

### 🔴 fieldList 格式（查询数据节点 selectParam 中使用）

查询数据(type=43)的 `selectParam` 可以通过 `fieldList` 指定返回哪些列。缺失则返回全部列：

```json
"selectParam": {
  "fieldList": [
    { "fieldID": 1, "isDistinct": false },
    { "fieldID": 2, "isDistinct": false },
    { "fieldID": 3, "isDistinct": false }
  ],
  "condition": { ... },
  "orderByList": [],
  "limit": 100
}
```

> `fieldID` 是从 **1** 开始的连续整数（**注意这里是 number 不是 string**），对应表中自定义字段的顺序。如不确定具体字段编号，可省略 `fieldList` 让平台返回全部列。

### conditionList 条件结构（查询/更新/删除通用）

`conditionList` 是**二维数组**，每个条件是 `[{left:字段名}, {operation:操作符}, {right:值}]` 三元组：

```json
"condition": {
  "conditionList": [
    [
      { "name": "left", "input": { "type": "string", "value": { "type": "literal", "content": "domain" } } },
      { "name": "operation", "input": { "type": "string", "value": { "type": "literal", "content": "EQUAL" } } },
      { "name": "right", "input": { "type": "string", "value": { "type": "literal", "content": "example.com", "rawMeta": { "type": 1 } } } }
    ],
    [
      { "name": "left", "input": { "type": "string", "value": { "type": "literal", "content": "status" } } },
      { "name": "operation", "input": { "type": "string", "value": { "type": "literal", "content": "NOT_EQUAL" } } },
      { "name": "right", "input": { "type": "string", "value": { "type": "literal", "content": "deleted", "rawMeta": { "type": 1 } } } }
    ]
  ],
  "logic": "AND"
}
```

**right 也可以用 ref 引用上游变量**：
```json
{ "name": "right", "input": { "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "601001", "name": "domain" }, "rawMeta": { "type": 1 } } } }
```

**操作符枚举**：`EQUAL`、`NOT_EQUAL`、`LIKE`（模糊匹配）、`NOT_LIKE`、`GREATER_THAN`、`LESS_THAN`、`GREATER_THAN_OR_EQUAL`、`LESS_THAN_OR_EQUAL`

**logic**：`"AND"` 或 `"OR"`（字符串，非数字）

### fieldInfo 字段赋值结构（新增/更新通用）

`fieldInfo` 是二维数组，每个字段赋值是 `[{fieldID}, {fieldValue}]` 二元组：

```json
"fieldInfo": [
  [
    { "name": "fieldID", "input": { "type": "string", "value": { "type": "literal", "content": "2" } } },
    { "name": "fieldValue", "input": { "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "601001", "name": "domain" }, "rawMeta": { "type": 1 } } } }
  ]
]
```

### 🔴 fieldInfo 中的 fieldID 是数字字符串（新增/更新节点）

`fieldID` 的 `content` 值必须是**数字字符串**（如 `"1"`, `"2"`, `"3"`），代表字段在数据库表中的编号（从 1 开始），**绝不是字段名字符串**：

```json
// ✅ 正确：数字字符串编号
{ "name": "fieldID", "input": { "type": "string", "value": { "type": "literal", "content": "1" } } }
{ "name": "fieldID", "input": { "type": "string", "value": { "type": "literal", "content": "2" } } }

// ❌ 错误：字段名字符串（AI 常见错误）
{ "name": "fieldID", "input": { "type": "string", "value": { "type": "literal", "content": "proc_cmd_pattern" } } }
{ "name": "fieldID", "input": { "type": "string", "value": { "type": "literal", "content": "domain" } } }
```

> 用户需在平台 GUI 中查看每个字段的编号。生成时如不确定具体编号，可用占位符 `"{{FIELD_ID_1}}"`, `"{{FIELD_ID_2}}"` 等，并在 Phase 4 中提醒用户替换。

> ⚠️ **fieldID 编号依赖用户建表时的字段创建顺序**：`fieldID = "1"` 对应用户创建的第 1 个自定义字段，`"2"` 对应第 2 个，以此类推。生成 JSON 时给出的字段顺序建议必须与 Phase 4 中建表指引的字段顺序完全一致。如果用户实际建表时字段顺序与建议不同，fieldID 会对不上，导致数据写错列。**当字段顺序不确定或不可控时，建议改用 SQL 自定义节点(type=12)通过字段名操作，避免 fieldID 编号问题**。

### fieldValue 的 type 和 rawMeta 必须匹配字段类型

`fieldValue` 的 `input.type` 和 `rawMeta.type` 必须与目标数据库字段的实际类型对应：

| 数据库字段类型 | fieldValue.input.type | rawMeta.type | content 示例 |
|---------------|----------------------|-------------|-------------|
| String | `"string"` | 1 | `"hello"` |
| Integer | `"integer"` | 2 | `1`（注意是数字不是字符串） |
| Number(浮点) | `"float"` | 4 | `3.14` |
| Boolean | `"boolean"` | 3 | `true` |

示例 — integer 类型字段的赋值：
```json
{ "name": "fieldValue", "input": { "type": "integer", "value": { "type": "literal", "content": 1, "rawMeta": { "type": 2 } } } }
```

示例 — float 类型字段的赋值（使用 ref 引用上游）：
```json
{ "name": "fieldValue", "input": { "type": "float", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "601001", "name": "score" }, "rawMeta": { "type": 4 } } } }
```

> `fieldID` 是字段在数据库中的编号（字符串），用户需在 GUI 中查看。生成时可用占位符。

### 平台数据库支持的字段类型（仅 5 种）

| 类型 | 说明 | 示例 |
|------|------|------|
| String | 字符串 | 域名、名称、描述、JSON文本 |
| Integer | 整数 | 状态码、计数、等级 |
| Number | 浮点数 | 评分、金额、概率 |
| Boolean | 布尔值 | 是否启用、是否通过 |
| Time | 时间 | 过期时间、更新时间 |

> ⚠️ 没有 `float`、`text`、`varchar`、`datetime`、`bigint` 等 MySQL 类型。生成数据库表结构建议时，字段类型只能从以上 5 种中选择。

### 平台数据库表默认字段（系统自动创建）

每张表**自动包含 3 个系统字段**，无需用户手动创建：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Integer | 数据唯一标识（主键），自增 |
| `uuid` | String | 用户唯一标识，系统自动生成 |
| `bstudio_create_time` | Time | 数据插入时间，系统自动记录 |

### 去重注意事项

- 自定义字段**无法设置唯一键**
- 若业务需要某字段唯一（如白名单中的 domain、email 等），**必须在新增数据前用查询数据节点(43)检查是否已存在**，不存在时才执行插入
- 不要假设平台会自动去重
- **禁止**用 SQL 自定义(12)做去重查询后判断 rowNum（rowNum 始终为 null）

### 去重模式（推荐 — 查询数据 + 选择器判空）

**适用场景**：白名单、唯一字段去重、防重复插入等。

**流程**：查询数据(43) → 选择器(8)判断 `outputList` 是否不为空 → 不为空则已存在(跳过插入)，为空则不存在(执行插入)

1. **查询数据(43)**：配置 `selectParam.condition` 按目标字段查询（如 `domain EQUAL {{输入域名}}`）
2. **选择器(8)**：判断查询结果 `outputList` **不为空(operator=10)**
   - **true 分支**（outputList 不为空 → 数据已存在）：跳过插入，或走"已存在"的处理逻辑
   - **false/否则分支**（outputList 为空 → 数据不存在）：执行新增数据(46)或 SQL INSERT

选择器节点关键结构：
```json
{
  "branches": [{
    "condition": {
      "logic": 2,
      "conditions": [{
        "operator": 10,
        "left": {
          "input": {
            "type": "list",
            "schema": { "type": "object", "schema": [] },
            "value": {
              "type": "ref",
              "content": {
                "source": "block-output",
                "blockID": "{{查询数据节点ID}}",
                "name": "outputList"
              }
            }
          }
        }
      }]
    }
  }]
}
```

> ⚠️ 这里用 **operator=10（不为空）** 判断 outputList，不为空说明已有数据，走 true 分支跳过；为空说明不存在，走 false/否则分支执行插入。

### UPSERT 模式（先查后更新/插入）

**适用场景**：数据存在则更新，不存在则新增。

**方案 A（推荐）— 查询数据(43) + 选择器(8) + 更新/新增分支**：
1. 查询数据(43): 按条件查询（如 `domain EQUAL {{key}}`）
2. 选择器(8): 判断 `outputList` 不为空(operator=10)
3. true 分支（已存在）→ 更新数据(42): 配置条件 `domain = {{key}}`，更新目标字段
4. false/否则分支（不存在）→ 新增数据(46) 或 SQL 自定义(12): `INSERT INTO t (uuid, col1, col2) VALUES (UUID(), '{{val1}}', '{{key}}')`

**方案 B — 用图形化更新节点(42)，`rowNum` 可用**：
1. 更新数据(42): 配置条件 `col2 = {{key}}`，更新 `col1 = {{val1}}`
2. 选择器(8): 判断 `rowNum == 0`（未更新到任何记录，说明不存在）
3. 新增数据(46) 或 SQL 自定义(12): `INSERT INTO t (uuid, col1, col2) VALUES (UUID(), '{{val1}}', '{{key}}')`

> ⚠️ **`rowNum` 可用性速记**：查询数据(43)和 SQL 自定义(12)的 `rowNum` 始终为 null 不可用；更新(42)/新增(46)/删除(44)的 `rowNum` 返回真实影响行数，可直接用于选择器分支判断。

### SQL INSERT 必须包含 uuid 列

平台只兼容 SQL92 常用语法，且执行 INSERT 时**会校验 uuid 列的存在**：

```
❌ INSERT INTO t (col1, col2) VALUES ('a', 'b')
   → 报错: expected N+1 arguments, got N（缺少 uuid 列）

❌ INSERT INTO t (col1) SELECT ... FROM DUAL WHERE NOT EXISTS (...)
   → 报错: Column count doesn't match（子查询语法不兼容）

✅ INSERT INTO t (uuid, col1, col2) VALUES (UUID(), 'a', 'b')
   → 正常执行
```

### 查询数据节点 outputs schema 定义

当查询数据节点(type=43)需要返回具体字段时，**必须在 `outputs[0].schema.schema` 中逐个定义字段**，否则下游无法通过 `outputList.xxx` 引用字段：

```json
"outputs": [
  {
    "type": "list",
    "name": "outputList",
    "schema": {
      "type": "object",
      "schema": [
        { "type": "string", "name": "proc_cmd_pattern" },
        { "type": "string", "name": "proc_name" },
        { "type": "integer", "name": "hit_count" },
        { "type": "string", "assistType": 10000, "name": "bstudio_create_time" }
      ]
    }
  },
  { "type": "integer", "name": "rowNum" }
]
```

> 系统字段 `bstudio_create_time` 需加 `"assistType": 10000` 标记。`id`/`uuid` 通常不需要在 schema 中定义，除非下游确实要用。

### 更新节点 conditionList 多条件 + OR 逻辑示例

```json
"condition": {
  "conditionList": [
    [
      { "name": "left", "input": { "type": "string", "value": { "type": "literal", "content": "uuid" } } },
      { "name": "operation", "input": { "type": "string", "value": { "type": "literal", "content": "EQUAL" } } },
      { "name": "right", "input": { "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "701013", "name": "input" }, "rawMeta": { "type": 1 } } } }
    ],
    [
      { "name": "left", "input": { "type": "string", "value": { "type": "literal", "content": "proc_cmd_pattern" } } },
      { "name": "operation", "input": { "type": "string", "value": { "type": "literal", "content": "LIKE" } } },
      { "name": "right", "input": { "type": "string", "value": { "type": "literal", "content": "abc", "rawMeta": { "type": 1 } } } }
    ]
  ],
  "logic": "OR"
}
```

> 多个条件组放在 `conditionList` 的不同数组元素中，通过 `logic` 字段指定 `"AND"` 或 `"OR"` 关系。

### 更新节点 fieldInfo — integer 类型字段赋值示例

```json
"fieldInfo": [
  [
    { "name": "fieldID", "input": { "type": "string", "value": { "type": "literal", "content": "11" } } },
    { "name": "fieldValue", "input": { "type": "integer", "value": { "type": "literal", "content": 1, "rawMeta": { "type": 2 } } } }
  ]
]
```

> 注意 integer 类型的 `content` 是数字 `1` 而非字符串 `"1"`，`rawMeta.type` 为 `2`。

---

## 更新数据

type=42, 更新数据表记录。适用于简单的单表更新操作，复杂更新逻辑用 SQL 自定义(12)。**优先使用此节点而非 SQL 自定义**。

> **注意**：`databaseInfoList` 若用户提供了表ID则填 `[{"databaseInfoID": "表ID"}]`，否则写空数组 `[]`。

```json
{
  "id": "{{NODE_ID}}",
  "type": "42",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "inputs": {
      "databaseInfoList": [{ "databaseInfoID": "{{TABLE_ID}}" }],
      "updateParam": {
        "condition": {
          "conditionList": [
            [
              { "name": "left", "input": { "type": "string", "value": { "type": "literal", "content": "{{FIELD_NAME}}" } } },
              { "name": "operation", "input": { "type": "string", "value": { "type": "literal", "content": "EQUAL" } } },
              { "name": "right", "input": { "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{SOURCE_VAR}}" }, "rawMeta": { "type": 1 } } } }
            ]
          ],
          "logic": "AND"
        },
        "fieldInfo": [
          [
            { "name": "fieldID", "input": { "type": "string", "value": { "type": "literal", "content": "{{FIELD_ID}}" } } },
            { "name": "fieldValue", "input": { "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{SOURCE_VAR}}" }, "rawMeta": { "type": 1 } } } }
          ]
        ]
      }
    },
    "outputs": [
      { "type": "list", "name": "outputList", "schema": { "type": "object", "schema": [] } },
      { "type": "integer", "name": "rowNum" }
    ],
    "nodeMeta": {
      "title": "更新数据",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-database-update.jpg",
      "description": "修改表中已存在的数据记录",
      "mainColor": "#F2B600",
      "subTitle": "更新数据"
    }
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 165.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-database-update.jpg",
      "description": "修改表中已存在的数据记录，用户指定更新条件和内容来更新数据",
      "title": "更新数据",
      "mainColor": "#F2B600"
    }
  }
}
```

---

## 查询数据

type=43, 从数据表查询数据。适用于简单的单表查询，复杂查询用 SQL 自定义(12)。**优先使用此节点而非 SQL 自定义**。

> **注意**：`databaseInfoList` 若用户提供了表ID则填 `[{"databaseInfoID": "表ID"}]`，否则写空数组 `[]`。

> 🔴 **致命陷阱：`rowNum` 始终为 null！** 查询数据节点(type=43)和 SQL 自定义节点(type=12)执行后，`rowNum` 输出**默认就是 null**，**不会**返回实际行数。只有 `outputList` 才会包含查询到的数据。因此：
> - ❌ **禁止**用 `rowNum > 0` 或 `rowNum == 0` 来判断是否查询到数据
> - ✅ 直接用选择器(8)判断 `outputList` **不为空**(operator=10)或**为空**(operator=9)，无需 right 字段
> - ✅ 或用代码节点(5)计算 `len(outputList)` 后传给选择器
> - ℹ️ **更新(42)/新增(46)/删除(44)节点的 `rowNum` 正常可用**，能返回真实影响行数

```json
{
  "id": "{{NODE_ID}}",
  "type": "43",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "inputs": {
      "databaseInfoList": [{ "databaseInfoID": "{{TABLE_ID}}" }],
      "selectParam": {
        "condition": {
          "conditionList": [
            [
              { "name": "left", "input": { "type": "string", "value": { "type": "literal", "content": "{{FIELD_NAME}}" } } },
              { "name": "operation", "input": { "type": "string", "value": { "type": "literal", "content": "EQUAL" } } },
              { "name": "right", "input": { "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{SOURCE_VAR}}" }, "rawMeta": { "type": 1 } } } }
            ]
          ],
          "logic": "AND"
        },
        "orderByList": [],
        "limit": 100
      },
      "settingOnError": { "processType": 1, "timeoutMs": 60000, "retryTimes": 0 }
    },
    "outputs": [
      { "type": "list", "name": "outputList", "schema": { "type": "object", "schema": [] } },
      { "type": "integer", "name": "rowNum" }
    ],
    "nodeMeta": {
      "title": "查询数据",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icaon-database-select.jpg",
      "description": "从表获取数据，用户可定义查询条件、选择列等，输出符合条件的数据",
      "mainColor": "#F2B600",
      "subTitle": "查询数据"
    }
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 156.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icaon-database-select.jpg",
      "description": "从表获取数据，用户可定义查询条件、选择列等，输出符合条件的数据",
      "title": "查询数据",
      "mainColor": "#F2B600"
    }
  }
}
```

---

## 删除数据

type=44, 删除数据表记录。

> **注意**：`databaseInfoList` 若用户提供了表ID则填 `[{"databaseInfoID": "表ID"}]`，否则写空数组 `[]`。

```json
{
  "id": "{{NODE_ID}}",
  "type": "44",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "inputs": {
      "databaseInfoList": [{ "databaseInfoID": "{{TABLE_ID}}" }],
      "deleteParam": {
        "condition": {
          "conditionList": [
            [
              { "name": "left", "input": { "type": "string", "value": { "type": "literal", "content": "{{FIELD_NAME}}" } } },
              { "name": "operation", "input": { "type": "string", "value": { "type": "literal", "content": "EQUAL" } } },
              { "name": "right", "input": { "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{SOURCE_VAR}}" }, "rawMeta": { "type": 1 } } } }
            ]
          ],
          "logic": "AND"
        }
      }
    },
    "outputs": [
      { "type": "list", "name": "outputList", "schema": { "type": "object", "schema": [] } },
      { "type": "integer", "name": "rowNum" }
    ],
    "nodeMeta": {
      "title": "删除数据",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-database-delete.jpg",
      "description": "从表中删除数据记录，用户指定删除条件来删除符合条件的记录",
      "mainColor": "#F2B600",
      "subTitle": "删除数据"
    }
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 156.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-database-delete.jpg",
      "description": "从表中删除数据记录，用户指定删除条件来删除符合条件的记录",
      "title": "删除数据",
      "mainColor": "#F2B600"
    }
  }
}
```

---

## HTTP请求

type=45, 发送 HTTP API 请求。推荐优先使用此节点处理网络请求，支持 GUI 配置鉴权、重试、超时。

### ⚠️ 致命差异：HTTP 的 inputParameters 与 LLM/代码节点完全不同！

| 对比项 | LLM / 代码节点 | HTTP 节点 |
|--------|---------------|-----------|
| **inputParameters 位置** | `data.inputs.inputParameters` | `data.inputParameters`（与 `inputs` 平级） |
| **inputParameters 用途** | 声明变量，在 prompt/代码中用 `{{varName}}` 引用 | **仅为 headers/params 等 ref 字段提供来源**，**不用于** url/json/rawText 插值 |
| **url / json / rawText 引用上游变量** | N/A | 直接写 `{{block_output_节点ID.变量名}}`，**不需要先在 inputParameters 声明** |
| **结构化字段 (headers/params) 引用** | N/A | 必须用 `{"type":"ref","content":{"source":"block-output","blockID":"节点ID","name":"变量名"}}` |

```
❌ 致命错误：把 HTTP 当 LLM 用
1. 在 data.inputParameters 声明 query 变量
2. 在 url 中写 "https://api.com/search?q={{query}}"
→ 运行时 {{query}} 无法解析！

✅ 正确做法：
1. data.inputParameters 保持 []（或省略）
2. 在 url 中直接写 "https://api.com/search?q={{block_output_601001.query}}"
→ 运行时自动从节点 601001 的 query 输出取值
```

### 完整模板

```json
{
  "id": "{{NODE_ID}}",
  "type": "45",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "nodeMeta": {
      "title": "HTTP 请求",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-HTTP.png",
      "description": "用于发送API请求，从接口返回数据",
      "mainColor": "#3071F2",
      "subTitle": "HTTP 请求"
    },
    "inputParameters": [],
    "inputs": {
      "apiInfo": {
        "method": "GET",
        "url": "https://api.example.com/path"
      },
      "body": {
        "bodyType": "JSON",
        "bodyData": {}
      },
      "headers": [],
      "params": [],
      "auth": {
        "authType": "NO_AUTH",
        "authData": {
          "customData": { "data": [], "addTo": "header" },
          "bearerTokenData": []
        },
        "authOpen": false
      },
      "setting": { "timeout": 120, "retryTimes": 3 },
      "settingOnError": {}
    },
    "outputs": [
      { "type": "string", "name": "body" },
      { "type": "integer", "name": "statusCode" },
      { "type": "string", "name": "headers" }
    ]
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 115.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-HTTP.png",
      "description": "用于发送API请求，从接口返回数据",
      "title": "HTTP 请求",
      "mainColor": "#3071F2"
    }
  }
}
```

### bodyType 完整枚举（6 种）— bodyData 字段按 bodyType 互斥

| bodyType | 用途 | bodyData 格式 | bodyData 中**只能存在**的字段 |
|----------|------|--------------|--------------------------|
| `JSON` | JSON 请求体 | `{"json": "{\"key\":\"{{block_output_ID.name}}\"}"}` | `json` |
| `FORM_DATA` | 文件上传/表单 | `{"formData": {"data": [...]}}` | `formData` |
| `FORM_URLENCODED` | 表单编码 | `{"formURLEncoded": [{"key":"k","value":{ref}}]}` | `formURLEncoded` |
| `RAW_TEXT` | 原始文本 | `{"rawText": "文本内容或{{block_output_ID.name}}"}` | `rawText` |
| `BINARY` | 二进制数据 | `{"binary": {ref}}` | `binary` |
| `EMPTY` | 无请求体 | `{}` | （空） |

> ⚠️ **bodyData 字段互斥**：选择一种 bodyType 后，bodyData 中**只放对应的那一个字段**。例如 bodyType=`RAW_TEXT` 时，bodyData 中只有 `rawText`，不能同时有 `json`/`binary` 等其他字段。

> 不存在 `RAW` 或 `X_WWW_FORM_URLENCODED`。

#### RAW_TEXT bodyType 完整示例

```json
{
  "body": {
    "bodyType": "RAW_TEXT",
    "bodyData": {
      "rawText": "用户查询：{{block_output_601001.user_query}}\n\n上下文：{{block_output_601002.context}}"
    }
  }
}
```

> `rawText` 中的 `{{block_output_ID.name}}` 运行时会自动替换为上游节点的输出值。

### 变量引用规则（极其重要）

> 🔴 **核心原则**：HTTP 节点的 url/json/rawText 使用 `{{block_output_节点ID.变量名}}` 直接引用上游输出，**不需要**在 inputParameters 中声明变量。这与 LLM/代码节点的 `{{varName}}` 模式完全不同！

| 字段位置 | 引用方式 | 示例 |
|---------|---------|------|
| `apiInfo.url` | `{{}}` 插值（直接引用上游） | `"https://api.com/{{block_output_601001.path}}"` |
| `bodyData.json` | `{{}}` 插值（直接引用上游） | `"{\"key\":\"{{block_output_601001.val}}\"}"` |
| `bodyData.rawText` | `{{}}` 插值（直接引用上游） | `"text: {{block_output_601001.content}}"` |
| `headers[].value` | **必须用 ref 对象** | 见下方示例 |
| `params[].value` | **必须用 ref 对象** | 见下方示例 |
| `formURLEncoded[].value` | **必须用 ref 对象** | 同上 |
| `formData.data[].value` | **必须用 ref 对象** | 同上 |

#### headers/params 引用上游变量（ref 方式）

```json
"headers": [
  {
    "key": "Authorization",
    "value": {
      "type": "ref",
      "content": { "source": "block-output", "blockID": "601001", "name": "token" }
    }
  }
]
```

#### headers 使用固定值（literal 方式）

```json
"headers": [
  {
    "key": "Content-Type",
    "value": {
      "type": "literal",
      "content": "application/json"
    }
  },
  {
    "key": "X-Custom-Header",
    "value": {
      "type": "literal",
      "content": "fixed-value-here"
    }
  }
]
```

> ⚠️ headers/params 的 value **只能是 ref 或 literal 对象**，不能直接写字符串，也不能在 literal 的 content 中使用 `{{}}` 插值。如果需要拼接动态值到 header，应使用上游代码节点先拼好字符串再 ref 引用。

```
❌ 错误：literal 中使用插值
"headers": [{"key":"Authorization","value":{"type":"literal","content":"Bearer {{block_output_601001.token}}"}}]

✅ 正确：纯动态值用 ref
"headers": [{"key":"Authorization","value":{"type":"ref","content":{"source":"block-output","blockID":"601001","name":"token"}}}]

✅ 正确：需要拼接前缀时，先用代码节点拼好 "Bearer xxx"，再 ref 引用代码节点输出
```

### 全局变量鉴权示例

```json
"headers": [
  {
    "key": "Authorization",
    "value": {
      "type": "ref",
      "content": { "source": "global_variable_app", "path": ["API_KEY"], "blockID": "", "name": "" }
    }
  }
]
```

---

## 新增数据

type=46, 向数据表插入新记录。**优先使用此节点而非 SQL INSERT**。

> **注意**：`databaseInfoList` 若用户提供了表ID则填 `[{"databaseInfoID": "表ID"}]`，否则写空数组 `[]`。

```json
{
  "id": "{{NODE_ID}}",
  "type": "46",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "inputs": {
      "databaseInfoList": [{ "databaseInfoID": "{{TABLE_ID}}" }],
      "insertParam": {
        "fieldInfo": [
          [
            { "name": "fieldID", "input": { "type": "string", "value": { "type": "literal", "content": "{{FIELD_ID}}" } } },
            { "name": "fieldValue", "input": { "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "{{SOURCE_NODE_ID}}", "name": "{{SOURCE_VAR}}" }, "rawMeta": { "type": 1 } } } }
          ]
        ]
      },
      "settingOnError": { "processType": 1, "timeoutMs": 60000, "retryTimes": 0 }
    },
    "outputs": [
      { "type": "list", "name": "outputList", "schema": { "type": "object", "schema": [] } },
      { "type": "integer", "name": "rowNum" }
    ],
    "nodeMeta": {
      "title": "新增数据",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-database-insert.jpg",
      "description": "向表添加新数据记录",
      "mainColor": "#F2B600",
      "subTitle": "新增数据"
    }
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 166.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-database-insert.jpg",
      "description": "向表添加新数据记录，用户输入数据内容后插入数据库",
      "title": "新增数据",
      "mainColor": "#F2B600"
    }
  }
}
```

---

## JSON序列化

type=58, 将变量转为 JSON 字符串。

```json
{
  "id": "{{NODE_ID}}",
  "type": "58",
  "meta": {
    "position": { "x": {{X}}, "y": {{Y}} }
  },
  "data": {
    "outputs": [{ "type": "string", "name": "output" }],
    "nodeMeta": {
      "title": "JSON 序列化",
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-to_json.png",
      "description": "用于把变量转化为JSON字符串",
      "mainColor": "F2B600",
      "subTitle": "JSON 序列化"
    }
  },
  "_temp": {
    "bounds": { "x": {{X}}, "y": {{Y}}, "width": 360, "height": 113.9 },
    "externalData": {
      "icon": "https://lf3-static.bytednsdoc.com/obj/eden-cn/dvsmryvd_avi_dvsm/ljhwZthlaukjlkulzlp/icon/icon-to_json.png",
      "description": "用于把变量转化为JSON字符串",
      "title": "JSON 序列化",
      "mainColor": "F2B600"
    }
  }
}
```

---

## 连线 (Edge) 完整格式参考

工作流中节点之间的连线通过 `edges` 数组定义。每条连线描述一个从源节点到目标节点的数据流向。

### 开始/结束节点 ID（固定值）

| 节点 | NodeID | 说明 |
|------|--------|------|
| **开始节点** | `"100001"` | 画布上预置的起始节点，所有工作流入口 |
| **结束节点** | `"900001"` | 画布上预置的终止节点，所有工作流出口 |

> ⚠️ **生成 edges 时必须包含开始和结束节点的连线**，这样粘贴后可自动与画布上已有的系统节点正确连接，无需用户手动拉线。

### 基础结构

```json
{
  "sourceNodeID": "601001",
  "targetNodeID": "601002",
  "sourcePortID": "",
  "targetPortID": ""
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `sourceNodeID` | string | ✅ | 来源节点 ID，必须与某个 node 的 `id` 一致 |
| `targetNodeID` | string | ✅ | 目标节点 ID，必须与某个 node 的 `id` 一致 |
| `sourcePortID` | string | 条件 | 来源端口 ID，分支/容器节点必填，普通节点留空字符串 `""` |
| `targetPortID` | string | 条件 | 目标端口 ID，容器节点内部连入时必填，普通节点留空字符串 `""` |

### 各场景连线格式

#### 1. 开始节点(100001) → 工作流第一个节点

```json
{ "sourceNodeID": "100001", "targetNodeID": "601001", "sourcePortID": "", "targetPortID": "" }
```

#### 2. 工作流最后一个节点 → 结束节点(900001)

```json
{ "sourceNodeID": "601005", "targetNodeID": "900001", "sourcePortID": "", "targetPortID": "" }
```

> 如果工作流有多个分支末端（如选择器的不同分支），每个分支末端都需要一条连到 900001 的 edge。

#### 3. 普通节点 → 普通节点

```json
{ "sourceNodeID": "601001", "targetNodeID": "601002", "sourcePortID": "", "targetPortID": "" }
```

#### 4. 选择器(type=8) → 下游（双分支）

```json
// 条件成立
{ "sourceNodeID": "601003", "targetNodeID": "601004", "sourcePortID": "true", "targetPortID": "" }
// 否则
{ "sourceNodeID": "601003", "targetNodeID": "601005", "sourcePortID": "false", "targetPortID": "" }
```

#### 5. 选择器(type=8) → 下游（多分支 ≥3）

```json
{ "sourceNodeID": "601003", "targetNodeID": "601004", "sourcePortID": "true", "targetPortID": "" }
{ "sourceNodeID": "601003", "targetNodeID": "601005", "sourcePortID": "true_1", "targetPortID": "" }
// 最后的否则分支
{ "sourceNodeID": "601003", "targetNodeID": "601006", "sourcePortID": "false", "targetPortID": "" }
```

#### 6. 意图识别(type=22) → 下游

```json
{ "sourceNodeID": "601003", "targetNodeID": "601004", "sourcePortID": "branch_0", "targetPortID": "" }
{ "sourceNodeID": "601003", "targetNodeID": "601005", "sourcePortID": "branch_1", "targetPortID": "" }
// 默认兜底分支
{ "sourceNodeID": "601003", "targetNodeID": "601006", "sourcePortID": "default", "targetPortID": "" }
```

#### 7. processType=3 异常端口连线

```json
{ "sourceNodeID": "601007", "targetNodeID": "601008", "sourcePortID": "branch_error", "targetPortID": "" }
```

#### 8. 循环容器(type=21) 内部连线

```json
// 容器 → 第一个内部节点（入口）
{ "sourceNodeID": "601010", "targetNodeID": "601011", "sourcePortID": "loop-function-inline-output", "targetPortID": "" }
// 内部普通连线
{ "sourceNodeID": "601011", "targetNodeID": "601012", "sourcePortID": "", "targetPortID": "" }
// 最后内部节点 → 容器（出口）
{ "sourceNodeID": "601012", "targetNodeID": "601010", "sourcePortID": "", "targetPortID": "loop-function-inline-input" }
```

#### 9. 批处理容器(type=28) 内部连线

```json
// 容器 → 第一个内部节点（入口）
{ "sourceNodeID": "601020", "targetNodeID": "601021", "sourcePortID": "batch-function-inline-output", "targetPortID": "" }
// 最后内部节点 → 容器（出口）
{ "sourceNodeID": "601022", "targetNodeID": "601020", "sourcePortID": "", "targetPortID": "batch-function-inline-input" }
```

### 关键规则总结

| 规则 | 说明 |
|------|------|
| **开始节点(100001)/结束节点(900001)必须连线** | edges 中必须包含 100001 → 第一个节点 和 最后一个节点 → 900001 的连线 |
| sourceNodeID/targetNodeID 必须真实存在 | 必须与 nodes 数组中某个节点的 `id` 完全匹配（100001/900001 除外） |
| 普通连线端口留空字符串 | `sourcePortID: ""`, `targetPortID: ""`，不能省略字段 |
| 选择器双分支用 `true`/`false` | 不是 `"0"`/`"1"`，是字符串 `"true"` 和 `"false"` |
| 选择器多分支用 `true`/`true_N`/`false` | 第1个 `"true"`，第2个 `"true_1"`，第3个 `"true_2"` ... 最后 `"false"`（否则分支） |
| 意图识别用 `branch_N` + `default` | `"branch_0"`, `"branch_1"` ... 对应意图编号，最后 `"default"` 为兜底 |
| 循环端口前缀 `loop-` | 入口: `sourcePortID="loop-function-inline-output"`，出口: `targetPortID="loop-function-inline-input"` |
| 批处理端口前缀 `batch-` | 入口: `sourcePortID="batch-function-inline-output"`，出口: `targetPortID="batch-function-inline-input"` |
| processType=3 异常端口 `branch_error` | `sourcePortID="branch_error"`，连到异常处理节点 |
| 容器内部连线放在容器的 `edges` 中 | 不放在顶层 `json.edges` 中，放在容器节点自身的 `edges` 数组中 |
| 禁止 edge 回环 | 不允许下游节点连回上游形成循环，重复执行用循环/批处理容器 |
| 4 个字段都必须存在 | 即使值为空字符串，字段不能省略 |

---

## rawMeta.type 完整映射参考

**错误的 rawMeta 会导致输入的类型被平台强行改变**，必须严格按此表填写。

### 标量类型（1~6）

| rawMeta.type | input.type | 说明 |
|:---:|:---|:---|
| **1** | `string` | 字符串 |
| **2** | `integer` | 整数 |
| **3** | `boolean` | 布尔值 |
| **4** | `float` | 浮点数 |
| **6** | `object` | 对象（⚠️ 不是 1） |

### 文件类型（7~17）

文件类型统一用 `type="string"`，通过 **`assistType`** 区分子类型：

| rawMeta.type | assistType | 文件子类型 |
|:---:|:---:|:---|
| **7** | 2 | Image（图片） |
| **8** | 1 | Default（通用文件） |
| **9** | 3 | Doc（文档） |
| **10** | 4 | Code（代码） |
| **11** | 5 | PPT（演示文稿） |
| **12** | 6 | Txt（文本） |
| **13** | 7 | Excel（表格） |
| **14** | 8 | Audio（音频） |
| **15** | 9 | Zip（压缩包） |
| **16** | 10 | Video（视频） |
| **17** | 11 | Svg（矢量图） |

### 列表类型（99~116）

| rawMeta.type | schema.type | 说明 |
|:---:|:---|:---|
| **99** | `string` | list[string]（⚠️ 不是 103） |
| **100** | `integer` | list[integer] |
| **101** | `boolean` | list[boolean] |
| **102** | `float` | list[float] |
| **103** | `object` | list[object] |
| **116** | `string` + assistType:10000 | list[file] |

### 常见错误

| 错误 | 正确 |
|------|------|
| object 用 rawMeta=1 | object → rawMeta=**6** |
| 所有 list 都用 rawMeta=103 | list[string]→**99**, list[integer]→**100**, list[object]→103 |
| 所有 file 都用 rawMeta=8 | 8 仅是 Default 文件，图片=7, 文档=9 等 |

---

## 模型映射表

LLM 节点(type=3)的 `modleName` + `modelType` 对照表：

| modleName | modelType | 特殊说明 |
|-----------|-----------|---------|
| **GLM-5.1** | 80014 | ⭐ 首选推荐，默认 maxTokens=65536 |
| **DeepSeek-V3.2** | 80009 | 备选推荐 |
| **GPT-OSS-120B** | 75544 | 无 thinking 字段 |
| **GPT-OSS-20B** | 75545 | 无 thinking 字段 |
| **Qwen3-235B-A22B** | 75541 | 支持 `thinkingBudget` 字段 |
| **XuanYuan-LLM-4.0** | 80012 | 无 thinking 字段 |
| **Claude Sonnet 4.6** | 80016 | 支持 `effort` 字段，无 topP |
| **Gemini 3.1 Pro** | 80002 | 无 thinking 字段 |

> ⚠️ 不同模型支持的 llmParam 字段有差异。`thinking` 字段并非所有模型都支持，不支持的模型不要生成此字段。`thinkingBudget`、`effort` 是模型特有字段，仅对应模型可用。
> 
> ⚠️ 默认推荐使用 **GLM-5.1**（modelType=80014），除非用户明确指定其他模型。
