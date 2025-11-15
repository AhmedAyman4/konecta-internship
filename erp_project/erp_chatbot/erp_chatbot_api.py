import os
from flask import Flask, request, jsonify
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
google_api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Flask app
app = Flask(__name__)

# Initialize MongoDB connection
client = MongoClient(mongo_uri)
db = client["invoice_reader_db"]

# Define collections
collections = {
    "invoice": db["invoices"],
    "purchase_order": db["purchase_orders"],
    "approval": db["approvals"]
}

# Set cache directories
os.environ["HF_HOME"] = "/tmp/huggingface"
os.environ["TRANSFORMERS_CACHE"] = "/tmp/huggingface"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = "/tmp/sentence_transformers"
print("Model cache directory:", os.environ["HF_HOME"])

# Initialize models (load once at startup)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
llm = ChatGoogleGenerativeAI(
    google_api_key=google_api_key,
    temperature=0.1,
    max_retries=2,
    convert_system_message_to_human=True,
    model="gemini-2.5-flash"
)

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        "message": "ERP Multi-Collection Chatbot API",
        "endpoints": {
            "/": "GET - API information",
            "/query": "POST - Query across all collections or specific ones",
            "/invoices": "GET - Get all invoices",
            "/purchase_orders": "GET - Get all purchase orders",
            "/approvals": "GET - Get all approvals",
            "/health": "GET - Health check"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check MongoDB connection
        client.server_info()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "collections": list(collections.keys())
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/invoices', methods=['GET'])
def get_invoices():
    """Get all invoices or filter by parameters"""
    return get_documents_from_collection("invoice")

@app.route('/purchase_orders', methods=['GET'])
def get_purchase_orders():
    """Get all purchase orders"""
    return get_documents_from_collection("purchase_order")

@app.route('/approvals', methods=['GET'])
def get_approvals():
    """Get all approvals"""
    return get_documents_from_collection("approval")

def get_documents_from_collection(collection_name):
    """Helper function to get documents from a specific collection"""
    try:
        # Get query parameters
        limit = request.args.get('limit', default=10, type=int)
        skip = request.args.get('skip', default=0, type=int)
        
        collection = collections[collection_name]
        
        # Fetch documents
        documents = list(collection.find({}, {"_id": 0, "embedding": 0}).skip(skip).limit(limit))
        
        return jsonify({
            "success": True,
            "collection": collection_name,
            "count": len(documents),
            "documents": documents
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/query', methods=['POST'])
def query_invoices():
    """Query across multiple collections using natural language"""
    try:
        # Get query from request
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'query' in request body"
            }), 400
        
        query = data['query']
        num_results = data.get('num_results', 3)
        
        # Optional: specify which collections to search
        # If not provided, search all collections
        search_collections = data.get('collections', list(collections.keys()))
        
        # Validate collection names
        invalid_collections = [c for c in search_collections if c not in collections]
        if invalid_collections:
            return jsonify({
                "success": False,
                "error": f"Invalid collections: {invalid_collections}. Valid options: {list(collections.keys())}"
            }), 400
        
        if not query.strip():
            return jsonify({
                "success": False,
                "error": "Query cannot be empty"
            }), 400
        
        # Encode query
        query_embedding = embedder.encode(query).tolist()
        
        # Search across specified collections
        all_results = []
        for collection_name in search_collections:
            collection = collections[collection_name]
            
            # MongoDB vector search
            results = collection.aggregate([
                {
                    "$vectorSearch": {
                        "queryVector": query_embedding,
                        "path": "embedding",
                        "numCandidates": 5,
                        "limit": num_results,
                        "index": "vector_index"  # Make sure this index exists for each collection
                    }
                },
                {
                    "$addFields": {
                        "collection_type": collection_name
                    }
                }
            ])
            
            results_list = list(results)
            all_results.extend(results_list)
        
        if not all_results:
            return jsonify({
                "success": True,
                "answer": "No relevant documents found.",
                "retrieved_documents": []
            }), 200
        
        # Sort by relevance score if available, otherwise keep order
        # Take top num_results across all collections
        all_results = all_results[:num_results * len(search_collections)]
        
        # Combine context
        retrieved_docs = []
        for r in all_results:
            doc_text = r.get("extracted_text", "")
            collection_type = r.get("collection_type", "unknown")
            retrieved_docs.append({
                "text": doc_text,
                "collection": collection_type,
                "metadata": {k: v for k, v in r.items() if k not in ["embedding", "extracted_text", "_id", "collection_type"]}
            })
        
        context = "\n\n".join([
            f"[{doc['collection'].upper()}]\n{doc['text']}" 
            for doc in retrieved_docs
        ])
        
        # Create prompt
        prompt = f"""Answer the question based only on the following context from multiple document types (invoices, purchase orders, and approvals):

{context}

Question: {query}

Please provide a comprehensive answer based on the information available in the documents above."""
        
        # LLM response
        response = llm.invoke(prompt)
        answer = response.content
        
        return jsonify({
            "success": True,
            "query": query,
            "answer": answer,
            "collections_searched": search_collections,
            "retrieved_documents": retrieved_docs
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7860)