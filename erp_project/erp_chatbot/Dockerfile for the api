# Use the official Python image as a base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies, including gunicorn for production serving
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file into the container
# Assuming your Python code is saved as 'erp_chatbot_api.py'
COPY erp_chatbot_api.py .

# Expose the port your Flask app is configured to listen on (7860)
# Hugging Face Spaces automatically maps this port.
EXPOSE 7860

# Command to run the application using Gunicorn
# 'app:app' means running the 'app' object from the 'app.py' file.
# We bind it to 0.0.0.0 on the standard port 7860 for HF Spaces.
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "erp_chatbot_api:app"]
