# 🤖 Washing-Machince-Service-Chatbot (Streamlit + Ollama + RAG)

This repository provides a ready-to-run Streamlit chatbot that uses a locally-hosted Ollama Qwen model enhanced with a Washing Machine Service Manual via RAG (FAISS). It includes an admin panel that logs queries and shows which manual chunks were retrieved for each reply.

This chatbot helps service engineers diagnose washing-machine faults.  
It combines:

* **Streamlit** – conversational web UI  
* **LangChain RAG** – retrieves chunks from the service-manual PDF  
* **Ollama (Qwen model)** – local LLM for answer generation  
* **FAISS** – vector search over embeddings  
* **Docker Compose** – one-command deployment (Ollama + Streamlit)
  
## What's included
- `ingest.py` — Ingests a PDF manual, chunks text, generates embeddings via Ollama, and builds a FAISS index.
- `streamlit_app.py` — Streamlit UI for engineers + admin page showing logs and retrieved contexts.
- `requirements.txt`
- `Dockerfile`
- `.env.example`
- `.gitignore`
- `make_zip.sh` (helper)
## Project Structure:
```sh
washing_machine_chatbot/
├── data/
│   └── Washing Machine Service Manual.pdf  # The input manual
├── faiss_index/                     # Persisted vector database (FAISS)
├── .gitignore
├── requirements.txt                 # Python dependencies
├── ingest.py                        # Script for manual processing & FAISS creation
├── chatbot.py                       # Core RAG logic & LLM interaction
├── app.py                           # Streamlit UI
├── Dockerfile                       # Docker image definition for the chatbot
└── docker-compose.yml               # Orchestration for multi-container deployment

```
## Quick steps (summary)

### 1) Create and activate a virtual environment
```sh
 python -m venv venv       # Create enivronment
.\venv\Scripts\Activate.ps1 # Windows PowerShell , virtual environment
```
### 2) Install Python dependencies
```sh 
pip install -r requirements.txt
```

### 3) Generate the FAISS vector store from the PDF
```sh 
python ingest.py
 ```

### 4) start Ollama and pull the model 

```sh
ollama serve # new terminal, leaves it running
ollama pull qwen:0.5b
```

### 5) Launch the Streamlit app for a quick test
```sh 
streamlit run app.py
 ```

> ####  To stop a running Streamlit app in PowerShell (or any terminal/command prompt), you typically use a keyboard shortcut:
Go to the PowerShell window where you originally ran the streamlit run app.py command.
Press Ctrl + C on your keyboard.

> The local route is handy for development; production deployment is containerised below.

---

## Deploy with Docker Compose

#### 1) Stop and remove any running containers/volumes to clear state:
```sh 
docker compose down -v
 ```
#### 2) Update your code files: Replace chatbot.py, ingest.py, and docker-compose.yml with the corrected versions above (edit them in your editor).

#### 3) Build the chatbot image (includes code changes):
```sh
docker compose build chatbot
 ```
#### 4) Start Ollama container alone first (to isolate and fix health):
```sh
docker compose up -d ollama
 ```
#### 5) Verify Ollama is healthy and pull the model inside the container:
```sh
docker exec -it ollama_server sh
ollama pull qwen:0.5b
ollama list  # Confirm model is listed
exit
```
#### 6) Should return "Ollama is running" 
```sh
curl http://localhost:11434
```
#### 7) Check Ollama container status (ensure it's healthy):
```sh
docker inspect --format "{{.State.Health.Status}}" ollama_server
```
#### It should output "healthy". If not, check logs:
 ```sh
 docker logs ollama_server
 ```
#### 8) Access the app: 
```sh
docker compose up --build 
```
Open  http://localhost:8501 in your browser.

#### 9) Monitor logs if issues persist:
 ```sh
docker logs -f wm_chatbot
docker logs -f ollama_server
 ```
> This sequence ensures Ollama starts healthy, the model is loaded, and LangChain uses the  correct base_url

---

## Helpful tips
* Run all commands from the project root (where `docker-compose.yml` lives).   
* Change ports in `docker-compose.yml` if 8501 or 11434 are already in use.  
* Monitor logs with `docker compose logs -f` for troubleshooting.  
* Avoid running another `ollama serve` on the host while Docker is active to prevent port conflicts.  

---
