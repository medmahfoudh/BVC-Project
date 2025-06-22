FROM ubuntu:22.04

# 1. Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    software-properties-common \
    git \
    python3 \
    python3-pip \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# 3. Download mistral model
# Download will happen in entrypoint
# RUN ollama pull mistral

# 4. Set up app directory
WORKDIR /app
COPY . /app

# 5. Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir --ignore-installed -r requirements.txt

# 6. Expose default Streamlit port
EXPOSE 8501

# 7. Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# 8. Start Ollama and Streamlit app
ENTRYPOINT ["/app/entrypoint.sh"]
