---
name: coze-workflow-generator
description: "Generate workflow JSON for the 原力平台 that users can paste directly onto the canvas. Use this skill whenever the user wants to create, design, build, or generate a workflow, 原力平台工作流, or mentions automating workflow creation with JSON. Also trigger when users describe a data processing pipeline, an automation flow, or a multi-step AI agent logic that should be implemented as a 原力 workflow. Covers all node types: LLM, code, conditions, loops, batch processing, HTTP requests, database CRUD, knowledge base, plugins, and more."
---

# 原力工作流自动化生成

你的任务是根据用户的自然语言需求，生成可以直接粘贴到原力平台画布上的工作流 JSON 数据。

> **参考资料**：在设计工作流前，Read `references/workflow-knowledge.md` 获取各节点的详细能力描述、使用方法、注意事项和高频坑位。Read `references/node-templates.md` 获取每种节点的精确 JSON 模板。

---

## 平台级硬限制

| 限制项 | 数值 | 说明 |
|-------|------|------|
| 单工作流最大节点数 | 1000 | 包含容器内部子节点 |
| 单次运行最大执行次数 | 1000 | 循环迭代次数也计入 |
| 代码节点上限 | 50 个/工作流 | 包含容器内的代码节点 |
| Object 嵌套深度 | 最多 3 层 | 开始/结束节点的参数定义 |
| 循环次数范围 | 1~1000 | 超出被裁剪 |
| 批处理并行上限 | 10 | concurrentSize 最大值 |
| 批处理次数上限 | 200 | batchSize 最大值 |
| 意图分类上限 | 50 | 意图识别节点 |

---

## 节点选型决策树

### 编排控制

| 场景 | 推荐节点 | 说明 |
|------|---------|------|
| 条件分支（确定规则） | 选择器(8) | if-else 逻辑 |
| 条件分支（语义理解） | 意图识别(22) | 大模型意图分类 |
| 串行重复（依赖上轮结果） | 循环(21) | 有状态迭代 |
| 并行批量（同构任务） | 批处理(28) | 无状态并行 |
| 多分支结果收口 | 变量聚合(32) | 取第一个非空值 |
| 调用可复用子流程 | 工作流调用(9) | 子工作流版本需手动同步 |

### 能力调用

| 场景 | 推荐节点 | 说明 |
|------|---------|------|
| 文本理解/生成/改写/抽取 | 大模型(3) | 必须配好 Prompt |
| 确定性外部 API 调用 | 插件(4) | 已知插件直接填 ID |
| 获取当前时间 | 插件(4)-时间类工具包 | **禁止让 LLM 输出时间**；涉及新闻/最新知识/时间筛选等时效性场景必须前置此插件 |
| 数据加工/类型转换/计算 | 代码(5) | Python，网络库可用 |
| 调外部 HTTP 接口 | HTTP请求(45) | 全方法+鉴权 |
| 从知识库检索信息 | 知识库检索(6) | 语义/全文/混合 |
| 飞书电子表格/多维表格操作 | 插件(4)-飞书系列 | pluginID=17(电子表格)/16(多维表格)/20(知识库)，token 参数支持传 URL |
| 飞书消息/任务/文档/日历 | 插件(4)-飞书系列 | pluginID=15(消息)/18(任务)/19(云文档)/21(日历)/14(认证) |
| 标准数据库 CRUD | 查询(43)/新增(46)/更新(42)/删除(44) | 图形化配置 |
| 复杂 SQL | SQL自定义(12) | SQL92 语法 |

### 交互与数据转换

| 场景 | 推荐节点 |
|------|---------|
| 运行中补采信息 | 输入(30) |
| 对话式收集信息 | 问答(18) | **仅限 Agent 模式，工作流中不可用** |
| 轻量字符串拼接/分割 | 文本处理(15) |
| Object/Array 转 JSON 字符串 | JSON序列化(58) |
| 写入知识库 | 知识库写入(27)（异步） |
| 持久化状态/跨轮记忆 | 变量赋值(40) |

### 关键选型原则

1. **循环 vs 批处理**：需要上一轮结果 → 循环；各元素独立处理 → 批处理
2. **选择器 vs 意图识别**：规则明确 → 选择器；需语义理解 → 意图识别
3. **多分支后必须用变量聚合收口**：未执行分支的变量是空值，直接接结束节点会出问题
4. **容器节点不支持嵌套**：循环内不能再放循环/批处理

---

## 核心规则（生成时必须遵守）

以下规则按类别组织，**每条都必须遵守**，违反任何一条都可能导致工作流粘贴失败或运行异常。

### Object-First 原则（最高优先级设计约束）

> **在工作流全链路中，结构化数据始终以 object/list[object] 格式传递，只有在"写入数据库 String 字段"或"拼入 LLM Prompt 文本"这两个边界场景时才做 json.dumps 序列化。**

**决策流程**：
1. 数据是结构化的（dict / list[dict]）？ → 用 `object` / `list[object]`
2. 数据是纯文本、URL、ID 等标量？ → 用 `string`
3. 只有写入数据库 String 字段 或 拼入 LLM prompt 时，才允许 json.dumps

**禁止反模式**：
```python
# ❌ 禁止：对 dict 做 json.dumps 再传递
item = json.dumps({'name': name, 'score': score})
items.append(item)  # list[string] — 错误！
```

**正确做法**：
```python
# ✅ 直接传 dict
items.append({'name': name, 'score': score})  # list[object]
```

**下游代码节点接收 object 时**：
```python
# ✅ 直接使用，添加 string fallback 增强健壮性
item = params.get('item_obj', {})
if isinstance(item, str):
    item = json.loads(item)
```

**结束节点必须保留 object 格式**：当输出包含结构化数据时，结束节点变量**必须**使用 `object` 类型（最多嵌套 3 层），直接传递 dict 给结束节点，**禁止**将 object 转义展开为 string 再输出。下游消费者可以直接解析字段，无需 json.loads。

### 节点结构规则

1. **每个节点必须包含 `_temp` 字段**：缺少此字段粘贴无反应。`_temp` 包含 `bounds` 和 `externalData`
2. **容器节点(21/28)的 `blocks`/`edges` 在节点顶层**：与 `data`/`meta`/`_temp` 同级，**不在 `data` 内部**
3. **循环端口 `loop-function-inline-output/input`，批处理端口 `batch-function-inline-output/input`**
4. **容器内部连线放在容器自身的 `edges` 数组中**，不放在顶层 `json.edges`
5. **type=13（输出节点）已废弃，不要使用**
5b. **容器节点(21/28)的 outputs 结构不同于普通节点（致命级）**：普通节点 outputs 是扁平 `{type, name}`，**容器节点 outputs 必须用 `{name, input:{type, schema, value}}` 包装结构**。同理，`concurrentSize`/`batchSize`/`loopCount` 等参数必须用 typed value 结构 `{type:"integer", value:{type:"literal", content:"10"}}`，**禁止写裸数值**

