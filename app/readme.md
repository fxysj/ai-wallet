# 交易大模型接口与处理流程

## 交易大模型接口

### `/aynaise/trandellm`

该接口通过大模型进行交易，涉及以下实体和组件：

- **`trandellmRequestEntity`**: 交易大模型请求实体
- **`trandellmResponseEntity`**: 交易大模型响应实体
- **`trandellm`**: 交易大模型本身
- **`trandellmToolsNode`**: 交易大模型的工具节点
- **`trandellmCommonFuncs`**: 交易大模型公用组件库
- **`trandellmTrasformState`**: 交易大模型传输过程中共享的数据，包括：
  - **`messages`**: 历史对话记录
  - **`last_input`**: 最后一次对话内容
  - **`attached_data`**: 用户附带的数据（如前端表单数据、聚合数据等）
  - **`current_indent`**: 当前事件行为类型（用户识别出的意图，枚举值）
  - **`is_signed`**: 是否已经签名成功（若签名成功，则代表真实的钱包区块链交易成功）
  - **`is_valid`**: 本次大模型返回的校验是否合法
  - **`is_complted`**: 本次对话是否结束

---

## 整体架构

### 入口文件

- **`main.py`**: 入口文件，负责应用初始化和启动

### 路由模块

- **`app/api/chat.py`**: 主要路由处理逻辑，包括：
  - 大模型初始化（OpenAI 初始化）
  - 交易对话图（LangGraph）初始化
  - LangGraph 节点初始化
  - LangGraph 工具节点初始化
  - LangGraph 条件边初始化
  - LangGraph 切入点初始化
  - LangGraph 选择条件边初始化
  - 日志组件初始化
  - 上下文管理初始化
  - 工具函数定义
  - 缓存组件初始化
  - 监控日志初始化

---

## 交易大模型处理流程

### 用户输入

```json
{
  "message": "我要转账",
  "attached_data": {}
}
```

### 处理流程

1. **意图解析 (`IntenetPareAgent`)**
   - 根据 `message` 信息，结合提示词模板、用户上下文、区块链领域知识进行解析
   - 更新 `AgentState` 中的 `intent`
   - 识别出 `intent` 后，交由 `ValidaIntentTypeScaheAgent` 进行校验

2. **意图校验 (`ValidaIntentTypeScaheAgent`)**
   - 更新 `AgentState` 中 `is_valid` 状态
   - 若校验成功，则分发给相应的 `IntentRouteAgent`

3. **意图路由 (`IntentRouteAgent`)**
   - 向用户进行多轮对话，确认交易参数
   - 通过 LLM 处理历史对话，并更新 `AgentState`
   - 当交易表单填充完整后，执行相应的业务逻辑

4. **最终返回**
   - 所有返回值均基于 `BaseResult`，结合 `AgentState` 进行封装

---

## 其他说明

- 该架构基于 **FastAPI** 和 **LangGraph** 实现多轮对话系统
- 通过 `AgentState` 维护对话状态，确保交易流程的完整性
- `is_signed` 变量用于标识实际的区块链交易是否成功

--- 

🚀 **快速启动说明**  
1. 在根目录下，运行 `main.py` 启动 FastAPI 应用。
2. 通过 `/aynaise/trandellm` 接口进行交易操作。
3. 确保已经配置好大模型、路由、节点和上下文管理等依赖。
