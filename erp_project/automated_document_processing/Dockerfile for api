# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for OCR (Tesseract) and PDF handling (pdfplumber dependencies)
# We need tesseract-ocr and necessary libraries for handling images and PDFs
RUN apt-get update && \
    apt-get install -y libpoppler-cpp-dev libtesseract-dev poppler-utils tesseract-ocr \
    # Clean up to keep the image small
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY document_processor_flask_api.py .

# The application is configured to listen on the Hugging Face default port 7860
ENV PORT 7860
EXPOSE 7860

# Define the command to run the application using gunicorn for production reliability
# gunicorn is a WSGI HTTP Server that's more robust than Flask's built-in server.
# The format is: gunicorn -w [workers] -b 0.0.0.0:[PORT] [module_name]:[flask_app_variable]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "document_processor_flask_api:app"]
