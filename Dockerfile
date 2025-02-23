# Use an official Python runtime as the base image.
FROM python:3.9-slim

# Set the working directory.
WORKDIR /app

# Copy the requirements file and install dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Expose port 5000 to the outside world.
EXPOSE 5000

# Define environment variable to tell Flask it's running in production mode (optional)
ENV FLASK_ENV=production

# Run the Flask application.
CMD ["python", "app.py"]
