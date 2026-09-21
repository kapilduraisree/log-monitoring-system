FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 7860

ENV PORT=7860
ENV DATABASE_URL=sqlite:///./logs_security.db
ENV SECRET_KEY=logmonitor2024secretkey32charslong
ENV ADMIN_USERNAME=admin
ENV ADMIN_PASSWORD=Admin@12345
ENV FRONTEND_URL=*
ENV ALERT_THRESHOLD=5
ENV MAX_UPLOAD_SIZE_MB=50

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
