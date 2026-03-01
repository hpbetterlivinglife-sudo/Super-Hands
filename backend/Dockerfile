# Use official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install the Docker client so the AI can launch sandboxes
RUN apt-get update && apt-get install -y docker.io

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend files
COPY . .

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
