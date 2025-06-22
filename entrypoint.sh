#!/bin/bash

# Start Ollama in background
ollama serve &

# Wait until Ollama is ready
until curl -s http://localhost:11434 > /dev/null; do
  echo "Waiting for Ollama..."
  sleep 2
done

# Download model if not already pulled
ollama list | grep -q mistral || ollama pull mistral

# Start Streamlit app
streamlit run app.py --server.port=8501 --server.enableCORS=false