### 变量与类型规则

6. **变量类型全链路一致**：上游 outputs 声明的 type/schema → ref 引用的 rawMeta.type → 下游 inputParameters 的 type，三者必须完全匹配。**rawMeta.type 必须精确匹配变量类型**（标量：1=string, 2=integer, 3=boolean, 4=float, 6=object；列表：99=list[string], 100=list[integer], 101=list[boolean], 102=list[float], 103=list[object]），详见「rawMeta.type 完整映射表」
7. **循环/批处理 input schema.type 必须与上游 list 的 schema.type 一致**：上游 `list[string]` 则填 `"string"`，`list[object]` 则填 `"object"`
8. **代码返回值类型、outputs 声明、下游 input schema 四者必须完全一致**（含代码实际 Python 类型）
9. **ref 引用不留空**：所有 `"type": "ref"` 的 `content.blockID` 和 `content.name` 必须填实际值
10. **使用丰富的变量类型**：不要全部用 string，分数用 integer，标记用 boolean，列表用 list，结构化数据用 object
11. **object/list[object] 输出必须显式定义子变量 schema**：当节点输出类型为 `object` 或 `list`+`schema.type:"object"` 时，**必须**在 `schema` 中列出所有子字段的 `name` 和 `type`，否则下游节点无法通过 `变量名.key` 引用子字段。示例：
    ```json
    {"type": "list", "name": "items", "schema": {"type": "object", "schema": [
      {"type": "string", "name": "title"},
      {"type": "integer", "name": "score"}
    ]}}
    {"type": "object", "name": "result", "schema": [
      {"type": "string", "name": "summary"},
      {"type": "boolean", "name": "is_valid"}
    ]}
    ```
    > ⚠️ **常见踩坑**：只写 `"schema": {"type": "object"}` 而不展开子字段，粘贴后下游引用 `result.summary` 会报错。默认对所有 object 类型输出都配齐子变量。

### LLM 节点规则

12. **模型标识三件套（致命级）**：`modleName`（⚠️ 注意拼写，不是 `modelName`，平台历史规范）+ `modelType` + `generationDiversity` 三个字段**缺一不可**，否则模型选择失败、节点无法运行
13. **禁止生成 `frequencyPenalty` 和 `presencePenalty`**：平台不支持这两个字段
14. **必须包含 `thinking` 字段**：`0`=关闭，`1`=开启思考模式（复杂推理任务）
15. **prompt 和 systemPrompt 必须用 `literal` 类型，禁止用 `ref`**。引用其他节点输出：先在 `inputParameters` 中 ref 声明变量，再在 prompt literal 中用 `{{变量名}}` 插值
16. **responseFormat 只有 3 个值**：`"0"`=文本, `"1"`=Markdown, `"2"`=JSON。**优先用 `"2"`**。不存在 3 或 4
16b. **JSON 多输出模式(responseFormat=2)**：outputs 中每个变量名必须与 Prompt 中 JSON 字段名一致；Prompt 末尾必须包含 `# Output Format (JSON Only)` 段落；不需后接代码节点做 JSON 解析
17. **LLM timeoutMs 设为 180000~600000**（3~10分钟），过短容易超时
18. **任何时效性场景必须前置获取当前时间**：工作流涉及新闻检索、最新知识查询、时间范围筛选、日期计算、"最近/今天/本周"等时间相关行为时，**必须**在流程前端使用「时间类工具包」插件(pluginID: `7615195917427146752`, apiName: `get_current_time`)获取真实当前时间，将时间结果传给下游节点使用。**绝对禁止**依赖 LLM 自行判断或生成当前时间——LLM 的训练数据有截止日期，输出的时间必定不准确
19. **LLM 节点 `data` 层必须包含 `"version": "3"`**

#### generationDiversity 四种预设模式

| 模式值 | 含义 | temperature | thinking | 适用场景 |
|--------|------|-------------|----------|---------|
| `"precise"` | 精确模式 | 0.3 | 0(关闭) | 分类/判断/结构化输出 |
| `"balance"` | 均衡模式 | 0.8 | 0(关闭) | 通用问答/常规分析 |
| `"creative"` | 创意模式 | 1.0 | 0(关闭) | 创意写作/头脑风暴 |
| `"default_val"` | 自定义 | 手动设置 | 手动设置 | 需精确控制参数时 |

> 四种预设模式默认都**不开启深度思考**（thinking=0）。如需开启，请使用 `"default_val"` 模式并手动设置 `thinking=1`。

20. **LLM 节点插件调用（仅 DeepSeek-V3.2 和 GLM-5.1 支持）**：通过 `inputs.fcParam.pluginFCParam.pluginList` 配置插件列表，同时必须在 `_temp.externalData.skills` 中镜像（含 type:1/pluginName/icon）。完整可用插件列表（78个，含搜索/OCR/语音/时间/创作/数据查询/飞书集成等8大类）见 `references/plugin-catalog.md`

### 意图识别节点规则（与 LLM 节点有重大差异！）

21. **意图识别(type=22)的 `llmParam` 是 object**，不是 array。且模型字段用 **`modelName`**（标准拼写），不是 `modleName`。详见 node-templates.md

### HTTP 节点规则

22. **HTTP 节点的 inputParameters 与 LLM/代码节点完全不同**：HTTP 的 `inputParameters` 位于 `data.inputParameters`（与 `inputs` 平级），**不是** `data.inputs.inputParameters`。且 HTTP 的 inputParameters **仅为 headers/params 的 ref 提供来源**，**不用于** url/json/rawText 的变量插值。url/json/rawText 中直接写 `{{block_output_节点ID.变量名}}` 引用上游输出，**不需要先在 inputParameters 中声明变量**。这是 HTTP 节点与 LLM/代码节点最容易搞混的致命差异！
23. **变量引用两种方式不能混用**：`{{block_output_ID.name}}` 插值**仅限** `url`/`json`/`rawText`；`headers`/`params`/`formURLEncoded`/`formData` 等结构化字段**必须用 ref 对象**（`{"type":"ref","content":{"source":"block-output","blockID":"ID","name":"name"}}`）。literal 的 content 中**不能使用 `{{}}` 插值**
24. **bodyType 只有 6 种**：`JSON`/`FORM_DATA`/`FORM_URLENCODED`/`RAW_TEXT`/`BINARY`/`EMPTY`（不存在 `RAW` 或 `X_WWW_FORM_URLENCODED`）。bodyData 中的字段按 bodyType **互斥**——选 `RAW_TEXT` 时 bodyData 只放 `rawText`，不能同时有 `json`/`binary` 等

