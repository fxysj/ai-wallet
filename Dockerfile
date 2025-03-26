# 使用 Python 3.10 官方镜像
FROM python:3.10-slim-buster

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/tikeAgent \
    PIP_CACHE_DIR=/root/.cache/pip \
    ENV_FILE=/tikeAgent/.env

# 设置工作目录
WORKDIR /tikeAgent

# 先单独复制依赖列表（利用缓存层）
COPY ./app/requirements.txt .

# 安装依赖（requirements.txt 不变时跳过）
RUN pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 再复制项目所有文件（频繁变动的步骤放最后）
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "app/main.py"]