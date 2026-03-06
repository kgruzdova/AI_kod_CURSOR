FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY api.py .
COPY utils.py .

EXPOSE 8080

ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "api:app"]