### 代码节点规则

25. **`language` 必须为 `3`**，不能是 `"codeLanguage": "python3"`
26. **网络库可用但推荐用 HTTP 节点**：代码节点实际可 import requests/aiohttp/httpx 等网络库，但**建议仍优先使用 HTTP 请求节点(type=45)**，因为 HTTP 节点支持 GUI 配置鉴权、重试、超时等，更易维护。仅在 HTTP 节点无法满足需求时才在代码中使用网络库
27. **代码函数签名**：`async def main(args: Args) -> Output:`，通过 `args.params["变量名"]` 获取输入
28. **批处理/循环内部 item 类型是元素类型，不是 list**：当容器输入是 `list[object]` 时，内部每次迭代收到的 item 类型是 `object`，不再是 `list`。内部节点的 inputParameters 必须声明为元素类型（如 `"type": "object"`），不能声明为 `"type": "list"`
29. **f-string 中禁止使用反斜杠**：Python f-string 的 `{}` 表达式部分不允许包含反斜杠 `\`，否则报 SyntaxError。必须先将含反斜杠的值赋给变量，再在 f-string 中引用该变量
    ```python
    # ❌ 报错：f-string expression part cannot include a backslash
    lines.append(f'  分析: {r.get("reasoning", "无")}')

    # ✅ 正确：先提取变量再格式化
    reasoning = r.get("reasoning", "无")
    lines.append(f'  分析: {reasoning}')
    ```
30. **代码中的中文必须保留原文**：禁止将中文写成 unicode 编码（如 `\u5206\u6790`），必须直接写中文字符（如 `分析`）

### 循环节点规则

31. **设置变量(type=20)使用 `left/right` 赋值结构**：不是 `name/input` 结构！`left` → ref 到循环容器的 variableParameter（`blockID=容器ID, name=变量名`），`right` → ref 到内部节点输出（`blockID=内部节点ID, name=输出变量名`）。left/right 的 `type` 和 `rawMeta` 必须一致
32. **循环 count 模式内置 `index` 变量**：自动提供迭代索引（从 0 开始），**无需在 variableParameters 中声明**。引用方式：`blockID=容器ID, name="index"`, type=integer, rawMeta.type=2
33. **count 模式 outputs 为 list**：count 模式循环的 output 类型声明为 `type="list"`，`schema.type` 匹配内部节点输出元素类型。每轮迭代输出自动收集成列表
34. **object 子字段 dot notation 引用三前提**：(1) 上游 outputs 的 object 必须有显式 schema 声明子字段 (2) variableParameters 的 schema 与上游完全一致 (3) 子字段引用的 type/rawMeta 匹配子字段类型，不是父 object 类型。**全链路 schema 一致性**：上游 outputs.schema ═ variableParameters.schema ═ 内部节点引用

### 批处理节点规则

35. **批处理输出是"多列并行 list"，不是"一个 object list"（致命级）**：批处理节点的每个输出变量独立收集内部子节点该字段在每次迭代中的值，组成一个 list。需要几个字段就声明几个输出变量（建议用 `{原字段名}_list` 后缀），下游按 index 对齐还原。**绝不是**一个 `list[object]`
36. **输出变量逐个声明，一一映射内部节点输出字段**：内部 LLM 节点有 N 个业务输出，批处理节点就要声明 N 个输出变量，每个 output 的 `value` ref 到内部节点对应字段，外层 `type="list"`, `schema.type` 匹配元素类型
37. **输出声明中 rawMeta.type 对应元素原始类型**（string→1, integer→2），因为它引用的是内部节点的单个输出；**下游节点引用批处理输出时** rawMeta.type 对应 list 类型（list[string]→99, list[integer]→100, list[float]→102, list[object]→103）
38. **下游代码必须按"多个并行 list + index 对齐"解析**：接收多个独立 list 参数，用 `for i in range(len(...))` 按 index 对齐处理。**禁止**把批处理输出当 `list[object]` 遍历（运行时每个元素是标量，不是 dict）
39. **不需要输出 `reasoning_content`**：LLM 思考过程日志通常不需传递给下游，批处理输出中省略以减少数据传输量

### 数据库规则

40. **spaceId 规则**：工作流包含插件节点(4)、数据库节点(12/42/43/44/46)或知识库节点(6/27)时，顶层 `source.spaceId` **必须填写用户提供的真实 spaceId**。**禁止使用占位符、空字符串或虚构值**——必须在 Phase 1 先向用户索要，拿到真实值后才能生成 JSON，否则粘贴时节点会被丢弃
41. **资源引用列表**：`databaseInfoList` 默认写空数组 `[]`，用户粘贴后 GUI 手动选择。**但若用户明确提供了 `databaseInfoID`（表ID），则直接填入** `[{"databaseInfoID": "用户提供的表ID"}]`，无需用户再手动选择。`datasetList` 同理
42. **简单 CRUD 优先图形化节点**(43/46/42/44)，复杂 SQL(JOIN/子查询/聚合)才用 SQL 自定义(12)。**非必要不用 SQL 自定义节点**，图形化节点可读性更强且配置错误率更低
43. **SQL 自定义变量只引用 inputParameters**：SQL 中 `{{变量名}}` 只能引用本节点 `inputParameters` 中声明的变量，不能直接 `{{block_output_ID.name}}`
44. **SQL INSERT 必须包含 uuid 列**：`INSERT INTO t (uuid, col1) VALUES (UUID(), 'val1')`，否则报列数不匹配错误
45. **平台数据库仅 5 种字段类型**：`String`/`Integer`/`Number`/`Boolean`/`Time`。无 float/text/varchar/datetime
46. **数据库表有 3 个系统默认字段**：`id`(Integer主键)、`uuid`(String)、`bstudio_create_time`(Time)，自定义字段无法设唯一键
47. **查询数据(43)和 SQL 自定义(12)的 `rowNum` 始终为 null — 禁止用于判断**：这两种节点执行后只有 `outputList` 包含实际数据，`rowNum` 默认就是 null。下游如需判断"是否查询到数据"，**直接用选择器(8)判断 `outputList` 不为空(operator=10)或为空(operator=9)**即可，无需额外代码节点。**绝对禁止**用 `rowNum > 0` 或 `rowNum == 0` 做条件分支。**但更新(42)/新增(46)/删除(44)节点的 `rowNum` 正常可用**，能返回真实影响行数，可直接用于选择器分支判断
48. **databaseInfoList 格式**：只接受 `[{"databaseInfoID": "表ID"}]` 格式，**禁止**写成 `[{"tableID":"...", "fields":[...]}]` 等自造格式
49. **fieldID 是数字字符串**：新增(46)/更新(42)节点的 `fieldInfo` 中 `fieldID` 值是字段在数据库中的编号（`"1"`, `"2"`, `"3"`...），**不是字段名字符串**（如 `"proc_cmd_pattern"`）。生成时如不确定编号可用占位符 `"{{FIELD_ID_N}}"`。**编号依赖建表时字段创建顺序**：`"1"` = 第 1 个自定义字段，`"2"` = 第 2 个，以此类推。Phase 4 建表建议的字段顺序必须与 JSON 中 fieldID 的对应关系一致。**若字段顺序不确定或不可控，改用 SQL 自定义节点(12)通过字段名操作，避免 fieldID 编号问题**
50. **数据库节点变量与目标字段必须一一对应**：`fieldInfo` 中每个 `fieldID`/`fieldValue` 对必须与数据库表的实际字段编号精确对应，`conditionList` 中的 `left` 字段名必须与数据库表中实际字段名一致。**禁止乱填、混用或遗漏字段**

### 知识库规则

51. **知识库检索(type=6)参数名固定 `"Query"`（大写 Q）**：`inputParameters` 唯一参数名必须是 `"Query"`，不可自定义
52. **知识库检索(type=6) datasetParam 不预设具体值**：`topK`/`useRerank`/`useRewrite`/`isPersonalOnly` 的 value 只写 `{"type":"literal"}`，不要预设 `content` 值，由用户在 GUI 配置
53. **知识库检索(type=6)固定输出结构**：outputs 固定为 `outputList: list[object]`，schema 固定为 `[{output: string}, {documentId: string}]`，不可自定义
54. **知识库写入(type=27)无自定义输入参数**：`inputParameters` 固定为空数组 `[]`，节点只接受 Doc/File 类型输入（GUI 配置），不能通过 inputParameters 传 string
55. **知识库写入(type=27) strategyParam 必须含三个策略**：`parsingStrategy`(含 parsingType)、`chunkStrategy`(含 chunkType)、`indexStrategy`，缺少任一导致写入异常
56. **知识库写入(type=27)仅支持文本类型知识库**：`datasetList` 中只能放一个知识库 ID，且必须是文本类型

### 选择器/聚合规则

57. **选择器条件 left/right 结构对称**，都有 `{"input":{...}}` 包装层；一元操作符(9/10/11/12)无 right；operator 范围 1~16
58. **选择器始终使用 `branches` 数组**：无论单分支还是多分支，都用 `branches`（每个 branch 内含 `conditions` 数组）。详见 node-templates.md
59. **变量聚合 mergeGroups[].variables[] 不能为空**，必须有真实 blockID/name；outputs 不能空数组；组名≤20字符

### 连线规则

60. **每条 edge 必须包含 4 个字段**：`sourceNodeID`/`targetNodeID`/`sourcePortID`/`targetPortID`，普通连线端口为空字符串 `""`
61. **选择器端口命名**：单分支 sourcePortID 为 `"true"`(成立)/`"false"`(否则)；多分支：`"true"`(第1个) + `"true_1"`(第2个) + `"true_2"`(第3个) ... + `"false"`(否则)。**不是** `"branch-0"`/`"branch-1"`
62. **禁止 edge 回环**：重复执行用循环/批处理容器
63. **processType=3 异常端口**：sourcePortID = `"branch_error"`，连到异常处理节点
64. **开始/结束节点连线**：画布上的开始节点 NodeID 固定为 `"100001"`，结束节点 NodeID 固定为 `"900001"`。生成 edges 时**必须包含**：① 开始节点(100001) → 工作流第一个节点的连线；② 工作流最后一个节点 → 结束节点(900001) 的连线。这样粘贴后即可自动与画布上已有的开始/结束节点正确连接，无需用户手动拉线

### 其他规则

65. **多分支输出必须收口**：选择器/意图识别后需统一使用结果时，必须先接变量聚合节点
66. **知识库写入是异步的**：写完立即检索可能检索不到
67. **Array 类型参数不要用固定值**：直接填固定值会被当成 String，应引用上游或用代码构造
68. **过程数据写库不输出**：中间分析过程、原始数据应写数据库存档，不作为最终输出

---

## 异常处理配置

大多数执行类节点支持 `settingOnError`。详细模板见 `references/node-templates.md` 异常处理章节。

| processType | 含义 | 适用场景 |
|---|---|---|
| `1` | 中断流程 | 默认值，节点失败立即停止 |
| `2` | 返回设定内容 | 失败后继续走下游 |
| `3` | 执行异常流程 | 失败后跳转异常分支 |

### processType=2 必须满足的 3 项（缺一不可，最常遗漏！）

1. ✅ `settingOnError` 包含 `"switch": true`
2. ✅ `settingOnError` 包含 `"dataOnErr": "{ JSON字符串 }"`，key 与 outputs 业务变量名对应
3. ✅ `outputs` 末尾追加 `errorBody`(object, 含 errorMessage/errorCode schema, readonly) 和 `isSuccess`(boolean, readonly)

**LLM 节点额外要求**：
- `dataOnErr` 必须包含 `reasoning_content`（LLM 固有输出）
- `retryTimes >= 1` 时必须配置 `settingOnError.ext.backupLLmParam`（JSON 字符串，内部模型字段同样是 **`modleName`** 不是 `modelName`）

---

## 工作流程

### Phase 1: 需求分析

识别核心业务逻辑、数据流向、分支判断、外部资源依赖、交互需求。

> **⚠️ 每次生成工作流前，必须先 Read `references/node-templates.md`**，确保对每种用到的节点类型的完整 JSON 结构有准确参照。特别注意容器节点(21/28)的 outputs 包装结构与普通节点不同。同时 Read `references/workflow-knowledge.md` 了解平台能力边界。

向用户确认需求理解，包括节点类型、连接关系、需要手动配置的参数。

**⚠️ 若涉及插件(4)、数据库(12/42/43/44/46)或知识库(6/27)节点，必须向用户获取 `spaceId`**。用户可直接粘贴原力平台工作空间的 URL（从中提取 `space/` 后的数字串即为 spaceId）。

**🚫 阻断规则：在用户提供 spaceId 之前，禁止进入 Phase 3 生成 JSON。** 应在 Phase 1 明确告知用户需要 spaceId 并说明获取方式（打开原力平台 → 进入对应空间 → 粘贴浏览器地址栏 URL，如 `https://ai-force.duxiaoman-int.com/space/7563588980457865216/...`，其中 `space/` 后的数字串即为 spaceId），然后等待用户回复后再继续。

