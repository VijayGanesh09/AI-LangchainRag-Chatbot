# Chatbot Widget Integration

## Overview

The RAG chatbot provides an embeddable floating chat widget.

Companies can integrate it into their existing websites
without building their own chat interface.

## Integration

Add this script to the company's website:

<script
  src="YOUR_BACKEND_URL/widget.js"
  data-api-url="YOUR_BACKEND_URL">
</script>

Replace YOUR_BACKEND_URL with the company's deployed
backend URL.

## How It Works

1. The widget loads on the company website.
2. The user opens the chatbot.
3. The user submits a question.
4. The widget sends the question to the company's
   Flask backend.
5. The backend retrieves relevant document chunks.
6. The LLM generates an answer.
7. The answer is displayed in the widget.

## Important

The company's own backend, documents, vector database,
and API credentials are used.