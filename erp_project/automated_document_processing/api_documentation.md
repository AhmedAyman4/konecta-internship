# Document Processing API – API Documentation

---

## Overview

The **Document Processing API** extracts, classifies, and stores structured data from uploaded documents (invoices, purchase orders, and approvals) using OCR, LLMs, and vector embeddings. It supports image (PNG, JPG, JPEG) and PDF file types up to 16 MB.

---

## Base URL

```
https://ahmed-ayman-invoice-reader-api.hf.space
```


---

## Endpoints

### 1. Health Check

**GET** `/`

- **Purpose**: Verify the API is running.
- **Response**:
  ```json
  {
    "status": "running",
    "message": "Document Processing API",
    "endpoints": {
      "POST /api/extract": "Upload and extract document info (invoice, PO, approval)",
      "GET /api/<type>": "Get all documents by type (invoices, purchase_orders, approvals)"
    }
  }
  ```
- **Status Codes**:
  - `200 OK` – Service is operational.

---

### 2. Extract & Process Document

**POST** `/api/extract`

- **Purpose**: Upload a document, extract text, classify its type, parse structured data, and store it in MongoDB.

#### Request

- **Headers**:
  - `Content-Type: multipart/form-data`

- **Form Data**:
  - `file` *(required)* – The document file (PNG, JPG, JPEG, or PDF, max 16 MB).

#### Response

Successful processing:
```json
{
  "success": true,
  "message": "Invoice processed successfully",
  "mongodb_id": "672a1b2c3d4e5f6a7b8c9d0e",
  "document_type": "invoice",
  "extracted_text": "Seller: ABC Corp...\nTotal: $1,200...",
  "document_data": {
    "invoice_number": "INV-2025-001",
    "date": "2025-10-30",
    "total_amount": 1200.00,
    ...
  }
}
```

Document already exists:
```json
{
  "warning": "Document already exists in database",
  "existing_id": "672a1b2c3d4e5f6a7b8c9d0e",
  "document_type": "invoice",
  "extracted_text": "...",
  "document_data": { ... }
}
```

#### Error Responses

| Status Code | Response Body |
|------------|---------------|
| `400` | `{"error": "No file provided"}` |
| `400` | `{"error": "No file selected"}` |
| `400` | `{"error": "Invalid file type. Allowed: png, jpg, jpeg, pdf"}` |
| `400` | `{"error": "No text could be extracted from the file"}` |
| `413` | `{"error": "File too large. Maximum size is 16MB"}` |
| `500` | `{"error": "Invalid JSON response from AI model"}` |
| `500` | `{"error": "Processing error: <details>"}` |

> **Document Types Detected**:
> - `invoice`
> - `purchase_order`
> - `approval`  
> *(Defaults to `invoice` if uncertain)*

---

### 3. Retrieve All Documents by Type

**GET** `/api/<doc_type>`

- **Purpose**: Fetch all stored documents of a given type.

#### Path Parameters

| Parameter | Values |
|---------|--------|
| `doc_type` | `invoice`, `purchase_order`, or `approval` |

#### Response

```json
{
  "document_type": "invoice",
  "count": 2,
  "documents": [
    {
      "_id": "672a1b2c3d4e5f6a7b8c9d0e",
      "file_name": "inv_001.pdf",
      "document_type": "invoice",
      "extracted_text": "...",
      "document_data": { ... }
    },
    ...
  ]
}
```

> **Note**: Embedding vectors are excluded from the response for performance.

#### Error Responses

| Status Code | Response Body |
|------------|---------------|
| `400` | `{"error": "Invalid document type"}` |
| `500` | `{"error": "Database error: <details>"}` |

---

## Error Handling

| HTTP Code | Meaning |
|---------|--------|
| `400` | Bad Request – Client-side input error |
| `413` | Payload Too Large – File exceeds 16 MB |
| `500` | Internal Server Error – Unexpected failure |

All errors return a JSON object with an `"error"` key containing a descriptive message.

---

## Supported File Types

- `.png`
- `.jpg`
- `.jpeg`
- `.pdf`

> **Max File Size**: 16 MB

---

## Authentication & Security

- This API **does not include built-in authentication**.
- In production, secure endpoints using API keys, OAuth, or a reverse proxy (e.g., NGINX with basic auth or JWT validation).

---

## Dependencies Used

- **OCR**: `pytesseract` (for images), `pdfplumber` (for PDFs)
- **LLM**: `Google Generative AI (Gemini-2.5-Flash)` via LangChain
- **Embeddings**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Database**: MongoDB (collections: `invoices`, `purchase_orders`, `approvals`)
- **Framework**: Flask

---

## Deployment Notes

- The app runs on port `7860` by default (compatible with Hugging Face Spaces).
- Environment variables required:
  - `GOOGLE_API_KEY` – for Gemini LLM
  - `MONGO_URI` – MongoDB connection string
- Caching for Hugging Face models is configured to `/tmp/` for compatibility with serverless environments.

--- 

> ✅ **Tip for Users**: Always validate structured output (`document_data`) in your frontend or downstream services, as LLM outputs may vary slightly in format.