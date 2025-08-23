FROM python:3.9-slim

WORKDIR /app

# 1. 配置国内源（APT + Pip）
RUN sed -i 's|http://deb.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's|http://security.debian.org|https://mirrors.tuna.tsinghua.edu.cn/debian-security|g' /etc/apt/sources.list.d/debian.sources && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.trusted-host mirrors.tuna.tsinghua.edu.cn

# 2. 安装系统依赖（Python开发工具 + MySQL客户端库）
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev default-libmysqlclient-dev gcc pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 3. 安装Python依赖（含mysqlclient）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    # 安装后清理编译缓存（减小镜像体积）
    rm -rf /root/.cache/pip

# 4. 复制项目代码
COPY manage.py .
COPY app/ ./app/
COPY proj/ ./proj/

# 5. 运行时环境变量
ENV PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:$PATH"

# 6. 启动命令
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
