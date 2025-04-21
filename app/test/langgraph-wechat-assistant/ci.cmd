# 构建镜像
docker build -t langgraph-wechat .

# 运行容器（注意端口和 Redis 链接）
docker run -p 8000:8000 -e OPENAI_API_KEY=xxx -e REDIS_HOST=host.docker.internal langgraph-wechat
