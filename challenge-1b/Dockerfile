# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and other necessary files
COPY src ./src
COPY downloa_models.py ./
COPY models ./models
COPY input ./input
COPY output ./output

# Ensure input and output directories exist
RUN mkdir -p /app/input /app/output

# Exclude venv from image
RUN rm -rf /app/venv

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "src/main_1b.py"]
