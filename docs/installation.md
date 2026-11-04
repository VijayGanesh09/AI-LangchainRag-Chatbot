# Installation Guide

## 1. Clone the Repository

git clone YOUR_GITHUB_REPOSITORY_URL

cd AI-LangchainRag-Chatbot

## 2. Backend Setup

cd backend

python -m venv venv

## Activate virtual environment

Windows PowerShell:

venv\Scripts\Activate.ps1

## Install dependencies

pip install -r requirements.txt

## Configure Environment Variables

Copy .env.example to .env.

Add the required Groq API key and configuration.

## Run Backend

python app.py

Backend runs at:

http://localhost:5000

## 3. Frontend Setup

Open another terminal.

cd frontend

npm install

npm run dev

## 4. Build the Main Frontend

npm run build

## 5. Build the Chatbot Widget

npm run build:widget

The widget build is generated inside dist-widget/.