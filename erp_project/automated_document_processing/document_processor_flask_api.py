import os
import io
from dotenv import load_dotenv
from PIL import Image
import numpy as np
import pytesseract
from langchain_google_genai import ChatGoogleGenerativeAI
from sentence_transformers import SentenceTransformer
import json
from pymongo import MongoClient
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile

# Load environment variables
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
mongo_uri = os.getenv("MONGO_URI")

# MongoDB setup
client = MongoClient(mongo_uri)
db = client["invoice_reader_db"]
# Define collections for each document type
collections = {
    "invoice": db["invoices"],
    "purchase_order": db["purchase_orders"],
    "approval": db["approvals"]
}

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# LLM setup
llm = ChatGoogleGenerativeAI(
    google_api_key=google_api_key,
    temperature=0.1,
    max_retries=2,
    convert_system_message_to_human=True,
    model="gemini-2.5-flash"
)

# Set cache directories
os.environ["HF_HOME"] = "/tmp/huggingface"
os.environ["TRANSFORMERS_CACHE"] = "/tmp/huggingface"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = "/tmp/sentence_transformers"
print("Model cache directory:", os.environ["HF_HOME"])

# Load embedding model
embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file_stream, filename):
    """Extract text from uploaded file"""
    try:
        if filename.lower().endswith(".pdf"):
            import pdfplumber
            text = ""
            with pdfplumber.open(file_stream) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text.strip()
        else:  # image case
            image = Image.open(file_stream)
            gray_image = image.convert("L")
            extracted_text = pytesseract.image_to_string(gray_image).strip()
            return extracted_text
    except Exception as e:
        raise Exception(f"Error extracting text: {str(e)}")

# Function to detect document type
def detect_document_type(text):
    """Use Gemini to classify document type"""
    classification_prompt = f"""
    You are a document classifier. Based on the text below, classify the document type into one of the following categories:
    - invoice
    - purchase_order
    - approval
    Respond with ONLY one of these words and nothing else.

    Document text:
    {text[:3000]}  # limit text length for efficiency
    """

    response = llm.invoke(classification_prompt)
    doc_type = response.content.strip().lower()

    if "invoice" in doc_type:
        return "invoice"
    elif "purchase" in doc_type or "order" in doc_type:
        return "purchase_order"
    elif "approval" in doc_type:
        return "approval"
    else:
        return "invoice"  # default fallback

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "message": "Document Processing API",
        "endpoints": {
            "POST /api/extract": "Upload and extract document info (invoice, PO, approval)",
            "GET /api/<type>": "Get all documents by type (invoices, purchase_orders, approvals)"
        }
    }), 200

@app.route('/api/extract', methods=['POST'])
def extract_document():
    """Extract information and classify document"""
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, pdf"}), 400
    
    try:
        filename = secure_filename(file.filename)
        extracted_text = extract_text_from_file(file.stream, filename)
        
        if not extracted_text:
            return jsonify({"error": "No text could be extracted from the file"}), 400
        
        # 🆕 Step 1: Detect document type
        document_type = detect_document_type(extracted_text)
        collection = collections[document_type]

        # Step 2: Extract structured data
        message = f"""
        system: You are a document information extractor that converts text into structured JSON data.
        user: {extracted_text}
        """
        response = llm.invoke(message)
        result = response.content.strip().replace("```json", "").replace("```", "")
        json_data = json.loads(result)
        
        # Step 3: Create embeddings
        embedding_vector = embedding_model.encode(extracted_text).tolist()
        
        # Step 4: Check duplicates
        existing_doc = collection.find_one({
            "$or": [
                {"file_name": filename},
                {"extracted_text": extracted_text}
            ]
        })
        
        if existing_doc:
            return jsonify({
                "warning": "Document already exists in database",
                "existing_id": str(existing_doc["_id"]),
                "document_type": document_type,
                "extracted_text": extracted_text,
                "document_data": json_data
            }), 200
        
        # Step 5: Store in the correct collection
        insert_result = collection.insert_one({
            "file_name": filename,
            "document_type": document_type,
            "extracted_text": extracted_text,
            "document_data": json_data,
            "embedding": embedding_vector
        })
        
        return jsonify({
            "success": True,
            "message": f"{document_type.replace('_', ' ').title()} processed successfully",
            "mongodb_id": str(insert_result.inserted_id),
            "document_type": document_type,
            "extracted_text": extracted_text,
            "document_data": json_data
        }), 201
        
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON response from AI model"}), 500
    except Exception as e:
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

@app.route('/api/<doc_type>', methods=['GET'])
def get_all_documents(doc_type):
    """Get all documents of a specific type"""
    if doc_type not in collections:
        return jsonify({"error": "Invalid document type"}), 400

    try:
        docs = list(collections[doc_type].find({}, {"embedding": 0}))
        for d in docs:
            d["_id"] = str(d["_id"])
        
        return jsonify({
            "document_type": doc_type,
            "count": len(docs),
            "documents": docs
        }), 200
    except Exception as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500



@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

# if __name__ == '__main__':
#     # Run the Flask app
#     port = int(os.getenv("PORT", 5000))
#     app.run(host='0.0.0.0', port=port, debug=True)

if __name__ == '__main__':
    # Run the Flask app, prioritizing the Hugging Face default port 7860
    # The port is often set by the environment in deployment
    port = int(os.getenv("PORT", 7860)) 
    app.run(host='0.0.0.0', port=port, debug=False) # debug=False for production