# Use a specific platform to meet the requirement [cite: 57]
# Using a slim Python image to keep the final container size down.
FROM --platform=linux/amd64 python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker's layer caching
COPY app/requirements.txt .

# Install the Python dependencies [cite: 86]
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY ./app .

# Command to run the application. It will process all PDFs
# from /app/input and write to /app/output as required [cite: 69]
CMD ["python", "main.py"]