**⚠️ 若涉及数据库操作，必须明确表结构**（字段名、字段类型仅从 String/Integer/Number/Boolean/Time 中选）。默认使用平台图形化数据库。**若用户能提供 `databaseInfoID`（表ID），可直接填入 JSON 的 `databaseInfoList` 中**，省去用户粘贴后手动选表的步骤。

**⚠️ 时效性场景识别**：若需求涉及新闻检索、最新资讯、实时数据、时间范围筛选、"最近/今天/本周/本月"等时间相关行为，**必须在架构中前置「时间类工具包」插件节点**获取真实当前时间，禁止让 LLM 自行输出时间。

### Phase 2: 工作流架构设计

根据「节点选型决策树」选择节点，用 ASCII 描述架构：

```
开始 → 代码处理 → 选择器 → [成立] → 大模型 → 结束
                         → [否则] → HTTP请求 → 结束
```

**选型注意**：多分支后统一输出必须先接变量聚合；容器不嵌套。

### Phase 3: 生成 JSON

**前置检查**：如果工作流包含插件(4)、数据库(12/42/43/44/46)或知识库(6/27)节点，确认用户已提供真实 spaceId。若未提供，**立即停止并向用户索要**，拿到后再继续生成。绝不使用占位符或空字符串代替 spaceId。

