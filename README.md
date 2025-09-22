# Washing-Machince-Service-Chatbot
*A Streamlit + Ollama reference implementation*

This chatbot helps service engineers diagnose washing-machine faults.  
It combines:

* **Streamlit** – conversational web UI  
* **LangChain RAG** – retrieves chunks from the service-manual PDF  
* **Ollama (Qwen model)** – local LLM for answer generation  
* **FAISS** – vector search over embeddings  
* **Docker Compose** – one-command deployment (Ollama + Streamlit)

---

1 Create and activate a virtual environment
```sh python -m venv venv
.\venv\Scripts\Activate.ps1 # Windows PowerShell
```
2 Install Python dependencies
```sh 
pip install -r requirements.txt
```

3 Generate the FAISS vector store from the PDF
```sh 
python ingest.py
 ```

4 (Only if you are not using Docker) start Ollama and pull the model

```sh
ollama serve # new terminal, leaves it running
ollama pull qwen:0.5b
```

5 Launch the Streamlit app for a quick test
```sh 
streamlit run app.py
 ```



