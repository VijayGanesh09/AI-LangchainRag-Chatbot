# Backend Integration

## Overview

Developers can integrate the reusable RAG engine
into their own Python applications.

## Import the RAG Engine

from rag_engine import RAGEngine

## Initialize

bot = RAGEngine()

## Ask a Question

answer = bot.chat(
    "Explain the main points in my document"
)

print(answer)

## Requirements

- Python
- Backend dependencies installed
- Configured environment variables
- Documents indexed in ChromaDB

## Note

The current RAGEngine wrapper uses the existing
Groq configuration and ChromaDB collection.
It is not yet a standalone pip package.