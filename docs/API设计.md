# 一、整体 API 设计原则

1. **poetry = 工具层（Tool API）**

   * 可被前端直接调用
   * 也可被 Agent 调用
2. **agent = 智能层（Orchestration）**

   * 不直接暴露数据库
   * 只组合、调度工具
3. **Agent 不“查数据库”，Agent“调用工具”**

---

# 统一响应结构

```json
{
  "code": 200,
  "message": "success",
  "data": [...]
}
```
字段说明:

|字段名 |	类型 | 说明 |
| ---- | ---  | ---- |
| code | integer	|状态码，200 表示成功 |
| message	| string	| 状态说明 |
|data |	json |	业务数据 |

---

# 二、Poetry API（基础能力层）

文件位置：

```
backend/app/api/poetry.py
backend/app/services/poetry_service.py
```

---

## 1️. 检索诗词

该接口用于根据用户输入的查询文本，从诗词库中检索相关诗词，支持三种检索模式：

- 关键词搜索（keyword）：基于 MySQL LIKE 的文本匹配

- 向量搜索（vector）：基于 Embedding + Milvus 的语义相似度检索

- 混合搜索（hybrid）（默认）：关键词搜索与向量搜索结果合并去重

### Endpoint

```http
POST /api/poetry/search
```


### 请求体（Request Body）
```json
{
  "query": "明月",
  "search_type": "hybrid",
  "top_k": 5
}
```

### 参数说明
| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--- | ---- |  ---| ----   |  --- |
| query |	string	| 是 |	-	 | 搜索关键词或查询文本 |
|search_type |	string |	否	| hybrid	| 搜索模式：keyword /  vector / hybrid |
| top_k	| integer	| 否 |	5 |	返回的最大诗词数量 |

### 响应格式
 
5. 返回数据结构（PoetrySearchItem）
```json
{
  "id": 123,
  "title": "静夜思",
  "dynasty": "唐",
  "writer": "李白",
  "content": "床前明月光，疑是地上霜。"
}
```

### 字段说明
| 字段名 | 类型 | 说明 |
| ----- | ----- | --- |
|id | integer	| 诗词唯一 ID |
| title	| string | 诗词标题 |
| dynasty	| string | 朝代 |
| writer |string |作者 |
| content	| string | 诗词正文 |



---

# 三、Agent API（智能编排层）


---

# 四、Agent Prompt 设计

Agent System Prompt 核心思想：

```text
你是一个中文古诗词智能助手。
你不能编造诗词。
所有诗词必须来自工具返回结果。
你需要根据用户意图选择合适的工具。
```

---

# 五、Tool（函数）

Agent 可调用的 Tool 列表：

```json
[
  "keyword_search_poetry",
  "semantic_search_poetry",
  "search_sentence",
  "get_poetry_detail"
]
```

---
