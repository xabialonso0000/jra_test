FROM python:3.10-slim-bullseye

WORKDIR /app

# LightGBMに必要なシステムライブラリ（libgomp1）をインストール
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# プロジェクトのエントリポイントをモジュールとして実行
CMD ["python", "-m", "main"]