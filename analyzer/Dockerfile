FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY analyzer.py .
RUN mkdir -p /app/queue /app/results /app/database
CMD ["python", "analyzer.py"]