生成完整的 `coze-workflow-clipboard-data` JSON，**必须遵守上文「核心规则」全部条目**。

**⚠️ 生成每个节点时，必须先查阅 `references/node-templates.md` 中对应节点类型的完整模板**，严格复制模板的字段结构（尤其注意容器节点 outputs 的 `{name, input:{...}}` 包装、typed value 参数结构），禁止凭记忆生成参数格式。**生成插件节点时，必须查阅 `references/plugin-catalog.md`** 获取准确的 pluginID/apiID/输入输出参数。

**格式要求**：
1. 将 JSON 写入文件（如 `workflow.json`）
2. 输出**紧凑单行 JSON**：`json.dumps(data, ensure_ascii=False, separators=(',', ':'))`
3. 节点 ID 用 6 位随机数字字符串，互不重复
4. 节点位置 x 轴间距 450px，分支 y 轴错开 200px

### Phase 3.5: 生成后强制自检（必须执行！）

JSON 生成后、输出给用户前，**必须逐项检查**以下内容，发现问题立即修正：

#### 自检项1: 变量类型链路一致性 + rawMeta 精确匹配
逐个检查每条变量传递链路：上游 output type → ref rawMeta.type → 下游 input type，三者完全匹配。**rawMeta.type 必须按映射表精确填写**：string=1, integer=2, boolean=3, float=4, object=**6**(非1), list[string]=**99**(非103), list[integer]=100, list[object]=103。

#### 自检项2: 循环/批处理 schema + Object-First 验证
**对工作流中每个循环(21)/批处理(28)节点**：
- `inputParameters[].input.schema.type` 必须与上游 list 变量的 `schema.type` 完全相同
- `outputs[].input.schema.type` 必须与内部最后节点的输出变量类型一致
- **内部节点接收的 item 类型是元素类型**：输入 `list[object]` → 内部 item 是 `object`，不是 `list`

**对每个代码节点(type=5)的 list 类型输出，执行 3 步交叉验证**：
1. **查看代码构建方式**：`items.append(dict)` → object；`items.append(json.dumps(dict))` → ❌ 违反 Object-First，必须改为直接 append dict；`items.append(str)` → string（仅限纯文本）
2. **检查 outputs 声明**：实际 object → schema.type 必须 `"object"`；实际 string → 必须 `"string"`
3. **检查下游 input schema**：与 Step 2 一致；下游代码不应有多余的 json.loads

#### 自检项3: 代码节点 `"language": 3`
不能是 `"codeLanguage": "python3"`。

#### 自检项3.5: object 输出子变量 schema 完整性
逐个检查所有 `type:"object"` 或 `type:"list"` + `schema.type:"object"` 的输出变量，确认 `schema` 中已列出全部子字段的 `name` 和 `type`。**禁止**只写 `"schema":{"type":"object"}` 而不展开子字段——这会导致下游引用 `变量名.key` 失败。

#### 自检项4: LLM 一致性
- prompt/systemPrompt 值类型是 `"literal"`
- responseFormat content 值只有 `"0"`/`"1"`/`"2"`
- responseFormat=2 时 outputs 变量名与 Prompt JSON 字段名一致
- **模型三件套完整**：`modleName`（⚠️ 不是 `modelName`）+ `modelType` + `generationDiversity` 全部存在
- **不含 `frequencyPenalty`/`presencePenalty`**
- **包含 `thinking` 字段**
- **`data` 层包含 `"version": "3"`**

#### 自检项5: 容器节点结构
- `blocks`/`edges` 在节点顶层，不在 `data` 内部
- **outputs 使用 `{name, input:{type, schema, value}}` 包装结构**（不是普通节点的扁平 `{type, name}`）
- **`concurrentSize`/`batchSize`/`loopCount` 是 typed value 对象**（不是裸数值）：`{"type":"integer","value":{"type":"literal","content":"10"}}`
- 批处理每个业务输出字段各自独立声明为一个 list 输出变量

#### 自检项6: ref 引用完整性
所有 `"type": "ref"` 的 `blockID` 和 `name` 都不为空。重点排查选择器条件 left、变量聚合 variables、所有 inputParameters。

#### 自检项7: 选择器条件结构
left/right 对称有 `{"input":{...}}`；一元操作符(9/10/11/12)无 right；二元必须有 right；operator 1~16。

#### 自检项8: 变量聚合完整性
variables 不为空且 ref 有真实 blockID/name；outputs 不为空数组；mergeGroups.name = outputs.name。

#### 自检项9: processType=2 完整性
逐个检查：switch:true + dataOnErr + errorBody(含 errorMessage/errorCode schema)/isSuccess outputs。LLM 节点额外检查 reasoning_content、backupLLmParam（内部用 `modleName` 非 `modelName`）。

