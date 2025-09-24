# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY slack_listener/ ./slack_listener/
COPY nodes/ ./nodes/              # 👈 include nodes (classify, etc.)
COPY tools/ ./tools/              # 👈 include tools (routers, summarize, etc.)
COPY utils/ ./utils/              # 👈 include helpers like secrets_loader.py
COPY requirements.txt .
COPY README.md .
COPY main.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Python prints immediately (no buffering)
ENV PYTHONUNBUFFERED=1

# 👇 AWS Secrets defaults
ENV AWS_DEFAULT_REGION=ap-south-1
ENV SECRET_NAME=dobby-ai-slack-agent-secrets

# Run main
CMD ["python", "main.py"]
