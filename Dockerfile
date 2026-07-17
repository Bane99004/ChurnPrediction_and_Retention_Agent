#Use official Python slim image - smaller, faster
FROM python:3.12-slim

# RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

#Copy requirements first (docker layer caching - dont change this order)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#Copy application code
COPY . .

#Expose Fastapi port
EXPOSE 8000

#Run the api
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

