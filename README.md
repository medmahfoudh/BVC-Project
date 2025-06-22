# 🧠 Wieland Agentic AI App (Dockerized)

This project provides a modular, multi-agent Retrieval-Augmented Generation (RAG) system to extract insights from customer visit reports using local LLMs (via Ollama), vector search (Qdrant), and a Streamlit UI.

---

## 🚀 Features

- Ingest and embed PDF visit reports
- Semantic search and summarization via LLMs
- Actionable briefings for sales intelligence
- Containerized with Ollama + Streamlit inside Docker

---

## 🧰 Requirements

- Docker installed
- ~8GB of free RAM
- Internet access for first model download (4.1GB)

---

## 🐳 Run with Docker

### 🟢 1. Build the image (only once):

```bash
docker build -t wieland-app .
```

### 🟢 2. Run the container with persistent Ollama model cache:

**Linux/macOS:**

```bash
docker run -p 8501:8501 -v ollama-models:/root/.ollama/models wieland-app
```

**Windows CMD:**

```cmd
docker run -p 8501:8501 -v ollama-models:/root/.ollama/models wieland-app
```

> On first run, this pulls the `mistral` model (~4.1GB). Reused across runs.

---


## 🧠 Ollama Notes

- Model: `mistral` (loaded via `ollama pull`)
- API served at `http://localhost:11434`
- Already included inside the Docker image

---

## 🧪 Test Access

Once running, open your browser at:

```
http://localhost:8501
```

---

## 🙋 Troubleshooting

- 🐢 First load is slow? Wait for Ollama to fully download model
- 💥 Meta tensor error? Restart container, ensure model pulled fully
- 🚫 Sidebar shows wrong files? Only include UI pages under `pages/`

---

## 🧼 Clean Up

To remove model cache volume:
```bash
docker volume rm ollama-models
```

To rebuild from scratch:
```bash
docker image rm wieland-app
```

---