#### 自检项10: 代码节点代码质量
- **f-string 中无反斜杠**：`{}` 表达式部分不能含 `\`（含转义引号 `\"`），必须先赋值给变量再引用
- **中文保留原文**：不使用 `\uXXXX` unicode 编码，直接写中文字符
- **批处理内部 item 类型正确**：接收 `list[object]` 的容器，内部代码用 `object` 接收 item，不是 `list`

#### 自检项10b: 批处理输出结构
- **输出是"多列并行 list"**：每个业务字段对应一个独立的 `list` 输出变量，不是一个 `list[object]`
- **输出变量数量 = 内部节点业务输出字段数**：每个需要传递给下游的字段都要单独声明
- **rawMeta 双层区分**：输出声明中 rawMeta 对应元素类型（string→1），下游引用时 rawMeta 对应 list 类型（list[string]→99）
- **下游代码按 index 对齐**：接收多个独立 list，用 `for i in range(len(...))` 遍历，不把批处理输出当 `list[object]` 遍历
- **不输出 reasoning_content**：批处理输出中省略 LLM 思考过程日志

#### 自检项11: HTTP 节点变量引用方式（致命级）
- **inputParameters 位置正确**：HTTP 节点的 inputParameters 在 `data.inputParameters`（与 `inputs` 平级），**不是** `data.inputs.inputParameters`
- **url/json/rawText 使用 `{{block_output_节点ID.变量名}}` 直接引用上游**，不需要在 inputParameters 中声明变量，不使用 `{{varName}}` 格式
- **headers/params/formURLEncoded/formData 必须用 ref 对象**，不能用 literal+`{{}}` 插值
- **bodyData 字段按 bodyType 互斥**：RAW_TEXT 只有 rawText，JSON 只有 json，不能混搭

#### 自检项12: 资源类节点 spaceId + databaseInfoList 格式
包含插件/数据库/知识库节点时，source.spaceId 已填真实值。databaseInfoList 格式必须为 `[{"databaseInfoID": "..."}]` 或空数组 `[]`（禁止自造格式如 `{"tableID":"...", "fields":[...]}`）。若用户提供了表ID则预填，否则写空数组。datasetList 同理。

#### 自检项13: SQL 自定义变量引用
SQL 中 `{{变量名}}` 只引用 inputParameters 中声明的变量。INSERT 包含 uuid 列。

#### 自检项13b: 查询/SQL自定义 rowNum 陷阱
若工作流包含查询数据节点(43)或 SQL 自定义节点(12)且下游有分支判断"是否有数据"，确认**没有**使用 `rowNum` 做条件（这两种节点的 rowNum 始终为 null）。正确做法：用选择器(8)直接判断 `outputList` 不为空(operator=10)或为空(operator=9)。注意：更新(42)/新增(46)/删除(44)节点的 `rowNum` 正常可用，无需此变通。

#### 自检项13c: 数据库节点变量与字段一一对应
逐个检查所有数据库节点(42/43/44/46)：① `fieldInfo` 中每个 `[fieldID, fieldValue]` 对的 `fieldID` 值必须是数字字符串（如 `"1"`, `"2"`），不能是字段名字符串；② `conditionList` 中的 `left` 字段名必须与数据库表中实际存在的字段名一致；③ `fieldValue` 的 ref 引用（blockID/name）必须指向正确的上游输出变量，类型匹配；④ 若用户提供了 `databaseInfoID`，确认 `databaseInfoList` 已正确填入 `[{"databaseInfoID":"..."}]`。

#### 自检项14: 时效性场景前置时间获取
工作流涉及新闻/最新知识/时间筛选/日期计算时，确认已有「时间类工具包」插件节点(type=4)获取当前时间，且时间结果传递给了下游需要时间信息的节点。LLM 节点的 prompt 中不自行生成当前日期。

#### 自检项14b: 连线格式完整性
每条 edge 4 个字段齐全；sourceNodeID/targetNodeID 与 nodes 中 id 匹配；选择器端口 true/false（非 0/1）；容器内部连线在容器 edges 中。

#### 自检项15: externalData.title = subTitle
检查所有节点的 `_temp.externalData.title` 是否填的 `nodeMeta.subTitle`（节点类型名如"大模型"、"代码"、"选择器"），**不是**用户自定义的 title。

#### 自检项16: 意图识别节点差异
如有意图识别(type=22)节点：`llmParam` 是 object（不是 array）、模型字段用 `modelName`（不是 `modleName`）。

#### 自检项17: 选择器 branches 结构 + 端口命名
选择器**始终**使用 `branches` 数组（无论单分支还是多分支）。端口名：单分支 `"true"`/`"false"`；多分支 `"true"` + `"true_1"` + `"true_2"` ... + `"false"`。**不是** `"branch-0"`/`"branch-1"`。

#### 自检项18: processType=3 异常端口
如有 processType=3 的节点，检查是否有 `sourcePortID="branch_error"` 的连线到异常处理节点。

#### 自检项19: 设置变量(type=20) left/right 结构
如有设置变量节点，检查 `inputParameters` 使用的是 `left/right` 赋值对（不是 `name/input`）。left ref 到循环容器的 variableParameter，right ref 到内部节点输出。left/right 的 type 和 rawMeta 一致。

#### 自检项20: 知识库检索参数名
如有知识库检索(type=6)节点，检查 `inputParameters` 参数名是 `"Query"`（大写 Q），不是 `"query"` 等。outputs 是固定的 `outputList`。datasetParam 中 topK 等无 content 值。

#### 自检项21: 知识库写入完整性
如有知识库写入(type=27)节点，检查：`inputParameters` 为空数组；`strategyParam` 含三个策略（parsingStrategy + chunkStrategy + indexStrategy）；`datasetList` 只放一个文本类型知识库。

#### 自检项22: 循环全链路 schema 一致性
如有循环(type=21)且使用 variableParameters，检查：上游 outputs.schema ═ variableParameters.schema ═ 内部节点引用的 type/rawMeta。不能给 string 类型源强套 object schema。

如果自检发现任何问题，必须先修正 JSON 再输出。

#### Phase 3.5b: 脚本辅助自检（在人工自检之后执行）

完成上述人工逐项自检后，**再用自动化脚本做二次校验**。脚本覆盖了 rawMeta 映射、LLM 字段完整性、容器结构、连线格式等 22 项可程序化检查，能捕捉人工检查容易遗漏的细节错误。

**执行方式**（将上面已写入文件的 JSON 路径传给脚本）：

```bash
python scripts/coze_workflow_validator.py workflow.json
```

> 这里 `scripts/coze_workflow_validator.py` 是本 skill 自带的自检脚本（位于 `scripts/` 目录下）。运行时使用本 skill 目录下的相对路径，如 `python <skill-base-dir>/scripts/coze_workflow_validator.py workflow.json`。

