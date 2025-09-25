﻿FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY agent ./agent
COPY README.md ./README.md
EXPOSE 8080
CMD ["uvicorn", "agent.main:app", "--host", "0.0.0.0", "--port", "8080"]
