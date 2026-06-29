FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask

# Copy the application code into the container
COPY app.py .

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]
