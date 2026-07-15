FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

RUN addgroup --system nexkosmo && adduser --system --ingroup nexkosmo nexkosmo
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chown -R nexkosmo:nexkosmo /app
USER nexkosmo

CMD ["uvicorn", "app.interfaces.http.main:app", "--host", "0.0.0.0", "--port", "8000"]