**处理脚本结果**：
- 若脚本输出 **FAIL** 项：逐条核实并修正 JSON（修正后可重新运行脚本确认）
- 若脚本输出 **WARN** 项：根据提示信息判断是否需要调整
- 若脚本全部 **PASS**：确认无结构性问题，继续 Phase 4

**⚠️ 容错规则**：脚本辅助自检是对人工自检的补充增强，**不是替代**。如果脚本运行报错（如 Python 环境异常、脚本文件缺失、解析失败等任何异常），**不影响流程继续**——只要上面的人工逐项自检已完成并修正了发现的问题，即可正常进入 Phase 4。遇到脚本异常时简要提示用户"自动化辅助校验未成功执行，已通过人工自检确认"即可。

### Phase 4: 输出工作流设计说明与用户配置清单（强制执行！）

> **🚫 Phase 4 不可跳过！** JSON 输出后必须紧接着输出以下全部内容。Phase 4 是用户理解和配置工作流的唯一指引，缺少会导致用户无法正确使用。即使 JSON 很长，也**必须**在同一次回复中完成 Phase 4 的全部输出。

#### 4.1 工作流架构总览

用 ASCII 流程图展示完整的节点拓扑、ID 和关键变量。

#### 4.2 开始节点变量配置

列出需要在开始节点配置的输入变量（类型、说明、默认值）。根据数据特征选合适类型（string/integer/boolean/number/object/array/file）。

#### 4.3 结束节点变量配置

**输出设计原则**：
- 输出变量**不宜太多太复杂**，突出重点结论和可读性
- **详细过程数据写库不输出**
- 研判/分析/审核类聚焦：**结论 + 判断 + 分数 + 建议 + 摘要**
- 保留多个独立类型变量（不合并为单个 string）
- 结构化数据优先用 object 类型输出

| 变量名 | 类型 | 来源节点 → 输出变量 | 说明 |
|--------|------|-------------------|------|
| `conclusion` | string | "风险研判"(601005) → conclusion | 核心结论 |
| `is_risky` | boolean | "风险研判"(601005) → is_risky | 是否有风险 |
| `risk_level` | integer | "风险研判"(601005) → risk_level | 风险等级(1-5) |

#### 4.4 连线说明

生成的 JSON 已包含开始节点(100001)和结束节点(900001)的连线，粘贴后会自动与画布上的开始/结束节点连接。如有特殊分支或手动调整需求，用户可在画布上自行修改连线。

#### 4.5 外部资源配置

列出需手动配置的数据库表、知识库、插件、子工作流等。

**若涉及数据库操作，必须给出建议的表结构**。只列自定义字段，类型从 String/Integer/Number/Boolean/Time 选。提醒系统自动包含 id/uuid/bstudio_create_time，自定义字段无唯一键需自行去重。**若数据库不允许重复数据（如白名单、唯一字段场景），必须在工作流中新增数据前先用查询数据节点(43)按目标字段查询，再用选择器(8)判断 outputList 不为空(operator=10)来分支——已存在则跳过，不存在才插入。**

#### 4.6 关键节点配置说明

对大模型/代码节点的核心配置做简要说明。

#### 4.7 设计思路与改进建议

简述设计思路，给出 2-3 条改进方向。

> **✅ Phase 4 完成检查**：确认 4.1~4.7 每一项都已输出。如有任何一项遗漏，立即补充。

---

## 节点类型速查表

| type | 名称 | 颜色 | 备注 |
|------|------|------|------|
| 3 | 大模型 | #5C62FF | modleName(非modelName)+modelType+generationDiversity 三件套 |
| 4 | 插件调用 | #CA61FF | 已知插件直接填 ID, 需 spaceId |
| 5 | 代码 | #00B2B2 | language:3, 网络库可用但推荐HTTP节点 |
| 6 | 知识库检索 | #FF811A | 需 spaceId |
| 8 | 选择器 | #00B2B2 | operator 1~16 |
| 9 | 工作流调用 | #00B83E | 需 workflowId |
| 12 | SQL自定义 | #FF811A | 需 spaceId, SQL变量只引用 inputParameters |
| ~~13~~ | ~~输出~~ | | **已废弃** |
| 15 | 文本处理 | #3071F2 | |
| 18 | 问答 | #3071F2 | **仅限 Agent 模式**，工作流中不可用 |
| 19 | 终止循环(Break) | #00B2B2 | **仅在循环(21)内部使用** |
| 20 | 设置变量(LoopSetVariable) | #00B2B2 | **仅在循环(21)内部使用**, 更新 variableParameters |
| 21 | 循环 | #00B2B2 | **容器节点**, 三模式: array/count/infinite |
| 22 | 意图识别 | #00B2B2 | 端口 "branch_0","branch_1"..."default" |
| 27 | 知识库写入 | #FF811A | 异步, 需 spaceId |
| 28 | 批处理 | #00B2B2 | **容器节点**, batch-前缀端口 |
| 29 | 继续循环(Continue) | #00B2B2 | **仅在循环(21)内部使用**, 跳到下一轮 |
| 30 | 输入 | #5C62FF | |
| 32 | 变量聚合 | #00B2B2 | 组名≤20字符 |
| 40 | 变量赋值 | #FF811A | |
| 42 | 更新数据 | #F2B600 | 需 spaceId |
| 43 | 查询数据 | #F2B600 | 需 spaceId |
| 44 | 删除数据 | #F2B600 | 需 spaceId |
| 45 | HTTP请求 | #3071F2 | 结构化字段用 ref |
| 46 | 新增数据 | #F2B600 | 需 spaceId |
| 58 | JSON序列化 | #F2B600 | |

> 完整 JSON 模板参见 `references/node-templates.md`。

---

## JSON 剪贴板数据格式

### 顶层结构

```json
{
  "type": "coze-workflow-clipboard-data",
  "source": {
    "workflowId": "",
    "flowMode": 0,
    "spaceId": "",
    "isDouyin": false,
    "host": "ai-force.duxiaoman-int.com"
  },
  "json": {
    "nodes": [ ... ],
    "edges": [ ... ]
  },
  "bounds": { "x": 0, "y": 0, "width": 1200, "height": 600 }
}
```

- `source.spaceId`：包含插件/数据库/知识库节点时必须填真实 spaceId，否则留空
- `bounds` 根据节点实际坐标范围计算

### 节点结构

每个节点必须包含 `id`(6位数字字符串)、`type`(字符串)、`meta.position`、`data.nodeMeta`、`data.inputs`、`data.outputs`、**`_temp`**。

