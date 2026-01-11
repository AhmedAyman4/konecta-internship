### Automated Document Processing

A minimal, end-to-end pipeline that extracts structured data from invoices and receipts (PDFs or images) for integration into an ERP system.


1. **Upload** – User submits a document via Streamlit UI.  
2. **Extract** – Text is pulled using `pdfplumber` (PDF) or `pytesseract` (image).  
3. **Process** – LLM classifies document type, extracts JSON, and generates an embedding.  
4. **Store/Show** – Checks MongoDB for duplicates; saves if new, otherwise shows existing result.  

Output: Clean JSON displayed and downloadable.

<img width="8192" height="802" alt="Automated Document Processing diagram-2026-01-11-214840" src="https://github.com/user-attachments/assets/970a92cf-ff67-4bb8-bdf4-e41e4202a264" />


### Live demo & API

- Streamlit app (demo): https://huggingface.co/spaces/ahmed-ayman/automated_document_processing
- API: https://huggingface.co/spaces/ahmed-ayman/document-processor-api
