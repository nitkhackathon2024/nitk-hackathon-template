# Use the official Python image from the Docker Hub
FROM python:3.11.2-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Set the command to run your application
CMD ["python", "app.py"]

# Expose the port your app runs on
EXPOSE 5000
