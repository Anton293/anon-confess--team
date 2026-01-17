FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
#CMD ["uvicorn", "src.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--uds", "/run/anon/backend.sock", "--proxy-headers"]

EXPOSE 8000