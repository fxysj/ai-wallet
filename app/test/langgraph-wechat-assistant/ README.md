
---

# LangGraph 多轮对话情感分析系统

## 🧠 项目背景

本项目旨在构建一个多轮对话式情感分析系统，结合 LangChain 的 LangGraph 构建闭环智能体，支持：

- 用户目标设定、资源感知与计划执行闭环
- 微信小程序 & 企业微信的对接能力
- 实时用户修正与智能提示反馈
- 用户画像 & 智能打标签能力

## 🚀 技术栈

- **LangGraph + LangChain**
- **FastAPI**
- **HuggingFace Transformers**
- **Docker**
- **企业微信 & 微信小程序**
- **Redis + MySQL**
- **OpenTelemetry（分布式链路追踪）**

## 🌐 系统流程图

```mermaid
graph TD
  A[用户输入评论] --> B[语言标准化]
  B --> C[保存用户版本]
  C --> D[情感分析]
  D --> E[版本对比]
  E --> F{情绪是否达标}
  F -->|是| G[输出成功反馈]
  F -->|否| H[建议用户优化反馈]
  G --> I[企业微信/小程序推送反馈]
  H --> I
```

## 🔩 LangGraph 节点代码示例

### 1. Save Version Node

```python
# 🧩 Node: Save version
def save_version(state: AgentState) -> AgentState:
    ver_id = save_data_version(state["user_id"], state["normalized_comments"])
    return {**state, "version_id": ver_id}
```

### 2. Evaluate Target Match Node

```python
# ⚖️ Node: Evaluate target match
def evaluate_result(state: AgentState) -> str:
    ratio = state["analysis_result"].get("positive_ratio", 0)
    return "output_success" if ratio >= 0.9 else "suggest_improve"
```

## 🛠️ 数据库结构设计

### 用户画像表

```sql
CREATE TABLE user_profile (
  user_id VARCHAR(64) PRIMARY KEY,
  nickname VARCHAR(64),
  tags JSON,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 评论版本表

```sql
CREATE TABLE user_comments_version (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(64),
  version_data JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 情感分析结果缓存表

```sql
CREATE TABLE sentiment_result (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(64),
  result_data JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📊 可视化管理后台

使用 `Vite + React`（或 `Vue3`）构建：
- 用户列表、画像查看、标签管理
- 任务执行流程状态跟踪（节点完成状态）
- 历史版本和情感变化趋势图表
- 反馈建议和人工审核接口

## 📡 OpenTelemetry 分布式追踪

在每个 LangGraph 节点中注入 trace span：

```python
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("analyze_sentiment")
def run_sentiment_analysis(state):
    ...
```

并通过 FastAPI middleware 自动追踪外部 API 请求。

启动时支持使用 `.env` 配置：

```env
OPENAI_API_KEY=sk-xxxx
HUGGINGFACE_CACHE_DIR=./models
WECHAT_BOT_URL=https://qyapi.weixin.qq.com/xxx
TELEMETRY_EXPORTER=jaeger
```

## 📱 微信对接方式（小程序 & 企业微信）

### 微信小程序端

- 小程序端调用 FastAPI 接口，传入用户身份标识 + 评论
- 企业微信机器人 Webhook 推送最终反馈结果
- 支持 LangGraph 多用户并发任务处理

### 企业微信机器人推送示例

```python
import requests

def send_wecom_message(user_id, analysis_result, is_success):
    title = "情感目标达成 ✅" if is_success else "请优化表达 😅"
    description = f"当前正面情绪比率：{analysis_result['positive_ratio']:.2f}"
    message = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"## {title}\n> {description}\n用户ID：{user_id}"
        }
    }
    webhook_url = os.getenv("WECHAT_BOT_URL")
    requests.post(webhook_url, json=message)
```

## 🧩 用户实时修正支持

- 用户提供初始目标（如希望正面率达到 90%）
- 每轮反馈后支持 `新的输入 + 修正目标`
- LangGraph 动态更新状态并重评估计划路径

## 🧪 快速启动（含 Docker）

### 环境配置

首先复制 `.env.example` 文件为 `.env` 并根据环境配置 API 密钥、Redis、MySQL 等。

```bash
cp .env.example .env
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker 启动

```bash
docker build -t langgraph-agent .
docker run --env-file .env -p 8000:8000 langgraph-agent
```

## 🚀 完整的 LangGraph Agent 构建方法

### LangGraph Agent 构建

```python
from langchain.agents import initialize_agent, AgentExecutor
from langchain.agents import AgentType
from langchain.prompts import PromptTemplate

# 创建代理所需的工具和节点
def build_langgraph_agent():
    tools = [
        {"name": "sentiment_analysis", "func": analyze_sentiment},
        {"name": "text_standardization", "func": standardize_text},
    ]
    
    agent = initialize_agent(
        tools,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    
    return agent

# 运行情感分析节点
def analyze_sentiment(text: str):
    sentiment_result = {"positive_ratio": 0.8}
    return sentiment_result

# 运行文本标准化节点
def standardize_text(text: str):
    standardized_text = text.lower()
    return standardized_text
```

### 执行代理任务

```python
from langgraph_agent import build_langgraph_agent

# 构建 LangGraph 代理
agent = build_langgraph_agent()

# 执行用户输入的任务
def execute_user_task(user_input: str):
    result = agent.run(user_input)
    return result
```

## 🚀 企业部署方案

### 1. 容器化部署（Docker）

#### Dockerfile

```Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `.env` 文件

```env
OPENAI_API_KEY=sk-xxxx
HUGGINGFACE_API_KEY=hf-xxxx
MYSQL_URL=mysql+pymysql://user:password@host:3306/langgraph
REDIS_URL=redis://localhost:6379/0
WECHAT_BOT_URL=https://qyapi.weixin.qq.com/xxx
```

#### 生产环境部署

构建 Docker 镜像：

```bash
docker build -t langgraph-agent .
```

启动容器：

```bash
docker run --env-file .env -p 8000:8000 langgraph-agent
```

### 2. 高可用架构（Kubernetes 部署）

#### Kubernetes 配置文件

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langgraph-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: langgraph-agent
  template:
    metadata:
      labels:
        app: langgraph-agent
    spec:
      containers:
        - name: langgraph-agent
          image: yourdockerhub/langgraph-agent:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: langgraph-env
---
apiVersion: v1
kind: Service
metadata:
  name: langgraph-api
spec:
  selector:
    app: langgraph-agent
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

---

## ✅ TODO

- [✅] LangGraph 多轮闭环任务系统
- [✅] 支持并行节点处理
- [✅] 用户画像系统 & 打标签
- [✅] LangSmith 集成调试 & OpenTelemetry 链路可视化
- [✅] UI 管理后台部署
- [✅] 微信小程序身份同步对接

---
📮 联系作者
邮箱：986244259@qq.com

