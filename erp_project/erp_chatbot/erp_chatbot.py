import os
import streamlit as st
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
import numpy as np
from dotenv import load_dotenv

# Must be first Streamlit command
st.set_page_config(page_title="ERP Invoice Chatbot", page_icon="🧾", layout="centered")

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
google_api_key = os.getenv("GEMINI_API_KEY")

# --- Initialize MongoDB connection ---
client = MongoClient(mongo_uri)
db = client["invoice_reader_db"]
collection = db["invoices"]

# --- Initialize models ---
@st.cache_resource
def load_models():
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    llm = ChatGoogleGenerativeAI(
        google_api_key=google_api_key,
        temperature=0.1,
        max_retries=2,
        convert_system_message_to_human=True,
        model="gemini-2.5-flash"
    )
    return embedder, llm

embedder, llm = load_models()

# --- Streamlit UI ---
st.title("🧠 ERP Invoice Chatbot")
st.write("Ask questions about your invoices stored in MongoDB!")

query = st.text_input("💬 Enter your question:", placeholder="e.g. What is the seller name in invoice number us-001?")

if st.button("Ask") and query:
    with st.spinner("Searching and generating answer..."):
        # Encode query
        query_embedding = embedder.encode(query).tolist()

        # MongoDB vector search
        results = collection.aggregate([
            {
                "$vectorSearch": {
                    "queryVector": query_embedding,
                    "path": "embedding",
                    "numCandidates": 5,
                    "limit": 3,
                    "index": "invoice_vector_index"
                }
            }
        ])

        results_list = list(results)

        if not results_list:
            st.warning("No relevant documents found.")
        else:
            # Combine context
            retrieved_docs = [r.get("extracted_text", "") for r in results_list]
            context = "\n\n".join(retrieved_docs)

            # Create prompt
            prompt = f"Answer the question based only on the following context:\n{context}\n\nQuestion: {query}"

            # LLM response
            response = llm.invoke(prompt)
            answer = response.content

            st.subheader("🧾 Answer")
            st.write(answer)

            # Expandable context
            with st.expander("Show retrieved invoice texts"):
                for i, doc in enumerate(retrieved_docs):
                    st.markdown(f"**Document {i+1}:**")
                    st.text(doc)
