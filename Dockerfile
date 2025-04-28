# 继承基础镜像
FROM registry.cn-hangzhou.aliyuncs.com/sinrpc/mypython:latest
# 设置环境变量
ENV PYTHONPATH=/tikeAgent \
    ENV_FILE=/tikeAgent/.env

# 设置工作目录
WORKDIR /tikeAgent
#进行生成需要的文件格式
RUN mkdir -p /tmp/langchain_qdrant

# 复制项目文件（跳过 requirements.txt，因为依赖已安装）
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "app/main.py"]
