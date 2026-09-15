FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0 PORT=8000 UVICORN_HOST=0.0.0.0 UVICORN_PORT=8000
WORKDIR /app
COPY . .
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
HEALTHCHECK --timeout=5s --retries=3 CMD ["python","-c","import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=3)"]
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
