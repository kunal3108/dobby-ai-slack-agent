# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY slack_listener/ ./slack_listener/
COPY requirements.txt .
COPY README.md .
COPY main.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Python prints immediately (no buffering)
ENV PYTHONUNBUFFERED=1

# Run main
CMD ["python", "main.py"]
