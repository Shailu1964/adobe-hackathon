# Use a specific platform and a slim Python image for efficiency
FROM --platform=linux/amd64 python:3.9-slim

# Set environment variables for non-interactive installs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /

# Install system dependencies (if PyMuPDF or others need them)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt tqdm

# Copy the application code
COPY ./app .

# Create input/output folders if not present
RUN mkdir -p /input /output

# Use a non-root user for security
# RUN useradd -m appuser
# RUN chown -R appuser:appuser /app
# USER appuser

# Default command: process all PDFs in /app/input and write to /app/output
CMD ["python", "main.py"]