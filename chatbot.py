# chatbot.py
import os
import streamlit as st
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

# --- Configuration ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen:0.5b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")  # Use env var directly (no fallback here; set it in Compose)
VECTOR_DB_PATH = "faiss_index"

def get_rag_chain():
    print(f"Loading RAG chain with Ollama model: {OLLAMA_MODEL}...")
    print(f"OLLAMA_HOST for chatbot: {OLLAMA_HOST}")

    # Load embeddings with base_url
    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL, base_url=OLLAMA_HOST)

    # Load existing vector store
    if not os.path.exists(VECTOR_DB_PATH):
        raise FileNotFoundError(f"Vector store not found at {VECTOR_DB_PATH}. Please run ingest.py first.")
    try:
        vector_store = FAISS.load_local(VECTOR_DB_PATH, embeddings, allow_dangerous_deserialization=True)
        print("FAISS vector store loaded successfully.")
    except Exception as e:
        raise ValueError(f"Could not load FAISS vector store from {VECTOR_DB_PATH}. Error: {e}")

    # Initialize Ollama LLM with base_url
    try:
        llm = Ollama(model=OLLAMA_MODEL, temperature=0.1, base_url=OLLAMA_HOST)
        # Test LLM to ensure Ollama is accessible
        _ = llm.invoke("hello", stop=["."])
        print("Ollama LLM initialized successfully.")
    except Exception as e:
        raise ConnectionError(f"Error initializing Ollama LLM. Please ensure Ollama is running and model '{OLLAMA_MODEL}' is pulled.\n"
                              f"Check if Ollama is accessible at '{OLLAMA_HOST}'.\n"
                              f"Original Error: {e}")

    # Define custom prompt for Qwen (unchanged)
    system_template = """You are a helpful and expert washing machine service assistant.
    Your primary goal is to assist service engineers in diagnosing and resolving washing machine problems.

    You will answer questions based *strictly* on the provided context, which is an excerpt
    from the washing machine service manual.
    Keep your answers concise, clear, and directly relevant to the question and context.

    If the necessary information to answer a question is *not* present in the provided
    context, politely state that you don't have enough information from the manual to answer
    that specific query. Do not invent information or provide general advice not found in the
    manual.

    Context from Service Manual:
    {context}
    """
    human_template = "Engineer's Question: {question}"

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(human_template),
    ])

    # Setup memory for conversational history
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")

    # Create the Conversational RetrievalChain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=False
    )
    print("RAG chain setup complete.")
    return qa_chain

if __name__ == "__main__":
    # This block is for direct command-line execution (for testing or non-Streamlit use)
    try:
        qa_chain = get_rag_chain()
        print("\n--- Chatbot Ready ---")
        print("Type your questions about washing machine issues. Type 'exit' to quit.")
        chat_history = []
        while True:
            user_input = input("Engineer: ")
            if user_input.lower() == 'exit':
                break
            if not user_input.strip():
                print("Chatbot: Please enter a question.")
                continue

            try:
                response = qa_chain.invoke({"question": user_input, "chat_history": chat_history})
                ai_response = response["answer"]
                print(f"Chatbot: {ai_response}")
                chat_history.append(HumanMessage(content=user_input))
                chat_history.append(AIMessage(content=ai_response))
            except Exception as e:
                print(f"An error occurred during chat: {e}")
                print("Please ensure Ollama is running and the Qwen model is pulled and accessible.")
    except (FileNotFoundError, ValueError, ConnectionError) as e:
        print(f"Error initializing chatbot: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during chatbot initialization: {e}")
