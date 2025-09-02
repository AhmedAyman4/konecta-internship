Hello ya shabab, here's the task for this week

Objective

Build a chatbot with conversational memory that can answer user queries based on three distinct product manuals (PDFs). The chatbot should be able to index the documents, store them in a suitable vector store along with metadata, and retrieve relevant information to answer questions.

Data Requirements

- Collect four product manuals in PDF format from the following source: https://www.manualslib.com/
- Each manual should be at least 10 pages long.
- Metadata to extract per chunk should include at minimum:
- Document name
- Page number
- Section heading (if available)

Task Requirements

- Document Ingestion and Preprocessing
- Load the four PDFs.
- Split the documents into chunks.
- Attach metadata to each chunk.

Indexing

- Store the documents in a suitable vector store along with embeddings.
- Justify the choice of embedding model and vector store.

Chatbot with Memory

- Implement conversational memory so that the chatbot can handle follow-up questions.
- Ensure the chatbot can combine user history with retrieved context when generating answers.

Retrieval-Augmented Generation (RAG) Pipeline

- Retrieve relevant chunks from the manuals based on user queries.
- Ground responses in the documents and cite the source (document and page number).
- Ensure the chatbot can handle multi-turn interactions.

Evaluation

- Provide at least five example Q&A interactions with the chatbot, covering:
- Direct factual questions.
- Follow-up questions that depend on memory.
- Questions requiring retrieval from different manuals.
- An out-of-scope question where the chatbot should respond appropriately.

Deliverables
A single Jupyter Notebook containing:

- All code.
- Explanations in markdown cells.
- Output cells showing chatbot interactions.
- The notebook should run end-to-end without requiring external scripts.

Bonus (Optional)

- Implement metadata-based filtering (e.g., restrict retrieval to one manual or section).
- Add summarization functionality.
- Persist the vector store locally so it does not need to be rebuilt each run.

And here's last session's code:
https://github.com/M-Abdelmegeed/Konecta-DS-W06
