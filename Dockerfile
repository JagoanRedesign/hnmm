# Use the official Python image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Flask runs on (adjust if needed for your app)
EXPOSE 8000

# Run the Flask app and bot
CMD ["sh", "-c", "python web.py & python main.py"]
