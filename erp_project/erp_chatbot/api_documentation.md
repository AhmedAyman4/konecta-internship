# ERP Multi-Collection Chatbot API Documentation

## Overview

This API enables semantic querying across multiple business document collections (invoices, purchase orders, and approvals) using natural language. It leverages sentence embeddings for vector-based retrieval and a large language model (Google Gemini) to generate contextual answers.

---

## Base URL

https://ahmed-ayman-erp-chatbot-api.hf.space

---

## Authentication

All endpoints are publicly accessible. Secure your deployment using environment variables and reverse proxy authentication in production.

---

## Endpoints

### 1. Home — API Information

**GET** `/`

Returns general information about the API and available endpoints.

**Response (200 OK)**  
```json
{
  "message": "ERP Multi-Collection Chatbot API",
  "endpoints": {
    "/": "GET - API information",
    "/query": "POST - Query across all collections or specific ones",
    "/invoices": "GET - Get all invoices",
    "/purchase_orders": "GET - Get all purchase orders",
    "/approvals": "GET - Get all approvals",
    "/health": "GET - Health check"
  }
}
```

---

### 2. Health Check

**GET** `/health`

Verifies that the API and MongoDB connection are functioning.

**Response (200 OK)**  
```json
{
  "status": "healthy",
  "database": "connected",
  "collections": ["invoice", "purchase_order", "approval"]
}
```

**Response (500 Internal Server Error)**  
```json
{
  "status": "unhealthy",
  "error": "Error message from MongoDB client"
}
```

---

### 3. Retrieve Documents

#### a. Invoices

**GET** `/invoices`

Fetches invoice documents with optional pagination.

**Query Parameters**
- `limit` (int, optional, default=10): Max number of documents to return.
- `skip` (int, optional, default=0): Number of documents to skip (for pagination).

**Response (200 OK)**  
```json
{
  "success": true,
  "collection": "invoice",
  "count": 5,
  "documents": [ /* list of invoice objects without `_id` or `embedding` */ ]
}
```

#### b. Purchase Orders

**GET** `/purchase_orders`

Same behavior as `/invoices`, but for purchase order documents.

#### c. Approvals

**GET** `/approvals`

Same behavior as `/invoices`, but for approval documents.

**Error Response (500)** for any retrieval failure:
```json
{
  "success": false,
  "error": "Description of the error"
}
```

---

### 4. Semantic Query Across Collections

**POST** `/query`

Performs a natural language query across one or more document collections using vector search and LLM-based summarization.

**Request Body (JSON)**
```json
{
  "query": "What are the total amounts for invoices from Vendor X?",
  "num_results": 3,
  "collections": ["invoice", "purchase_order"]
}
```

**Fields**
- `query` (string, required): The natural language question.
- `num_results` (int, optional, default=3): Number of top documents to retrieve per collection.
- `collections` (array of strings, optional): Subset of collections to search.  
  Valid values: `"invoice"`, `"purchase_order"`, `"approval"`.  
  If omitted, searches all three.

**Success Response (200 OK)**
```json
{
  "success": true,
  "query": "What are the total amounts for invoices from Vendor X?",
  "answer": "Based on the retrieved documents, Vendor X has two invoices totaling $5,200...",
  "collections_searched": ["invoice", "purchase_order"],
  "retrieved_documents": [
    {
      "text": "Invoice #12345 from Vendor X, amount: $2,500...",
      "collection": "invoice",
      "metadata": { /* document fields except _id, embedding, extracted_text */ }
    },
    ...
  ]
}
```

**Error Responses**
- **400 Bad Request** (missing or invalid input):
  ```json
  { "success": false, "error": "Missing 'query' in request body" }
  ```
- **400 Bad Request** (invalid collection name):
  ```json
  { "success": false, "error": "Invalid collections: ['invalid_coll']. Valid options: ['invoice', 'purchase_order', 'approval']" }
  ```
- **500 Internal Server Error** (e.g., embedding/LMM failure):
  ```json
  { "success": false, "error": "Description of exception" }
  ```

> **Note**: This endpoint requires that each MongoDB collection has a vector search index named `vector_index` on the `embedding` field.

---

## Requirements

- MongoDB Atlas (or MongoDB with vector search support)
- Environment variables:
  - `MONGO_URI`: Connection string to MongoDB
  - `GOOGLE_API_KEY`: API key for Google Generative AI (Gemini)

---

## Deployment Notes

- Embedding and LLM models are loaded once at startup for efficiency.
- Hugging Face cache is directed to `/tmp` to support serverless or containerized deployments.
- Runs on port `7860` by default.

---

## Example Usage

```bash
# Query all collections
curl -X POST http://localhost:7860/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me pending approvals from last week"}'

# Get first 5 invoices
curl "http://localhost:7860/invoices?limit=5"
```

--- 

*Built for data-driven ERP insights using AI-augmented retrieval.*