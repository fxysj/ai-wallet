# 继承基础镜像
FROM registry.cn-hangzhou.aliyuncs.com/sinrpc/mypython:latest
# 设置环境变量
ENV PYTHONPATH=/tikeAgent \
    ENV_FILE=/tikeAgent/.env

# 设置工作目录
WORKDIR /tikeAgent
# Create the necessary directory with correct permissions
RUN mkdir -p /tmp/langchain_qdrant && chmod 777 /tmp/langchain_qdrant

# Alternatively, if you are using a non-root user, set the permissions correctly
# RUN mkdir -p /tmp/langchain_qdrant && chown user:user /tmp/langchain_qdrant

# 复制项目文件（跳过 requirements.txt，因为依赖已安装）
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "app/main.py"]