#### `_temp` 字段（必填）

```json
"_temp": {
  "bounds": { "x": position_x, "y": position_y, "width": 360, "height": 见高度表 },
  "externalData": { "icon": "同nodeMeta.icon", "description": "同nodeMeta.description", "title": "同nodeMeta.subTitle（节点类型名，非用户自定义title）", "mainColor": "同nodeMeta.mainColor" }
}
```

> ⚠️ `externalData.title` 必须填 `nodeMeta.subTitle`（如"大模型"、"代码"、"选择器"），**不是**用户自定义的 `nodeMeta.title`。

节点高度对照表：
| type | 高度 | type | 高度 | type | 高度 |
|------|-------|------|-------|------|-------|
| 3 | 189.9 | 4 | 137.9 | 5 | 137.9 |
| 6 | 139.9 | 8 | 137.9 | 9 | 113.9 |
| 12 | 139.9 | 15 | 113.9 | 18 | 165.9 |
| 21 | 139.9 | 22 | 187.9 | 27 | 139.9 |
| 28 | 113.9 | 30 | 87.9 | 32 | 87.9 |
| 40 | 113.9 | 42 | 165.9 | 43 | 139.9 |
| 44 | 139.9 | 45 | 115.9 | 46 | 142.9 |
| 58 | 113.9 | 默认 | 113.9 | | |

### 数据引用机制

**字面量 (literal)**：
```json
{ "type": "string", "value": { "type": "literal", "content": "固定文本", "rawMeta": { "type": 1 } } }
```

**引用 (ref)**：
```json
{ "type": "string", "value": { "type": "ref", "content": { "source": "block-output", "blockID": "节点ID", "name": "变量名" }, "rawMeta": { "type": 1 } } }
```

**全局变量引用**（适合 API Key 等）：
```json
{ "type": "string", "value": { "type": "ref", "content": { "source": "global_variable_app", "path": ["变量名"], "blockID": "", "name": "" }, "rawMeta": { "type": 1 } } }
```

- 字符串插值：`{{global_variable_app["变量名"]}}`（仅限 url/json/rawText）
- 引用开始节点变量：`blockID` = `"100001"`

### rawMeta.type 完整映射表（必须严格遵守，错误的 rawMeta 会导致输入类型被强行改变）

#### 标量类型（1~6）

| rawMeta.type | input.type | 说明 |
|:---:|:---|:---|
| **1** | `string` | 字符串 |
| **2** | `integer` | 整数 |
| **3** | `boolean` | 布尔值 |
| **4** | `float` | 浮点数 |
| **6** | `object` | 对象 |

#### 文件类型（7~17）

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

#### 列表类型（99~116）

| rawMeta.type | schema.type | 说明 |
|:---:|:---|:---|
| **99** | `string` | list[string] |
| **100** | `integer` | list[integer] |
| **101** | `boolean` | list[boolean] |
| **102** | `float` | list[float] |
| **103** | `object` | list[object] |
| **116** | `string` + assistType:10000 | list[file] |

> ⚠️ **常见错误**：
> - list[string] 的 rawMeta 是 **99**，不是 103。只有 list[object] 才是 103
> - object 的 rawMeta 是 **6**，不是 1
> - file 类型不只有 8（Default），不同文件子类型各有编号（7~17），且需要 `assistType` 字段

### 开始节点支持的变量类型

| 类型 | rawMeta.type | 适用场景 |
|------|-------------|---------|
| `string` | 1 | 文本、URL |
| `integer` | 2 | 计数、阈值 |
| `number` | 4 | 评分、概率 |
| `boolean` | 3 | 开关 |
| `object` | 6 | 结构化数据（最多3层） |
| `array[string]` | 99 | 字符串列表 |
| `array[object]` | 103 | 对象列表 |
| `file` | 8 | 通用文件上传 |

---

## 大模型节点 Prompt 设计

### Prompt 质量要求

**System Prompt** 必须包含：角色定义、能力描述、行为约束、质量标准。
**User Prompt** 必须包含：任务目标、输入信息(`{{变量名}}`)、输出格式、评估标准。

**绝对禁止**过于简单的 Prompt（如 `"请处理以下内容：{{item}}"`），每个 LLM 节点的 Prompt 都应是精心设计的结构化专业提示词。

### 高级提示词技术（按需使用）

| 技术 | 适用场景 | 工作流实现方式 |
|------|---------|-------------|
| **思维链 (CoT)** | 推理、分析、判断 | 单 LLM，Prompt 中要求逐步思考 |
| **Few-Shot** | 格式化输出、分类 | 单 LLM，Prompt 给 2-3 个范例 |
| **Self-Consistency** | 高可信度判断 | 批处理(28) + 多次 LLM + 代码投票 |
| **ReAct** | 多步观察-行动 | 循环(21): LLM(决策) → 执行 → LLM(观察) |
| **Plan & Execute** | 复杂多步拆解 | LLM(规划list) → 批处理/循环(执行) → LLM(总结) |
| **Reflection** | 迭代优化 | 循环(21): LLM(生成) → LLM(评审) → 选择器(通过?) |

> 简单任务用 CoT 即可；中等复杂度用 Plan & Execute；高度动态任务用 ReAct。不要为简单任务过度设计。

### JSON 输出格式（responseFormat=2 时必须遵守）

Prompt 末尾必须包含格式说明，列出所有字段名（与 outputs 一致）、类型、取值范围：

```
# Output Format (JSON Only)
{
  "is_sensitive": boolean,
  "risk_level": "High | Medium | Low | None",
  "confidence": number (0-100),
  "analysis": "格式：【定性依据】一句话；【行为评估】一句话；【最终结论】一句话"
}
```

### LLM 参数调优

| 参数 | 值 | 场景 |
|------|------|------|
| temperature | 0.1~0.3 | 分类/判断 |
| temperature | 0.5~0.7 | 通用问答 |
| temperature | 0.8~1.0 | 创意写作 |
| maxTokens | 1024 | 简短回复 |
| maxTokens | 4096 | 中等分析 |
| maxTokens | 8192~16384 | 长文本 |
| topP | 0.85~0.95 | 通用 |
| thinking | 0 | 简单任务 |
| thinking | 1 | 复杂推理 |
| timeoutMs | 180000~600000 | 不低于 3 分钟 |

---

## 坐标布局规则

- 节点宽 360px，水平间距 450px，垂直分支间距 200px
- 容器内部子节点坐标相对于容器内部画布，从 (0, 0) 开始
- 起始位置建议 x=0, y=0
