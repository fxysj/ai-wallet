# 使用 Python 3.12 官方镜像
FROM python:3.12-slim-bookworm



# 设置工作目录为 tikeAgent（容器中的路径）
WORKDIR /tikeAgent

# 复制项目文件到容器
COPY . .


# 使用国内 pip 源加速安装依赖
RUN python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install -r app/requirements.txt
# 暴露应用端口（根据实际应用端口调整，例如 8000）
EXPOSE 8000

# 启动应用
CMD ["python", "app/main.py"]
