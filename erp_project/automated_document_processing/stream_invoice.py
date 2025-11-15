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
import streamlit as st

# ==============================
# Environment & Model Setup
# ==============================

load_dotenv()
google_api_key = os.getenv("GEMINI_API_KEY")
mongo_uri = os.getenv("MONGO_URI")

# MongoDB setup with separate collections
client = MongoClient(mongo_uri)
db = client["invoice_reader_db"]

collections = {
    "invoice": db["invoices"],
    "purchase_order": db["purchase_orders"],
    "approval": db["approvals"]
}

llm = ChatGoogleGenerativeAI(
    google_api_key=google_api_key,
    temperature=0.1,
    max_retries=2,
    convert_system_message_to_human=True,
    model="gemini-2.5-flash"
)

# Set writable cache directories
os.environ["HF_HOME"] = "/tmp/huggingface"
os.environ["TRANSFORMERS_CACHE"] = "/tmp/huggingface"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = "/tmp/sentence_transformers"

embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# ==============================
# Helper Functions
# ==============================

def extract_text_from_file(uploaded_file):
    """Extract text from PDF or image."""
    try:
        if uploaded_file.name.lower().endswith(".pdf"):
            import pdfplumber
            text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text.strip()
        else:
            image = Image.open(uploaded_file)
            gray_image = image.convert("L")
            extracted_text = pytesseract.image_to_string(gray_image).strip()
            return extracted_text
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return None


def detect_document_type(text):
    """Use Gemini to classify document type."""
    classification_prompt = f"""
    You are a document classifier. Based on the text below, classify the document type into one of:
    - invoice
    - purchase_order
    - approval
    Respond with ONLY one of these words.

    Document text:
    {text[:3000]}
    """
    try:
        response = llm.invoke(classification_prompt)
        doc_type = response.content.strip().lower()
        if "invoice" in doc_type:
            return "invoice"
        elif "purchase" in doc_type or "order" in doc_type:
            return "purchase_order"
        elif "approval" in doc_type:
            return "approval"
        else:
            return "invoice"  # fallback
    except Exception as e:
        st.warning(f"Could not classify document: {e}")
        return "invoice"


# ==============================
# Streamlit UI
# ==============================

st.set_page_config(page_title="Document Information Extractor", layout="centered")
st.title("📄 Intelligent Document Information Extractor")
st.write("Upload an **Invoice**, **Purchase Order**, or **Approval** document for automatic processing.")

uploaded_file = st.file_uploader("Upload Document", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file is not None:
    # Preview for images
    if uploaded_file.name.lower().endswith((".png", ".jpg", ".jpeg")):
        st.image(uploaded_file, caption="Uploaded Document", use_container_width=True)
    else:
        st.info("📄 PDF uploaded — no preview available.")

    if st.button("🚀 Extract Information"):
        with st.spinner("Extracting text from file..."):
            extracted_text = extract_text_from_file(uploaded_file)

        if extracted_text:
            st.subheader("🧾 Extracted Text")
            st.text(extracted_text)

            # Step 1: Detect document type
            with st.spinner("Classifying document type..."):
                doc_type = detect_document_type(extracted_text)
            st.success(f"✅ Detected Document Type: **{doc_type.replace('_', ' ').title()}**")

            # Step 2: Process structured extraction
            st.subheader("🤖 Processing with Gemini...")
            message = f"""
            system: You are a {doc_type.replace('_', ' ')} information extractor who converts document text into structured JSON with proper key-value pairs.
            user: {extracted_text}
            """

            try:
                response = llm.invoke(message)
                result = response.content.strip().replace("```json", "").replace("```", "")
                json_data = json.loads(result)

                # Step 3: Embedding
                embedding_vector = embedding_model.encode(extracted_text).tolist()

                # Step 4: Save to MongoDB
                collection = collections[doc_type]
                existing_doc = collection.find_one({
                    "$or": [
                        {"file_name": uploaded_file.name},
                        {"extracted_text": extracted_text}
                    ]
                })

                if existing_doc:
                    st.warning(f"⚠️ This {doc_type.replace('_', ' ')} already exists in the database.")
                    st.json(existing_doc.get("document_data", existing_doc.get("invoice_data", {})))
                else:
                    insert_result = collection.insert_one({
                        "file_name": uploaded_file.name,
                        "document_type": doc_type,
                        "extracted_text": extracted_text,
                        "document_data": json_data,
                        "embedding": embedding_vector
                    })
                    st.success(f"✅ Saved to MongoDB in **{doc_type}** collection (ID: {insert_result.inserted_id})")

                # Step 5: Show structured data
                st.subheader("📋 Extracted Information (JSON)")
                st.json(json_data)

                # Step 6: Download option
                st.download_button(
                    label="💾 Download Extracted JSON",
                    data=json.dumps(json_data, indent=4),
                    file_name=f"{doc_type}_data.json",
                    mime="application/json"
                )

            except json.JSONDecodeError:
                st.error("Invalid JSON from AI model. Please try again.")
            except Exception as e:
                st.error(f"Error processing document: {str(e)}")
