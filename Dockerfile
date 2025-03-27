# 继承基础镜像
FROM registry.cn-hangzhou.aliyuncs.com/sinrpc/mypython:latest
# 设置环境变量
ENV PYTHONPATH=/tikeAgent \
    ENV_FILE=/tikeAgent/.env

# 设置工作目录
WORKDIR /tikeAgent

# 复制项目文件（跳过 requirements.txt，因为依赖已安装）
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "app/main.py"]
