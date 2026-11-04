
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from app.config import GROQ_API_KEY, MODEL_NAME
from app.retriever import retrieve_documents


# ==========================================
# LLM INITIALIZATION
# ==========================================

_llm = None


def get_llm():

    global _llm

    if not GROQ_API_KEY:
        raise ValueError("Groq API key is missing")

    if _llm is None:

        _llm = ChatGroq(
            model=MODEL_NAME,
            groq_api_key=GROQ_API_KEY,
            temperature=0,
            max_retries=2
        )

    return _llm


# ==========================================
# RAG PROMPT
# ==========================================

prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
        You are an intelligent, context-aware AI assistant
        specialized in answering questions about uploaded documents.

        Instructions:

        1. Understand the user's actual intention rather than
           simply matching keywords from the document.

        2. Understand synonyms, alternative expressions, and
           differently worded questions.

        3. When the user asks a broad question about the document,
           provide a meaningful explanation covering the available
           document context.

        4. When the user asks a specific question, focus on the
           relevant information and explain it clearly.

        5. Connect related information from different sections
           when needed.

        6. Use previous conversation history only to understand
           follow-up questions, references, and conversational context.
           Do not treat previous conversation history as a factual
           knowledge source.

        7. Answer directly and naturally. Do not unnecessarily
           repeat the question.

        8. Use simple, clear language and organize longer answers
           with headings or bullet points where appropriate.

        9. Do not invent information or make unsupported assumptions.

        10. Strictly use the information available in the currently
            uploaded document context to answer questions.

        11. If the requested information is not available in the
            document context, or the question is completely unrelated
            to the uploaded document, do not answer using general
            knowledge or information from previous conversations.

        12. In such cases, politely respond:
            "I'm sorry, but I'm specifically designed to assist with
            information from my available knowledge source. I may not
            be able to answer questions outside the scope of the
            uploaded document. Please feel free to ask me anything
            related to it."

        13. Understand the tone, intent, and conversational style
            of the user's questions, including when they switch
            between different languages. Respond in the language
            and tone appropriate to the user.

        Document Context:
        {context}

        Previous Conversation:
        {history}
        """
    ),

    ("human", "{question}")

])

# ==========================================
# GENERATE ANSWER
# ==========================================

def generate_answer(question, document_id, chat_history=None):

    if not question or not question.strip():
        return {
            "answer": "Please enter a valid question.",
            "sources": []
        }

    if not document_id:
        return {
            "answer": "No active document was found.",
            "sources": []
        }

    # Retrieve relevant chunks from the specific document
    documents = retrieve_documents(
        question,
        document_id
    )

    if not documents:
        return {
            "answer": "I could not find relevant information in your uploaded document.",
            "sources": []
        }

    # Prepare document context
    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    # Prepare recent conversation history
    history_text = ""

    if chat_history:

        history_text = "\n".join(
            f"{message.get('role', 'user')}: "
            f"{message.get('content', '')}"
            for message in chat_history[-4:]
            if isinstance(message, dict)
        )

    # Prepare source information
    sources = []

    for document in documents:

        source = {
            "source": document.metadata.get("source", "Unknown"),
            "page": document.metadata.get("page", None)
        }

        if source not in sources:
            sources.append(source)

    # Create LLM chain
    chain = prompt | get_llm()

    # Generate response
    response = chain.invoke({

        "context": context,
        "history": history_text,
        "question": question.strip()

    })

    return {
        "answer": response.content,
        "sources": sources
    }
