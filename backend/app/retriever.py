from app.vectorstore import get_vector_store
from app.config import TOP_K


def retrieve_documents(question, document_id):

    if not question or not question.strip():
        return []

    if not document_id:
        return []

    vectorstore = get_vector_store()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": TOP_K,
            "filter": {
                "document_id": document_id
            }
        }
    )

    documents = retriever.invoke(question.strip())

    return documents