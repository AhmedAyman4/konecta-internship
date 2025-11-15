# Use an official Python slim image
# It's better to use a specific, stable version like 3.11 for reproducibility
FROM python:3.11-slim as base

# Install system dependencies for Pillow, Tesseract OCR, and common build tools
# We use only one 'tesseract-ocr' and 'libtesseract-dev' for clarity and to avoid duplicates.
# 'tesseract-ocr-eng' installs the English language data.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       build-essential \
       git \
       tesseract-ocr \
       libtesseract-dev \
       libleptonica-dev \
       tesseract-ocr-eng \
       pkg-config \
       poppler-utils \
       ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
# 'pip install --no-cache-dir' is good, and you should ensure your 'requirements.txt' 
# includes 'pytesseract', 'Pillow', 'langchain-google-genai', 'streamlit', and 'python-dotenv'.
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy the app code
# The code structure in the image (stream_invoice.py, requirements.txt, etc.) is correct for this step.
COPY . /app

# Expose Streamlit default port (required by Docker, but HF handles it)
EXPOSE 8501

# Recommended environment variables
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_ENABLE_CORS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Default command to run the app
# Ensure the file name 'stream_invoice.py' is correct (which it is, according to the image)
# CMD ["streamlit", "run", "stream_invoice.py", "--server.port", "7860", "--server.address", "0.0.0.0"]
# IMPORTANT: Use port 7860 for Hugging Face Spaces deployment
CMD ["streamlit", "run", "stream_invoice.py", \
     "--server.port", "7860", \
     "--server.address", "0.0.0.0", \
     "--server.enableXsrfProtection", "false"]
# IMPORTANT: Hugging Face Spaces typically expects the app to run on port 7860.
# While Streamlit defaults to 8501, using 7860 is safer for HF Spaces environment.