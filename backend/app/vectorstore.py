
import os
import uuid

from langchain_community.vectorstores import Chroma

from app.config import CHROMA_DB_PATH
from app.embeddings import get_embedding_model


COLLECTION_NAME = "rag_documents"


def get_vector_store():

    os.makedirs(CHROMA_DB_PATH, exist_ok=True)

    embeddings = get_embedding_model()

    vectorstore = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )

    return vectorstore


def create_vector_store(chunks, reset=False):

    vectorstore = get_vector_store()

    # Remove old document embeddings when reset is True
    if reset:
        existing = vectorstore.get()

        if existing["ids"]:
            vectorstore.delete(ids=existing["ids"])

    if chunks:

        chunk_ids = [str(uuid.uuid4()) for _ in chunks]

        vectorstore.add_documents(
            documents=chunks,
            ids=chunk_ids
        )

    return vectorstore


def delete_all_embeddings():

    vectorstore = get_vector_store()

    existing = vectorstore.get()

    if existing["ids"]:
        vectorstore.delete(ids=existing["ids"])
        print("All embeddings deleted successfully!")

    else:
        print("Vector database is already empty.")