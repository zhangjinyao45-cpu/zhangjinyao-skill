# 原力平台插件目录

> 本文件为 coze-workflow-generator skill 的插件参考文档。
> 插件既可以作为**独立节点(type=4)**使用，也可以挂载到 **LLM 节点的技能(fcParam)**中。
> 当工作流使用了插件节点时，**必须向用户索要 spaceId**（用户可直接粘贴原力平台工作空间的 URL，从中提取 `space/` 后的数字串）。

---

## 快速索引表

| # | 插件名 | API名 | pluginID | apiID | 类别 | 用途 |
|---|--------|-------|----------|-------|------|------|
| 1 | 博查搜索 | 博查搜索 | `7573626799205122048` | `7628887759360360448` | 搜索与信息获取 | 从全网搜索网页信息和链接，结果准确、摘要完整 |
| 2 | 百度智能搜索 | 百度智能搜索(AI搜索生成) | `23` | `230002` | 搜索与信息获取 | 搜索全网实时信息并智能总结回答，支持深度搜索和推理 |
| 3 | 百度智能搜索 | 百度智能搜索(网页搜索) | `23` | `230001` | 搜索与信息获取 | 百度网页搜索，返回摘要、网址等详细信息 |
| 4 | 百度智能搜索 | 百度智能搜索(媒体热榜) | `23` | `230004` | 搜索与信息获取 | 根据媒体平台查询热榜数据 |
| 5 | 百度智能搜索 | 百度智能搜索(垂类热榜) | `23` | `230003` | 搜索与信息获取 | 根据垂类类型、媒体类型获取热榜列表 |
| 6 | 搜狐热闻 | 搜狐热闻 | `6` | `60001` | 搜索与信息获取 | 获取搜狐网每日热闻 |
| 7 | 内容读取 | 内容读取 | `7571060527728689152` | `7571060688051765248` | 搜索与信息获取 | 获取网页、PDF、DOCX、XLSX、CSV、TXT内容 |
| 8 | scrape网页抓取内容 | scrape网页抓取内容 | `7574332670541299712` | `7574332892591947776` | 搜索与信息获取 | 输入网页地址解析内容，支持视频平台 |
| 9 | 品牌社媒声量查询 | 品牌社媒声量查询 | `7574343510795485184` | `7574343814039470080` | 搜索与信息获取 | 查询品牌近30天社媒声量趋势 |
| 10 | 身份证OCR | 身份证OCR | `7623329737498165248` | `7623329907291979776` | OCR与文档识别 | 从身份证图片中提取姓名、身份证号、地址等 |
| 11 | 完税证明OCR | 完税证明OCR | `7618108655488991232` | `7618109840727998464` | OCR与文档识别 | 从完税证明图片中提取纳税人信息和税务明细 |
| 12 | 学历学位证书OCR | 学历学位证书OCR | `7618104615392772096` | `7618104758322069504` | OCR与文档识别 | 从学历学位证书图片中提取学校、学历、姓名等 |
| 13 | 芝麻分OCR | 芝麻分OCR | `7618061944372592640` | `7618062010151862272` | OCR与文档识别 | 从芝麻分页面图片中提取分值 |
| 14 | 微信分OCR | 微信分OCR | `7618058253791920128` | `7618058405197905920` | OCR与文档识别 | 从微信分图片中提取分值 |
| 15 | 竞品offer OCR | 竞品offer OCR | `7618052370265538560` | `7618052440264278016` | OCR与文档识别 | 从竞品offer图片中提取额度、利率等核心信息，含篡改检测 |
| 16 | 个税OCR | 个税OCR | `7618046187114856448` | `7618107264729088000` | OCR与文档识别 | 从个税图片中提取收入和税务信息 |
| 17 | 发票OCR | 发票OCR | `7617781476133699584` | `7617781625987792896` | OCR与文档识别 | 从发票图片中提取开票信息、金额等 |
| 18 | TTS | TTS | `7613690331657142272` | `7613690491376238592` | 语音与音频处理 | 文本转语音，返回音频URL |
| 19 | ASR | ASR | `7576911113934077952` | `7576911152265822208` | 语音与音频处理 | 语音转文字，支持mp3/m4a/wav/pcm/ogg，仅普... |
| 20 | AED | AED | `7615143939246391296` | `7615144026299170816` | 语音与音频处理 | 声学事件识别（如铃声类型等） |
| 21 | speech_meeting | speech_meeting | `7615588752462708736` | `7615589030188548096` | 语音与音频处理 | 说话人日志识别（会议纪要场景） |
| 22 | 语音播客 | 语音播客 | `7574334109489561600` | `7574334202070433792` | 语音与音频处理 | 文本转双人对话播客音频，返回MP3链接 |
| 23 | 时间类工具包 | 时间类工具包 | `7615195917427146752` | `7615196041205252096` | 时间与日期工具 | 获取当前时间，支持自定义格式和时区 |
| 24 | get_time | get_time | `7582200654681079808` | `7582200654702051328` | 时间与日期工具 | 日期变量计算：T-N/T+N/today/month_sta... |
| 25 | Doubao图像生成 | Doubao图像生成 | `7574338924361809920` | `7574339044948049920` | 内容生成与创作 | 根据提示词生成图片，支持中英文Prompt |
| 26 | ChatPPT | ChatPPT | `7574335254391947264` | `7574335388232187904` | 内容生成与创作 | 一句话生成PPT演示文稿 |
| 27 | mysql_reader | mysql_reader | `7584044147057623040` | `7584044379061354496` | 数据查询与分析 | 读取MySQL数据库，单次最多10000条 |
| 28 | 鸿鹄插件 | 鸿鹄插件 | `7584382198875160576` | `7584382223629942784` | 数据查询与分析 | 在Doris集群中执行SQL查询 |
| 29 | SpecCoder | SpecCoder | `7571072544216711168` | `7571072544229294080` | 代码与开发工具 | 代码库分析与问答，支持多轮对话 |
| 30 | 飞书电子表格 | 飞书电子表格:add_cols | `17` | `170001` | 飞书集成 | 新增多列至工作表最后 |
| 31 | 飞书电子表格 | 飞书电子表格:add_rows | `17` | `170002` | 飞书集成 | 新增多行至工作表最后 |
| 32 | 飞书电子表格 | 飞书电子表格:create_spreadsheet | `17` | `170003` | 飞书集成 | 创建电子表格 |
| 33 | 飞书电子表格 | 飞书电子表格:delete_cols | `17` | `170004` | 飞书集成 | 删除电子表格工作表列 |
| 34 | 飞书电子表格 | 飞书电子表格:delete_rows | `17` | `170005` | 飞书集成 | 删除电子表格工作表行 |
| 35 | 飞书电子表格 | 飞书电子表格:get_spreadsheet | `17` | `170006` | 飞书集成 | 获取电子表格信息 |
| 36 | 飞书电子表格 | 飞书电子表格:list_spreadsheet_sheets | `17` | `170007` | 飞书集成 | 获取电子表格所有工作表 |
| 37 | 飞书电子表格 | 飞书电子表格:read_cols | `17` | `170008` | 飞书集成 | 读取工作表列数据 |
| 38 | 飞书电子表格 | 飞书电子表格:read_rows | `17` | `170009` | 飞书集成 | 读取工作表行数据 |
| 39 | 飞书电子表格 | 飞书电子表格:read_table | `17` | `170010` | 飞书集成 | 自定义读取电子表格行列数据 |
| 40 | 飞书电子表格 | 飞书电子表格:search_spreadsheet | `17` | `170011` | 飞书集成 | 搜索电子表格类型文档 |
| 41 | 飞书知识库 | 飞书知识库:search_wiki | `20` | `200001` | 飞书集成 | 搜索Wiki文档列表 |
| 42 | 飞书多维表格 | 飞书多维表格:add_field | `16` | `160001` | 飞书集成 | 新增字段 |
| 43 | 飞书多维表格 | 飞书多维表格:add_records | `16` | `160002` | 飞书集成 | 新增多条记录(单次最多500条) |
| 44 | 飞书多维表格 | 飞书多维表格:create_base | `16` | `160003` | 飞书集成 | 创建多维表格 |
| 45 | 飞书多维表格 | 飞书多维表格:create_table | `16` | `160004` | 飞书集成 | 创建多维表格数据表 |
| 46 | 飞书多维表格 | 飞书多维表格:delete_field | `16` | `160005` | 飞书集成 | 删除字段 |
| 47 | 飞书多维表格 | 飞书多维表格:delete_records | `16` | `160006` | 飞书集成 | 批量删除记录 |
| 48 | 飞书多维表格 | 飞书多维表格:delete_tables | `16` | `160007` | 飞书集成 | 删除数据表(最多50个) |
| 49 | 飞书多维表格 | 飞书多维表格:get_base_info | `16` | `160008` | 飞书集成 | 获取多维表格元数据 |
| 50 | 飞书多维表格 | 飞书多维表格:list_fields | `16` | `160009` | 飞书集成 | 列出数据表全部字段 |
| 51 | 飞书多维表格 | 飞书多维表格:list_tables | `16` | `160010` | 飞书集成 | 列出全部数据表 |
| 52 | 飞书多维表格 | 飞书多维表格:search_base | `16` | `160011` | 飞书集成 | 搜索多维表格类型文档 |
| 53 | 飞书多维表格 | 飞书多维表格:search_record | `16` | `160012` | 飞书集成 | 查询记录(单次最多500条) |
| 54 | 飞书多维表格 | 飞书多维表格:update_field | `16` | `160013` | 飞书集成 | 更新字段 |
| 55 | 飞书多维表格 | 飞书多维表格:update_records | `16` | `160014` | 飞书集成 | 批量更新记录(单次最多500条) |
| 56 | 飞书消息 | get_chat_messages | `15` | `150001` | 飞书集成 | 获取指定单聊、群聊的消息历史 |
| 57 | 飞书消息 | get_thread_messages | `15` | `15002` | 飞书集成 | 获取指定话题的消息历史 |
| 58 | 飞书消息 | send_bot_message | `15` | `150003` | 飞书集成 | 使用应用机器人发送飞书消息 |
| 59 | 飞书任务 | create_task | `18` | `180001` | 飞书集成 | 创建飞书任务 |
| 60 | 飞书任务 | delete_task | `18` | `180002` | 飞书集成 | 删除飞书任务 |
| 61 | 飞书任务 | list_tasks | `18` | `180003` | 飞书集成 | 列取飞书任务列表 |
| 62 | 飞书任务 | update_task | `18` | `180004` | 飞书集成 | 更新飞书任务 |
| 63 | 飞书云文档 | create_document | `19` | `190001` | 飞书集成 | 创建文档，支持创建空文档和带内容的文档， |
| 64 | 飞书云文档 | get_document_content | `19` | `190002` | 飞书集成 | 获取文档内容，支持纯文本或markdow |
| 65 | 飞书云文档 | get_document_info | `19` | `190003` | 飞书集成 | 获取文档的基本信息 |
| 66 | 飞书云文档 | list_document_blocks | `19` | `190004` | 飞书集成 | 获取文档所有块的富文本内容并分页返回 |
| 67 | 飞书云文档 | search_document | `19` | `190005` | 飞书集成 | 搜索文档类型的文档 |
| 68 | 飞书云文档 | search_slides | `19` | `190006` | 飞书集成 | 搜索PPT类型的文档 |
| 69 | 飞书云文档 | write_document | `19` | `190007` | 飞书集成 | 在文档中新增内容，支持纯文本或markd |
| 70 | 飞书云文档 | download_media | `19` | `190008` | 飞书集成 | 下载素材 |
| 71 | 飞书云文档 | upload_media | `19` | `190009` | 飞书集成 | 上传素材到飞书云文档/多维表格/电子表格 |
| 72 | 飞书日历 | create_event | `21` | `210001` | 飞书集成 | 创建日程 |
| 73 | 飞书日历 | delete_event | `21` | `210002` | 飞书集成 | 删除日程 |
| 74 | 飞书日历 | get_primary_calendar | `21` | `210003` | 飞书集成 | 查询主日历信息 |
| 75 | 飞书日历 | list_events | `21` | `210004` | 飞书集成 | 获取日程列表 |
| 76 | 飞书日历 | search_events | `21` | `210005` | 飞书集成 | 搜索日程 |
| 77 | 飞书日历 | update_event | `21` | `210006` | 飞书集成 | 更新日程 |
| 78 | 飞书认证及授权 | get_tenant_access_token | `14` | `140001` | 飞书集成 | 获取租户访问凭证(tenant_acce |

---

## 搜索与信息获取

### 博查搜索 — 博查搜索

- **title**: `web_search`
- **pluginID**: `7573626799205122048`
- **apiID**: `7628887759360360448`
- **描述**: 从全网搜索网页信息和链接，结果准确、摘要完整

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `query` | string | 必填 | 搜索词 |
| `count` | integer | 选填 | 返回条数1-50 |
| `summary` | boolean | 选填 | 是否显示摘要 |
| `freshness` | string | 选填 | 时间范围: oneDay/oneWeek/oneMonth/oneYear/noLimit/YYYY-MM-DD..YYYY-MM-DD |
| `page` | integer | 选填 | 页码，默认1 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含webPages/images/queryContext |
| `log_id` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7628887759360360448", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "博查搜索", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7573626799205122048", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "博查搜索", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 百度智能搜索 — 百度智能搜索(AI搜索生成)

- **title**: `baidu_ai_search_chat`
- **pluginID**: `23`
- **apiID**: `230002`
- **描述**: 搜索全网实时信息并智能总结回答，支持深度搜索和推理

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `messages` | list[{content,role}] | 必填 | 用户消息列表 |
| `search_recency_filter` | string | 选填 | year/semiyear/month/week |
| `enable_deep_search` | boolean | 选填 | 深度搜索 |
| `enable_reasoning` | boolean | 选填 | 启用推理 |
| `search_filter` | object | 选填 | 网站筛选 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `choices` | list | 含message.content |
| `references` | list | 搜索结果列表 |
| `is_safe` | boolean |  |
| `usage` | object |  |
| `request_id` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "230002", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "百度智能搜索(AI搜索生成)", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "23", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "百度智能搜索", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 百度智能搜索 — 百度智能搜索(网页搜索)

- **title**: `baidu_web_search`
- **pluginID**: `23`
- **apiID**: `230001`
- **描述**: 百度网页搜索，返回摘要、网址等详细信息

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `messages` | list[{content,role}] | 必填 | 搜索内容 |
| `resource_type_filter` | list | 选填 | 资源类型web/video/image |
| `search_filter` | object | 选填 | 网站筛选 |
| `search_recency_filter` | string | 选填 | 时间范围 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `references` | list | 搜索结果含url/title/content/date |
| `request_id` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "230001", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "百度智能搜索(网页搜索)", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "23", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "百度智能搜索", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 百度智能搜索 — 百度智能搜索(媒体热榜)

- **title**: `baidu_medium_trending`
- **pluginID**: `23`
- **apiID**: `230004`
- **描述**: 根据媒体平台查询热榜数据

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `type` | integer | 必填 | 媒体平台类型，如6=抖音 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | list | 含title/url/hot/date |
| `msg` | string |  |
| `requestId` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "230004", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "百度智能搜索(媒体热榜)", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "23", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "百度智能搜索", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 百度智能搜索 — 百度智能搜索(垂类热榜)

- **title**: `baidu_vertical_trending`
- **pluginID**: `23`
- **apiID**: `230003`
- **描述**: 根据垂类类型、媒体类型获取热榜列表

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `type` | string | 必填 | 垂类如汽车/科技/娱乐 |
| `mediaType` | string | 必填 | 如抖音/微博/知乎 |
| `timeRange` | integer | 选填 | 天数 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | list | 含title/url/hotNum/likeCount等 |
| `msg` | string |  |
| `requestID` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "230003", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "百度智能搜索(垂类热榜)", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "23", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "百度智能搜索", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 搜狐热闻 — 搜狐热闻

- **title**: `top_news`
- **pluginID**: `6`
- **apiID**: `60001`
- **描述**: 获取搜狐网每日热闻

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `count` | integer | 必填 | 新闻条数 |
| `q` | string | 选填 | 搜索关键词 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `total` | float |  |
| `data` | object | 含list[{url,brief,title}] |
| `success` | boolean |  |
| `code` | float |  |
| `message` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "60001", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "搜狐热闻", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "6", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "搜狐热闻", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 内容读取 — 内容读取

- **title**: `LinkReader`
- **pluginID**: `7571060527728689152`
- **apiID**: `7571060688051765248`
- **描述**: 获取网页、PDF、DOCX、XLSX、CSV、TXT内容

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `url` | string | 必填 | 网页或文件url |
| `need_image_url` | boolean | 选填 | 是否返回图片url |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `msg` | string |  |
| `code` | integer |  |
| `data` | object | 含url/type/title/content/summary |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7571060688051765248", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "内容读取", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7571060527728689152", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "内容读取", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### scrape网页抓取内容 — scrape网页抓取内容

- **title**: `Scrape`
- **pluginID**: `7574332670541299712`
- **apiID**: `7574332892591947776`
- **描述**: 输入网页地址解析内容，支持视频平台

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `url` | string | 必填 | 网页地址 |
| `only_main_content` | boolean | 选填 | 是否只提取主要内容 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含title/content/description/source_data |
| `message` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7574332892591947776", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "scrape网页抓取内容", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7574332670541299712", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "scrape网页抓取内容", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 品牌社媒声量查询 — 品牌社媒声量查询

- **title**: `queryPayCozeData`
- **pluginID**: `7574343510795485184`
- **apiID**: `7574343814039470080`
- **描述**: 查询品牌近30天社媒声量趋势

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `keyword` | string | 必填 | 关键词 |
| `userKey` | string | 选填 | 用户标识 |
| `N-Token` | string | 选填 | 接口标识 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `message` | string |  |
| `code` | integer |  |
| `data` | object | 含score/awemeCount/hotEventVoList/totalAwemeList等 |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7574343814039470080", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "品牌社媒声量查询", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7574343510795485184", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "品牌社媒声量查询", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

## OCR与文档识别

### 身份证OCR — 身份证OCR

- **title**: `idcardOcr`
- **pluginID**: `7623329737498165248`
- **apiID**: `7623329907291979776`
- **描述**: 从身份证图片中提取姓名、身份证号、地址等

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `image_url` | string | 必填 | 身份证图片URL |
| `id_card_side` | string | 必填 | front=正面/back=背面 |
| `detect_risk` | string | 选填 | 是否检测风险 |
| `detect_direction` | string | 选填 | 是否检测旋转 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `error_code` | integer |  |
| `words_result` | object | 含姓名/性别/民族/出生/住址/公民身份证号码等 |
| `image_status` | string |  |
| `log_id` | string |  |
| `error_msg` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7623329907291979776", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "身份证OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7623329737498165248", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "身份证OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 完税证明OCR — 完税证明OCR

- **title**: `taxCertificateOcr`
- **pluginID**: `7618108655488991232`
- **apiID**: `7618109840727998464`
- **描述**: 从完税证明图片中提取纳税人信息和税务明细

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `image_url` | string | 必填 | 图片URL |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `error_code` | integer |  |
| `words_result` | object | 含taxpayerName/idNumber/orderLists等 |
| `log_id` | string |  |
| `error_msg` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7618109840727998464", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "完税证明OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7618108655488991232", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "完税证明OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 学历学位证书OCR — 学历学位证书OCR

- **title**: `degreeOcr`
- **pluginID**: `7618104615392772096`
- **apiID**: `7618104758322069504`
- **描述**: 从学历学位证书图片中提取学校、学历、姓名等

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `image_url` | string | 必填 | 图片URL |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `error_code` | integer |  |
| `words_result` | object | 含name/sex/nameOfUniversity/educationLevel/graduationTime/ps等 |
| `log_id` | string |  |
| `error_msg` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7618104758322069504", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "学历学位证书OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7618104615392772096", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "学历学位证书OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 芝麻分OCR — 芝麻分OCR

- **title**: `zmscoreOcr`
- **pluginID**: `7618061944372592640`
- **apiID**: `7618062010151862272`
- **描述**: 从芝麻分页面图片中提取分值

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `image_url` | string | 必填 | 图片URL |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `error_code` | integer |  |
| `words_result` | object | 含zmScore/wxScore/pictureType/personName等 |
| `log_id` | string |  |
| `error_msg` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7618062010151862272", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "芝麻分OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7618061944372592640", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "芝麻分OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 微信分OCR — 微信分OCR

- **title**: `wechatScoreOcr`
- **pluginID**: `7618058253791920128`
- **apiID**: `7618058405197905920`
- **描述**: 从微信分图片中提取分值

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `image_url` | string | 必填 | 图片URL |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `error_code` | integer |  |
| `words_result` | object | 含wxScore/wxScoreDate/pictureType/personName等 |
| `log_id` | string |  |
| `error_msg` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7618058405197905920", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "微信分OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7618058253791920128", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "微信分OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 竞品offer OCR — 竞品offer OCR

- **title**: `competingOfferOcr`
- **pluginID**: `7618052370265538560`
- **apiID**: `7618052440264278016`
- **描述**: 从竞品offer图片中提取额度、利率等核心信息，含篡改检测

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `image_url` | string | 必填 | 图片URL |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `error_code` | integer |  |
| `words_result` | object | 含offer_totaltaxes/offer_dailyinterestrate/is_tamper/picturetype等 |
| `log_id` | string |  |
| `error_msg` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7618052440264278016", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "竞品offer OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7618052370265538560", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "竞品offer OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 个税OCR — 个税OCR

- **title**: `incomeTaxOcr`
- **pluginID**: `7618046187114856448`
- **apiID**: `7618107264729088000`
- **描述**: 从个税图片中提取收入和税务信息

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `image_url` | string | 必填 | 图片URL |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `error_code` | integer |  |
| `words_result` | object | 含pageType/totalIncome/totalTaxDeclared/taxChecklistEconomicNature等 |
| `log_id` | string |  |
| `error_msg` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7618107264729088000", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "个税OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7618046187114856448", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "个税OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 发票OCR — 发票OCR

- **title**: `invoiceOcr`
- **pluginID**: `7617781476133699584`
- **apiID**: `7617781625987792896`
- **描述**: 从发票图片中提取开票信息、金额等

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `image_url` | string | 必填 | 图片URL |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `error_code` | integer |  |
| `words_result` | object | 含invoiceNumber/billingDate/totalAmount/nameOfPurchaser等 |
| `log_id` | string |  |
| `error_msg` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7617781625987792896", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "发票OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7617781476133699584", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "发票OCR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

## 语音与音频处理

### TTS — TTS

- **title**: `tts`
- **pluginID**: `7613690331657142272`
- **apiID**: `7613690491376238592`
- **描述**: 文本转语音，返回音频URL

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `text` | string | 必填 | 输入文本 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `url` | string | 音频URL |
| `code` | integer |  |
| `message` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7613690491376238592", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "TTS", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7613690331657142272", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "TTS", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### ASR — ASR

- **title**: `ASR`
- **pluginID**: `7576911113934077952`
- **apiID**: `7576911152265822208`
- **描述**: 语音转文字，支持mp3/m4a/wav/pcm/ogg，仅普通话

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `file_url` | string | 必填 | 音频文件url |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `msg` | string |  |
| `code` | float |  |
| `data` | object | 含text |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7576911152265822208", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "ASR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7576911113934077952", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "ASR", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### AED — AED

- **title**: `AED`
- **pluginID**: `7615143939246391296`
- **apiID**: `7615144026299170816`
- **描述**: 声学事件识别（如铃声类型等）

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `audio` | string | 必填 | 音频文件(assistType:8) |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含ring_type |
| `message` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7615144026299170816", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "AED", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7615143939246391296", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "AED", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### speech_meeting — speech_meeting

- **title**: `speech_meeting`
- **pluginID**: `7615588752462708736`
- **apiID**: `7615589030188548096`
- **描述**: 说话人日志识别（会议纪要场景）

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `arguments` | object | 必填 | 含wav_uri音频url |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `result` | list[object] | 含content/speaker/start_time/end_time |
| `errorMsg` | string |  |
| `errorCode` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7615589030188548096", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "speech_meeting", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7615588752462708736", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "speech_meeting", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 语音播客 — 语音播客

- **title**: `genPodcastURL`
- **pluginID**: `7574334109489561600`
- **apiID**: `7574334202070433792`
- **描述**: 文本转双人对话播客音频，返回MP3链接

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `input_text` | string | 选填 | 待播客文本≤15000字 |
| `use_head_music` | boolean | 选填 | 是否使用开头音效 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含data.content.podcast_url |
| `message` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7574334202070433792", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "语音播客", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7574334109489561600", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "语音播客", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

## 时间与日期工具

### 时间类工具包 — 时间类工具包

- **title**: `get_current_time`
- **pluginID**: `7615195917427146752`
- **apiID**: `7615196041205252096`
- **描述**: 获取当前时间，支持自定义格式和时区

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `format` | string | 选填 | 时间格式，默认yyyy-MM-dd HH:mm:ss |
| `timeZone` | string | 选填 | 时区，默认UTC+8 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer | 0=正常 |
| `message` | string | 格式化后的当前时间 |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7615196041205252096", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "时间类工具包", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7615195917427146752", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "时间类工具包", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### get_time — get_time

- **title**: `timevar`
- **pluginID**: `7582200654681079808`
- **apiID**: `7582200654702051328`
- **描述**: 日期变量计算：T-N/T+N/today/month_start/month_end/last_month_end等

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `parameters` | object | 选填 | 含date_var日期变量 |
| `app_id` | string | 选填 | app_id |
| `workflow_id` | string | 选填 | workflow_id |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `data` | string |  |
| `code` | integer |  |
| `token` | integer |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7582200654702051328", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "get_time", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7582200654681079808", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "get_time", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

## 内容生成与创作

### Doubao图像生成 — Doubao图像生成

- **title**: `gen_image`
- **pluginID**: `7574338924361809920`
- **apiID**: `7574339044948049920`
- **描述**: 根据提示词生成图片，支持中英文Prompt

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `prompt` | string | 必填 | 生成图像的提示词 |
| `req_schedule_conf` | string | 必填 | 模型配置，默认general_v20_9B_pe |
| `width` | integer | 选填 | 宽256-768,默认512 |
| `height` | integer | 选填 | 高256-768,默认512 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `data` | object | 含data.data.image_urls |
| `message` | string |  |
| `code` | integer |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7574339044948049920", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "Doubao图像生成", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7574338924361809920", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "Doubao图像生成", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### ChatPPT — ChatPPT

- **title**: `ChatPPT`
- **pluginID**: `7574335254391947264`
- **apiID**: `7574335388232187904`
- **描述**: 一句话生成PPT演示文稿

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `text` | string | 必填 | 文档主题 |
| `color` | string | 选填 | 主题颜色，默认蓝色 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含data.downloadInfo.fileInfo.preview_url |
| `message` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7574335388232187904", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "ChatPPT", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7574335254391947264", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "ChatPPT", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

## 数据查询与分析

### mysql_reader — mysql_reader

- **title**: `mysql_reader`
- **pluginID**: `7584044147057623040`
- **apiID**: `7584044379061354496`
- **描述**: 读取MySQL数据库，单次最多10000条

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `host` | string | 必填 | MySQL host |
| `port` | integer | 必填 | 端口 |
| `database` | string | 必填 | 数据库名 |
| `userName` | string | 必填 | 账号 |
| `password` | string | 必填 | 密码 |
| `querySql` | string | 必填 | SQL查询语句 |
| `requestId` | string | 必填 | 请求ID |
| `source` | string | 必填 | 来源名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `resultList` | list[string] | 查询结果集 |
| `rewrittenSql` | string |  |
| `code` | integer |  |
| `message` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7584044379061354496", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "mysql_reader", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7584044147057623040", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "mysql_reader", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 鸿鹄插件 — 鸿鹄插件

- **title**: `doris_query`
- **pluginID**: `7584382198875160576`
- **apiID**: `7584382223629942784`
- **描述**: 在Doris集群中执行SQL查询

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `sql` | string | 必填 | 查询SQL |
| `maxRows` | integer | 必填 | 查询条数 |
| `rccGroup` | string | 必填 | rcc组 |
| `userName` | string | 必填 | uuap |
| `clusterId` | integer | 必填 | 1=FSGRIM-DORIS, 2=BI-DORIS |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含data/columns/message/taskStatus |
| `message` | string |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7584382223629942784", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "鸿鹄插件", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7584382198875160576", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "鸿鹄插件", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

## 代码与开发工具

### SpecCoder — SpecCoder

- **title**: `analyze_code`
- **pluginID**: `7571072544216711168`
- **apiID**: `7571072544229294080`
- **描述**: 代码库分析与问答，支持多轮对话

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `repository_name` | string | 必填 | 代码库格式group/repo |
| `question` | string | 必填 | 用户提问 |
| `branch` | string | 选填 | 分支名 |
| `user_id` | string | 选填 | 用户ID |
| `conversation_id` | integer | 选填 | 多轮对话会话ID |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `answer` | string | 含思考过程 |
| `result` | string | 不含思考过程 |
| `success` | boolean |  |
| `conversation_id` | integer |  |

<details>
<summary>apiParam 配置片段（点击展开）</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "7571072544229294080", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "SpecCoder", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "7571072544216711168", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "SpecCoder", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

## 飞书集成

> 飞书插件支持电子表格、多维表格、知识库的操作。所有飞书插件都使用同一个 pluginID 下的不同 apiID。
> 所有 API 的 `spreadsheet_token` 和 `app_token` 参数都**支持直接传入飞书文档 URL**。

### 飞书电子表格（pluginID: `17`）

| apiID | title | 用途 |
|-------|-------|------|
| `170001` | add_cols | 新增多列至工作表最后 |
| `170002` | add_rows | 新增多行至工作表最后 |
| `170003` | create_spreadsheet | 创建电子表格 |
| `170004` | delete_cols | 删除电子表格工作表列 |
| `170005` | delete_rows | 删除电子表格工作表行 |
| `170006` | get_spreadsheet | 获取电子表格信息 |
| `170007` | list_spreadsheet_sheets | 获取电子表格所有工作表 |
| `170008` | read_cols | 读取工作表列数据 |
| `170009` | read_rows | 读取工作表行数据 |
| `170010` | read_table | 自定义读取电子表格行列数据 |
| `170011` | search_spreadsheet | 搜索电子表格类型文档 |

#### add_cols

- **apiID**: `170001`
- **描述**: 新增多列至工作表最后

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `spreadsheet_token` | string | 必填 | 电子表格token，支持URL |
| `length` | float | 必填 | 要增加的列数 |
| `values` | string | 选填 | 新增列内容，数组字符串 |
| `sheet_id` | string | 选填 | 工作表ID(与sheet_name二选一) |
| `sheet_name` | string | 选填 | 工作表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含addCount/majorDimension |
| `msg` | string |  |
| `log_id` | string |  |

#### add_rows

- **apiID**: `170002`
- **描述**: 新增多行至工作表最后

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `spreadsheet_token` | string | 必填 | 电子表格token，支持URL |
| `length` | float | 必填 | 要增加行数(0-5000] |
| `values` | string | 选填 | 新增行内容，数组字符串 |
| `sheet_id` | string | 选填 | 工作表ID |
| `sheet_name` | string | 选填 | 工作表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含addCount/majorDimension |
| `msg` | string |  |
| `log_id` | string |  |

#### create_spreadsheet

- **apiID**: `170003`
- **描述**: 创建电子表格

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `folder_token` | string | 选填 | 文件夹token，支持URL |
| `title` | string | 选填 | 电子表格标题 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含spreadsheet.url/token/title |
| `msg` | string |  |
| `log_id` | string |  |

#### delete_cols

- **apiID**: `170004`
- **描述**: 删除电子表格工作表列

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `spreadsheet_token` | string | 必填 | 电子表格token，支持URL |
| `start_index` | float | 必填 | 起始列位置(从1开始) |
| `end_index` | float | 必填 | 结束列位置(从1开始) |
| `sheet_id` | string | 选填 | 工作表ID |
| `sheet_name` | string | 选填 | 工作表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含delCount/majorDimension |
| `msg` | string |  |
| `log_id` | string |  |

#### delete_rows

- **apiID**: `170005`
- **描述**: 删除电子表格工作表行

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `spreadsheet_token` | string | 必填 | 电子表格token，支持URL |
| `start_index` | float | 必填 | 起始行(从1开始) |
| `end_index` | float | 必填 | 结束行(从1开始) |
| `sheet_id` | string | 选填 | 工作表ID |
| `sheet_name` | string | 选填 | 工作表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含delCount/majorDimension |
| `msg` | string |  |
| `log_id` | string |  |

#### get_spreadsheet

- **apiID**: `170006`
- **描述**: 获取电子表格信息

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `spreadsheet_token` | string | 必填 | 电子表格token，支持URL |
| `user_id_type` | string | 选填 | 用户ID类型 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含spreadsheet.owner_id/title/token/url |
| `msg` | string |  |
| `log_id` | string |  |

#### list_spreadsheet_sheets

- **apiID**: `170007`
- **描述**: 获取电子表格所有工作表

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `spreadsheet_token` | string | 必填 | 电子表格token，支持URL |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含sheets列表(sheet_id/title/grid_properties等) |
| `msg` | string |  |
| `log_id` | string |  |

#### read_cols

- **apiID**: `170008`
- **描述**: 读取工作表列数据

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `spreadsheet_token` | string | 必填 | 电子表格token，支持URL |
| `num_cols` | integer | 必填 | 读取列数 |
| `start_col` | integer | 选填 | 起始列号(从1开始) |
| `sheet_id` | string | 选填 | 工作表ID |
| `sheet_name` | string | 选填 | 工作表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含valueRange.valuesJsonString |
| `msg` | string |  |
| `log_id` | string |  |

#### read_rows

- **apiID**: `170009`
- **描述**: 读取工作表行数据

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `spreadsheet_token` | string | 必填 | 电子表格token，支持URL |
| `num_rows` | integer | 必填 | 读取行数 |
| `start_row` | integer | 选填 | 起始行号(从1开始) |
| `sheet_id` | string | 选填 | 工作表ID |
| `sheet_name` | string | 选填 | 工作表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含valueRange.valuesJsonString |
| `msg` | string |  |
| `log_id` | string |  |

#### read_table

- **apiID**: `170010`
- **描述**: 自定义读取电子表格行列数据

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `spreadsheet_token` | string | 必填 | 电子表格token，支持URL |
| `range` | string | 选填 | 取数范围如A1:B2 |
| `query` | string | 选填 | 传all查全部(最多100列) |
| `sheet_id` | string | 选填 | 工作表ID |
| `sheet_name` | string | 选填 | 工作表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含valueRange.valuesJsonString |
| `msg` | string |  |
| `log_id` | string |  |

#### search_spreadsheet

- **apiID**: `170011`
- **描述**: 搜索电子表格类型文档

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `search_key` | string | 必填 | 搜索关键字 |
| `count` | integer | 选填 | 返回文件数[0,50] |
| `offset` | integer | 选填 | 搜索偏移量 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含docs_entities列表(url/title/docs_token等) |
| `msg` | string |  |
| `log_id` | string |  |

<details>
<summary>飞书电子表格 apiParam 配置片段（点击展开）— 所有 API 共用 pluginID/pluginName，仅 apiID/apiName 不同</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "{API_ID}", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书电子表格", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "17", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书电子表格", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 飞书知识库（pluginID: `20`）

| apiID | title | 用途 |
|-------|-------|------|
| `200001` | search_wiki | 搜索Wiki文档列表 |

#### search_wiki

- **apiID**: `200001`
- **描述**: 搜索Wiki文档列表

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `query` | string | 必填 | 搜索关键词 |
| `space_id` | string | 选填 | 知识空间ID，支持URL |
| `node_id` | string | 选填 | 搜索该节点及子节点(需配合space_id) |
| `page_size` | integer | 选填 | 返回数量[0-50] |
| `page_token` | string | 选填 | 分页token |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer |  |
| `data` | object | 含items列表(title/url/space_id/node_id等) |
| `msg` | string |  |
| `log_id` | string |  |

<details>
<summary>飞书知识库 apiParam 配置片段（点击展开）— 所有 API 共用 pluginID/pluginName，仅 apiID/apiName 不同</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "{API_ID}", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书知识库", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "20", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书知识库", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

### 飞书多维表格（pluginID: `16`）

| apiID | title | 用途 |
|-------|-------|------|
| `160001` | add_field | 新增字段 |
| `160002` | add_records | 新增多条记录(单次最多500条) |
| `160003` | create_base | 创建多维表格 |
| `160004` | create_table | 创建多维表格数据表 |
| `160005` | delete_field | 删除字段 |
| `160006` | delete_records | 批量删除记录 |
| `160007` | delete_tables | 删除数据表(最多50个) |
| `160008` | get_base_info | 获取多维表格元数据 |
| `160009` | list_fields | 列出数据表全部字段 |
| `160010` | list_tables | 列出全部数据表 |
| `160011` | search_base | 搜索多维表格类型文档 |
| `160012` | search_record | 查询记录(单次最多500条) |
| `160013` | update_field | 更新字段 |
| `160014` | update_records | 批量更新记录(单次最多500条) |

#### add_field

- **apiID**: `160001`
- **描述**: 新增字段

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_token` | string | 必填 | 多维表格标识，支持URL |
| `field_name` | string | 必填 | 字段名称 |
| `type` | integer | 必填 | 字段类型(1文本/2数字/3单选/4多选/5日期/7复选框等) |
| `table_id` | string | 选填 | 数据表ID |
| `table_name` | string | 选填 | 数据表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含field(field_id/field_name/type等) |
| `msg` | string |  |
| `log_id` | string |  |

#### add_records

- **apiID**: `160002`
- **描述**: 新增多条记录(单次最多500条)

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_token` | string | 必填 | 多维表格标识，支持URL |
| `records` | list | 必填 | 记录列表[{fields:JSON字符串}] |
| `table_id` | string | 选填 | 数据表ID |
| `table_name` | string | 选填 | 数据表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含records列表(record_id/fields) |
| `msg` | string |  |
| `log_id` | string |  |

#### create_base

- **apiID**: `160003`
- **描述**: 创建多维表格

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | string | 必填 | 多维表格名字 |
| `folder_token` | string | 选填 | 归属文件夹，支持URL |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含app(app_token/url/name/default_table_id) |
| `msg` | string |  |
| `log_id` | string |  |

#### create_table

- **apiID**: `160004`
- **描述**: 创建多维表格数据表

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_token` | string | 必填 | 多维表格标识，支持URL |
| `name` | string | 必填 | 数据表名称 |
| `fields` | list | 选填 | 初始字段列表[{field_name,type}] |
| `default_view_name` | string | 选填 | 默认视图名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含table_id/field_id_list |
| `msg` | string |  |
| `log_id` | string |  |

#### delete_field

- **apiID**: `160005`
- **描述**: 删除字段

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_token` | string | 必填 | 多维表格标识，支持URL |
| `field_id` | string | 选填 | 字段ID(与field_name二选一) |
| `field_name` | string | 选填 | 字段名称 |
| `table_id` | string | 选填 | 数据表ID |
| `table_name` | string | 选填 | 数据表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含field_id/deleted |
| `msg` | string |  |
| `log_id` | string |  |

#### delete_records

- **apiID**: `160006`
- **描述**: 批量删除记录

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_token` | string | 必填 | 多维表格标识，支持URL |
| `records` | list | 必填 | 记录ID列表["recXXX"] |
| `table_id` | string | 选填 | 数据表ID |
| `table_name` | string | 选填 | 数据表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含records列表(record_id/deleted) |
| `msg` | string |  |
| `log_id` | string |  |

#### delete_tables

- **apiID**: `160007`
- **描述**: 删除数据表(最多50个)

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_token` | string | 必填 | 多维表格标识，支持URL |
| `table_ids` | list | 选填 | 数据表ID列表 |
| `table_names` | list | 选填 | 数据表名称列表 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `msg` | string |  |
| `log_id` | string |  |

#### get_base_info

- **apiID**: `160008`
- **描述**: 获取多维表格元数据

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_token` | string | 必填 | 多维表格标识，支持URL |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含app(app_token/name/revision/is_advanced等) |
| `msg` | string |  |
| `log_id` | string |  |

#### list_fields

- **apiID**: `160009`
- **描述**: 列出数据表全部字段

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_token` | string | 必填 | 多维表格标识，支持URL |
| `table_id` | string | 选填 | 数据表ID |
| `table_name` | string | 选填 | 数据表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含items列表(field_id/field_name/type/property等) |
| `msg` | string |  |
| `log_id` | string |  |

#### list_tables

- **apiID**: `160010`
- **描述**: 列出全部数据表

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_token` | string | 必填 | 多维表格标识，支持URL |
| `page_size` | integer | 选填 | 分页大小[最大100] |
| `page_token` | string | 选填 | 分页token |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含items列表(table_id/name/revision) |
| `msg` | string |  |
| `log_id` | string |  |

#### search_base

- **apiID**: `160011`
- **描述**: 搜索多维表格类型文档

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `search_key` | string | 必填 | 搜索关键字 |
| `count` | integer | 选填 | 返回数[0,50] |
| `offset` | integer | 选填 | 偏移量 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含docs_entities列表(url/title/docs_token等) |
| `msg` | string |  |
| `log_id` | string |  |

#### search_record

- **apiID**: `160012`
- **描述**: 查询记录(单次最多500条)

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_token` | string | 必填 | 多维表格标识，支持URL |
| `table_id` | string | 选填 | 数据表ID |
| `table_name` | string | 选填 | 数据表名称 |
| `filter` | object | 选填 | 筛选条件{conjunction,conditions} |
| `sort` | list | 选填 | 排序条件 |
| `field_names` | list | 选填 | 返回字段名列表 |
| `page_size` | integer | 选填 | 分页大小[最大500] |
| `page_token` | string | 选填 | 分页token |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含items列表(record_id/fields)/has_more/total |
| `msg` | string |  |
| `log_id` | string |  |

#### update_field

- **apiID**: `160013`
- **描述**: 更新字段

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_token` | string | 必填 | 多维表格标识，支持URL |
| `update_field` | object | 必填 | 修改后的字段信息{field_name,type} |
| `field_id` | string | 选填 | 待更新字段ID(与field_name二选一) |
| `field_name` | string | 选填 | 待更新字段名称 |
| `table_id` | string | 选填 | 数据表ID |
| `table_name` | string | 选填 | 数据表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含field详情 |
| `msg` | string |  |
| `log_id` | string |  |

#### update_records

- **apiID**: `160014`
- **描述**: 批量更新记录(单次最多500条)

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_token` | string | 必填 | 多维表格标识，支持URL |
| `records` | list | 必填 | 记录列表[{record_id,fields:JSON}] |
| `table_id` | string | 选填 | 数据表ID |
| `table_name` | string | 选填 | 数据表名称 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float |  |
| `data` | object | 含records列表(record_id/fields) |
| `msg` | string |  |
| `log_id` | string |  |

<details>
<summary>飞书多维表格 apiParam 配置片段（点击展开）— 所有 API 共用 pluginID/pluginName，仅 apiID/apiName 不同</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "{API_ID}", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书多维表格", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "16", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书多维表格", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

</details>

---

## 使用模式

### 模式一：作为独立插件节点 (type=4)

直接在工作流中使用，参考 `node-templates.md` 的插件调用基础模板。关键点：

1. **必须有 spaceId**（节点顶层）
2. `inputs.apiParam` 配置插件标识（从本文档的 apiParam 配置片段复制）
3. `inputs.inputParameters` 配置业务输入参数（如需引用上游变量，使用 ref）
4. `outputs` 配置业务输出参数
5. `_temp.externalData` 配置插件展示信息（含 inputs/outputs 元信息）

#### inputParameters 配置示例（引用上游节点输出）

```json
"inputParameters": [
  {
    "name": "text",
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
```

#### inputParameters 配置示例（使用固定值）

```json
"inputParameters": [
  {
    "name": "count",
    "input": {
      "type": "integer",
      "value": {
        "type": "literal",
        "content": "10",
        "rawMeta": { "type": 2 }
      }
    }
  }
]
```

### 模式二：挂载到 LLM 节点技能 (fcParam)

仅 **DeepSeek-V3.2** 和 **GLM-5.1** 模型支持。配置路径：

```json
"fcParam": {
  "pluginFCParam": {
    "pluginList": [
      {
        "pluginID": "{{PLUGIN_ID}}",
        "pluginName": "{{PLUGIN_NAME}}",
        "apiInfoList": [
          {
            "apiID": "{{API_ID}}",
            "apiName": "{{API_NAME}}",
            "description": "{{DESCRIPTION}}"
          }
        ]
      }
    ]
  }
}
```

同时必须在 `_temp.externalData.skills` 中镜像：

```json
"skills": [
  {
    "type": 1,
    "pluginName": "{{PLUGIN_NAME}}",
    "icon": "{{PLUGIN_ICON_URL}}"
  }
]
```

---

## spaceId 获取指引

当工作流使用了**插件节点(type=4)**、**数据库节点(12/42/43/44/46)**或**知识库节点(6/27)**时，必须获取用户的 spaceId。

**获取方式**：请用户粘贴原力平台工作空间的浏览器地址栏 URL，格式如：

```
https://ai-force.duxiaoman-int.com/space/7563588980457865216/...
```

从 URL 中提取 `space/` 后面的数字串（如 `7563588980457865216`）即为 spaceId。

**在 JSON 中的使用位置**：
- 顶层 `source.spaceId`
- 插件节点的 `spaceId`（节点顶层字段）
- 插件节点 `_temp.externalData.spaceID`

---

### 飞书消息 — 补充 API（pluginID: `15`）

> 以下 API 与已收录的 send_webhook_message 同属「飞书消息」插件（pluginID: `15`）。

#### get_chat_messages

- **apiID**: `150001`
- **描述**: 获取指定单聊、群聊的消息历史

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `appid` | string | 选填 | 飞书开放平台应用ID |
| `appsecret` | string | 选填 | 应用秘钥 |
| `container_id` | string | 必填 | 群聊或单聊的ID |
| `start_time` | string | 选填 | 起始时间，格式"2006-01-02 15:04:05" |
| `end_time` | string | 选填 | 结束时间，格式"2006-01-02 15:04:05" |
| `sort_type` | string | 选填 | 排序：ByCreateTimeAsc/ByCreateTimeDesc |
| `page_size` | integer | 选填 | 分页大小，默认20，范围[1,50] |
| `page_token` | string | 选填 | 分页标记 |
| `tenant_access_token` | string | 选填 | 租户访问凭证 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含items(消息列表)/has_more/page_token |
| `log_id` | string | 链路追踪id |

#### get_thread_messages

- **apiID**: `15002`
- **描述**: 获取指定话题的消息历史

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `appid` | string | 选填 | 飞书开放平台应用ID |
| `appsecret` | string | 选填 | 应用秘钥 |
| `container_id` | string | 必填 | 话题ID(thread_id) |
| `start_time` | string | 选填 | 起始时间，格式"2006-01-02 15:04:05" |
| `end_time` | string | 选填 | 结束时间，格式"2006-01-02 15:04:05" |
| `sort_type` | string | 选填 | 排序：ByCreateTimeAsc/ByCreateTimeDesc |
| `page_size` | integer | 选填 | 分页大小，默认20，范围[1,50] |
| `page_token` | string | 选填 | 分页标记 |
| `tenant_access_token` | string | 选填 | 租户访问凭证 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含items(消息列表)/has_more/page_token |
| `log_id` | string | 链路追踪id |

#### send_bot_message

- **apiID**: `150003`
- **描述**: 使用应用机器人发送飞书消息

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `tenant_access_token` | string | 选填 | 租户访问凭证 |
| `receive_id_type` | string | 必填 | 用户ID类型：open_id/union_id/user_id/email/chat_id |
| `appid` | string | 选填 | 飞书开放平台应用ID |
| `appsecret` | string | 选填 | 应用秘钥 |
| `content` | string | 必填 | 消息内容，文本或JSON序列化字符串 |
| `msg_type` | string | 必填 | 消息类型：text/post/image/file/interactive等 |
| `receive_id` | string | 必填 | 消息接收者ID |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含message_id/chat_id/msg_type/create_time等 |
| `log_id` | string | 链路追踪id |

<details>
<summary>飞书消息 apiParam 配置片段（点击展开）— 所有 API 共用 pluginID/pluginName，仅 apiID/apiName 不同</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "150001", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书消息", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "15", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书消息", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

各 API 的 apiID 对照：

| apiID | title | 说明 |
|-------|-------|------|
| `150001` | get_chat_messages | 获取指定单聊、群聊的消息历史 |
| `15002` | get_thread_messages | 获取指定话题的消息历史 |
| `150003` | send_bot_message | 使用应用机器人发送飞书消息 |
| `150004` | send_webhook_message | Webhook发送消息(已收录) |

</details>

### 飞书任务（pluginID: `18`）

> 支持创建/更新/删除/列取飞书任务。

#### create_task

- **apiID**: `180001`
- **描述**: 创建飞书任务

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `summary` | string | 必填 | 任务标题 |
| `completed_at` | string | 选填 | 完成时间，格式"2006-01-02 15:04:05"，不填为未完成 |
| `description` | string | 选填 | 任务备注 |
| `end_time` | string | 选填 | 结束时间，格式"2006-01-02 15:04:05" |
| `start_time` | string | 选填 | 开始时间，格式"2006-01-02 15:04:05" |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含guid/task_id/summary/status/url/members等 |
| `log_id` | string | 链路追踪id |

#### delete_task

- **apiID**: `180002`
- **描述**: 删除飞书任务

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `task_guid` | string | 必填 | 任务guid，支持传任务ID或任务链接URL |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer | 错误码 |
| `msg` | string | 错误描述 |
| `log_id` | string | 链路追踪id |

#### list_tasks

- **apiID**: `180003`
- **描述**: 列取飞书任务列表

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `user_id_type` | string | 选填 | 用户ID类型 |
| `page_size` | integer | 选填 | 每页任务数，范围1-100 |
| `page_token` | string | 选填 | 分页标记 |
| `completed` | boolean | 选填 | 是否按完成状态过滤(true=已完成/false=未完成) |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含items(任务列表)/has_more/page_token |
| `log_id` | string | 链路追踪id |

#### update_task

- **apiID**: `180004`
- **描述**: 更新飞书任务

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `task_guid` | string | 必填 | 任务guid，支持传任务ID或任务链接URL |
| `summary` | string | 选填 | 任务标题 |
| `description` | string | 选填 | 任务描述 |
| `start_time` | string | 选填 | 开始时间，格式"2024-08-15 23:00:00" |
| `end_time` | string | 选填 | 结束时间，格式"2024-08-15 23:20:00" |
| `completed_time` | string | 选填 | 完成时间，格式"2024-08-19 11:20:00" |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含task_guid/summary/start_time/end_time/updated_at等 |
| `log_id` | string | 链路追踪id |

<details>
<summary>飞书任务 apiParam 配置片段（点击展开）— 所有 API 共用 pluginID/pluginName，仅 apiID/apiName 不同</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "180001", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书任务", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "18", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书任务", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

各 API 的 apiID 对照：

| apiID | title | 说明 |
|-------|-------|------|
| `180001` | create_task | 创建飞书任务 |
| `180002` | delete_task | 删除飞书任务 |
| `180003` | list_tasks | 列取飞书任务列表 |
| `180004` | update_task | 更新飞书任务 |

</details>

### 飞书云文档（pluginID: `19`）

> 支持创建/写入/获取文档内容、搜索文档/PPT、上传下载素材。document_id 参数支持传 URL。

#### create_document

- **apiID**: `190001`
- **描述**: 创建文档，支持创建空文档和带内容的文档，支持markdown语法

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `content` | string | 选填 | 文档内容，支持markdown语法 |
| `folder_token` | string | 选填 | 所在文件夹Token，支持URL，不传表示根目录 |
| `title` | string | 选填 | 文档标题，纯文本 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含token/title/type/url |
| `log_id` | string | 链路追踪id |

#### get_document_content

- **apiID**: `190002`
- **描述**: 获取文档内容，支持纯文本或markdown格式返回

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `document_id` | string | 必填 | 文档唯一标识，支持URL |
| `lang` | integer | 选填 | @用户语言(0默认/1英文) |
| `mode` | string | 选填 | 返回格式：text/markdown，默认markdown |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含content(文档内容) |
| `log_id` | string | 链路追踪id |

#### get_document_info

- **apiID**: `190003`
- **描述**: 获取文档的基本信息

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `document_id` | string | 必填 | 文档唯一标识，支持URL |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含document(document_id/title) |
| `log_id` | string | 链路追踪id |

#### list_document_blocks

- **apiID**: `190004`
- **描述**: 获取文档所有块的富文本内容并分页返回

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `document_id` | string | 必填 | 文档唯一标识，支持URL |
| `document_revision_id` | integer | 选填 | 文档版本，-1为最新版 |
| `user_id_type` | string | 选填 | 用户ID类型：open_id/union_id/user_id |
| `page_size` | integer | 选填 | 分页大小 |
| `page_token` | string | 选填 | 分页标记 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含items(Block列表)/has_more/page_token |
| `log_id` | string | 链路追踪id |

#### search_document

- **apiID**: `190005`
- **描述**: 搜索文档类型的文档

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `search_key` | string | 必填 | 搜索关键字 |
| `count` | integer | 选填 | 返回文件数量，范围[0,50] |
| `offset` | integer | 选填 | 搜索偏移量，offset+count<200 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含docs_entities(文件列表)/has_more/total |
| `log_id` | string | 链路追踪id |

#### search_slides

- **apiID**: `190006`
- **描述**: 搜索PPT类型的文档

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `search_key` | string | 必填 | 搜索关键字 |
| `count` | integer | 选填 | 返回文件数量，范围[0,50] |
| `offset` | integer | 选填 | 搜索偏移量 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含docs_entities(文件列表)/has_more/total |
| `log_id` | string | 链路追踪id |

#### write_document

- **apiID**: `190007`
- **描述**: 在文档中新增内容，支持纯文本或markdown格式

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `document_id` | string | 必填 | 文档唯一标识，支持URL |
| `content` | string | 必填 | 纯文本或markdown内容 |
| `position` | string | 选填 | 添加位置：start/end，默认end |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer | 错误码 |
| `msg` | string | 错误描述 |
| `log_id` | string | 链路追踪id |

#### download_media

- **apiID**: `190008`
- **描述**: 下载素材

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `file_token` | string | 必填 | 素材唯一标识 |
| `extra` | string | 选填 | 额外鉴权参数(高级权限多维表格) |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 失败描述 |
| `data` | object | 含file_base64/file_name/file_token |
| `log_id` | string | 链路追踪id |

#### upload_media

- **apiID**: `190009`
- **描述**: 上传素材到飞书云文档/多维表格/电子表格，获取file_token

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `parent_type` | string | 必填 | 上传点类型：如"docx_image"/"bitable_image" |
| `file_name` | string | 必填 | 素材名称，如"demo.jpeg"，最大250字符 |
| `file_url` | string | 必填 | 待上传素材的公开链接 |
| `parent_node` | string | 必填 | 上传目标云文档token，支持URL |
| `extra` | string | 选填 | 额外参数 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含file_token(上传素材唯一标识) |
| `log_id` | string | 链路追踪id |

<details>
<summary>飞书云文档 apiParam 配置片段（点击展开）— 所有 API 共用 pluginID/pluginName，仅 apiID/apiName 不同</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "190001", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书云文档", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "19", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书云文档", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

各 API 的 apiID 对照：

| apiID | title | 说明 |
|-------|-------|------|
| `190001` | create_document | 创建文档，支持创建空文档和带内容的文档，支持markdown |
| `190002` | get_document_content | 获取文档内容，支持纯文本或markdown格式返回 |
| `190003` | get_document_info | 获取文档的基本信息 |
| `190004` | list_document_blocks | 获取文档所有块的富文本内容并分页返回 |
| `190005` | search_document | 搜索文档类型的文档 |
| `190006` | search_slides | 搜索PPT类型的文档 |
| `190007` | write_document | 在文档中新增内容，支持纯文本或markdown格式 |
| `190008` | download_media | 下载素材 |
| `190009` | upload_media | 上传素材到飞书云文档/多维表格/电子表格，获取file_to |

</details>

### 飞书日历（pluginID: `21`）

> 在飞书日历上创建/更新/删除/查询日程。时间格式统一为 `yyyy-MM-dd HH:mm:ss`。

#### create_event

- **apiID**: `210001`
- **描述**: 创建日程

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `summary` | string | 选填 | 日程标题，不填显示(无主题) |
| `start_time` | string | 必填 | 开始时间，格式"2006-01-02 15:04:05" |
| `end_time` | string | 必填 | 结束时间，格式"2006-01-02 15:04:05" |
| `description` | string | 选填 | 日程描述 |
| `need_notification` | boolean | 选填 | 是否发送bot消息 |
| `auto_record` | boolean | 选填 | 是否开启自动录制 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 返回信息 |
| `data` | object | 含event_id/summary/start_time/end_time/appLink/status等 |
| `log_id` | string | 日志id |

#### delete_event

- **apiID**: `210002`
- **描述**: 删除日程

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `event_id` | string | 必填 | 日程ID |
| `need_notification` | string | 选填 | 是否发送Bot通知 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer | 错误码 |
| `msg` | string | 错误描述 |
| `log_id` | string | 链路追踪id |

#### get_primary_calendar

- **apiID**: `210003`
- **描述**: 查询主日历信息

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `user_id_type` | string | 选填 | 用户ID类型 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含calendars列表(calendar_id/summary/permissions/type等) |
| `log_id` | string | 链路追踪id |

#### list_events

- **apiID**: `210004`
- **描述**: 获取日程列表

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `start_time` | string | 选填 | 开始时间，默认当天0点，格式"yyyy-MM-dd HH:mm:ss" |
| `end_time` | string | 选填 | 结束时间，默认当天23:59，格式"yyyy-MM-dd HH:mm:ss" |
| `page_size` | string | 选填 | 每次返回的最大日程数，范围50-1000 |
| `page_token` | string | 选填 | 分页标记 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer | 错误码 |
| `msg` | string | 错误描述 |
| `data` | object | 含items(日程列表)/has_more/page_token |
| `log_id` | string | 链路追踪id |

#### search_events

- **apiID**: `210005`
- **描述**: 搜索日程

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `query` | string | 必填 | 搜索关键字，最大200字符 |
| `start_time` | string | 选填 | 搜索区间开始，默认当天0点，格式"2024-08-01 10:00:00" |
| `end_time` | string | 选填 | 搜索区间结束，默认当天23:59 |
| `user_id_type` | string | 选填 | 用户ID类型：open_id/union_id/user_id |
| `page_size` | integer | 选填 | 每次返回最大日程数，最大100 |
| `page_token` | string | 选填 | 分页标记 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | integer | 错误码 |
| `msg` | string | 错误信息 |
| `data` | object | 含items(日程列表)/page_token |
| `log_id` | string | 日志ID |

#### update_event

- **apiID**: `210006`
- **描述**: 更新日程

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `event_id` | string | 必填 | 日程ID |
| `summary` | string | 选填 | 日程标题 |
| `description` | string | 选填 | 日程描述 |
| `start_time` | string | 选填 | 开始时间，格式"2024-07-22 22:30:00" |
| `end_time` | string | 选填 | 结束时间 |
| `need_notification` | boolean | 选填 | 是否发送bot消息 |
| `auto_record` | boolean | 选填 | 是否开启自动录制 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `log_id` | string | 链路追踪id |

<details>
<summary>飞书日历 apiParam 配置片段（点击展开）— 所有 API 共用 pluginID/pluginName，仅 apiID/apiName 不同</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "210001", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书日历", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "21", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书日历", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

各 API 的 apiID 对照：

| apiID | title | 说明 |
|-------|-------|------|
| `210001` | create_event | 创建日程 |
| `210002` | delete_event | 删除日程 |
| `210003` | get_primary_calendar | 查询主日历信息 |
| `210004` | list_events | 获取日程列表 |
| `210005` | search_events | 搜索日程 |
| `210006` | update_event | 更新日程 |

</details>

### 飞书认证及授权（pluginID: `14`）

> 获取 tenant_access_token，供飞书消息等需要凭证的 API 使用。有效期 2 小时。

#### get_tenant_access_token

- **apiID**: `140001`
- **描述**: 获取租户访问凭证(tenant_access_token)，有效期2小时

**输入参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `app_id` | string | 必填 | 应用唯一标识 |
| `app_secret` | string | 必填 | 应用秘钥 |

**输出参数**:

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `code` | float | 错误码 |
| `msg` | string | 错误描述 |
| `tenant_access_token` | string | 租户访问凭证 |
| `expire` | float | 过期时间(秒) |
| `log_id` | string | 链路追踪id |

<details>
<summary>飞书认证及授权 apiParam 配置片段（点击展开）— 所有 API 共用 pluginID/pluginName，仅 apiID/apiName 不同</summary>

```json
"apiParam": [
  { "name": "apiID", "input": { "type": "string", "value": { "type": "literal", "content": "140001", "rawMeta": { "type": 1 } } } },
  { "name": "apiName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书认证及授权", "rawMeta": { "type": 1 } } } },
  { "name": "pluginID", "input": { "type": "string", "value": { "type": "literal", "content": "14", "rawMeta": { "type": 1 } } } },
  { "name": "pluginName", "input": { "type": "string", "value": { "type": "literal", "content": "飞书认证及授权", "rawMeta": { "type": 1 } } } },
  { "name": "pluginVersion", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "tips", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } },
  { "name": "outDocLink", "input": { "type": "string", "value": { "type": "literal", "content": "", "rawMeta": { "type": 1 } } } }
]
```

各 API 的 apiID 对照：

| apiID | title | 说明 |
|-------|-------|------|
| `140001` | get_tenant_access_token | 获取租户访问凭证(tenant_access_token)， |

</details>

## 插件选型决策树

```
需求是什么？
├── 搜索网页信息
│   ├── 需要AI总结 → 百度智能搜索(AI搜索生成)
│   ├── 只要搜索结果 → 博查搜索 或 百度智能搜索(网页搜索)
│   └── 热榜/趋势 → 百度智能搜索(媒体热榜/垂类热榜)
├── 读取网页/文档内容
│   ├── 纯网页 → 内容读取(LinkReader)
│   └── 含视频平台 → scrape网页抓取
├── OCR图片识别
│   ├── 身份证 → 身份证OCR
│   ├── 发票 → 发票OCR
│   ├── 个税 → 个税OCR
│   ├── 完税证明 → 完税证明OCR
│   ├── 学历学位证书 → 学历学位证书OCR
│   ├── 芝麻分截图 → 芝麻分OCR
│   ├── 微信分截图 → 微信分OCR
│   └── 竞品offer截图 → 竞品offer OCR
├── 语音/音频
│   ├── 文字→语音 → TTS
│   ├── 语音→文字 → ASR
│   ├── 声学事件识别 → AED
│   ├── 会议纪要(多人) → speech_meeting
│   └── 生成播客音频 → 语音播客
├── 获取时间
│   ├── 当前时间 → 时间类工具包
│   └── 日期计算(T-N等) → get_time
├── 内容生成
│   ├── 生成图片 → Doubao图像生成
│   └── 生成PPT → ChatPPT
├── 数据库查询
│   ├── MySQL → mysql_reader
│   └── Doris → 鸿鹄插件
├── 品牌声量分析 → 品牌社媒声量查询
├── 新闻热点 → 搜狐热闻
└── 代码分析 → SpecCoder
├── 飞书电子表格
│   ├── 创建表格 → create_spreadsheet (170003)
│   ├── 读取数据 → read_table (170010) / read_rows (170009) / read_cols (170008)
│   ├── 新增行列 → add_rows (170002) / add_cols (170001)
│   ├── 删除行列 → delete_rows (170005) / delete_cols (170004)
│   ├── 获取表格信息 → get_spreadsheet (170006) / list_spreadsheet_sheets (170007)
│   └── 搜索表格 → search_spreadsheet (170011)
├── 飞书多维表格
│   ├── 创建 → create_base (160003) / create_table (160004)
│   ├── 查询记录 → search_record (160012)
│   ├── 新增记录 → add_records (160002)
│   ├── 更新记录 → update_records (160014)
│   ├── 删除记录 → delete_records (160006)
│   ├── 字段管理 → add_field/update_field/delete_field/list_fields
│   ├── 表管理 → list_tables/delete_tables/get_base_info
│   └── 搜索 → search_base (160011)
├── 飞书知识库
│   └── 搜索Wiki → search_wiki (200001)
├── 飞书消息
│   ├── Webhook 发送 → send_webhook_message (150004)
│   ├── 机器人发送 → send_bot_message (150003)
│   ├── 群聊/单聊历史 → get_chat_messages (150001)
│   └── 话题消息历史 → get_thread_messages (15002)
├── 飞书任务
│   ├── 创建/更新任务 → create_task (180001) / update_task (180004)
│   ├── 删除任务 → delete_task (180002)
│   └── 列取所有任务 → list_tasks (180003)
├── 飞书云文档
│   ├── 创建文档 → create_document (190001)
│   ├── 读取内容 → get_document_content (190002)
│   ├── 写入内容 → write_document (190007)
│   ├── 搜索文档/PPT → search_document (190005) / search_slides (190006)
│   ├── 获取块/基本信息 → list_document_blocks (190004) / get_document_info (190003)
│   └── 素材上传下载 → upload_media (190009) / download_media (190008)
├── 飞书日历
│   ├── 创建/更新日程 → create_event (210001) / update_event (210006)
│   ├── 删除日程 → delete_event (210002)
│   ├── 查询日程列表 → list_events (210004)
│   ├── 搜索日程 → search_events (210005)
│   └── 主日历信息 → get_primary_calendar (210003)
└── 飞书认证
    └── 获取 tenant_access_token → get_tenant_access_token (140001)
```