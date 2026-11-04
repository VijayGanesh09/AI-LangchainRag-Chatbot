
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHUNK_SIZE, CHUNK_OVERLAP


def load_and_split_pdf(file_path, document_id):

    # Check whether PDF exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    # Validate PDF extension
    if not file_path.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported")

    # Load PDF
    loader = PyPDFLoader(file_path)

    # Configure text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True
    )

    # Read pages one at a time
    for page in loader.lazy_load():

        # Skip empty pages
        if not page.page_content.strip():
            continue

        # Split page into smaller chunks
        page_chunks = text_splitter.split_documents([page])

        for chunk in page_chunks:

            # Add source filename
            chunk.metadata["source"] = os.path.basename(file_path)

            # Add unique document ID
            chunk.metadata["document_id"] = document_id

            # Return one chunk at a time
            yield chunk
