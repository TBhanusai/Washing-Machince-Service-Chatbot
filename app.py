# app.py
import streamlit as st
from chatbot import get_rag_chain # Import the function to get your RAG chain
from langchain_core.messages import HumanMessage, AIMessage

# --- Streamlit App Configuration ---
st.set_page_config(page_title="Washing Machine Troubleshooter", layout="centered")
st.title("Washing Machine Troubleshooting Chatbot 🤖")
st.markdown("---")

# Initialize the RAG chain (only once per session for efficiency)
@st.cache_resource # Caches the resource (the RAG chain) across reruns
def load_rag_chain():
    with st.spinner("Loading AI assistant and service manual knowledge..."):
        try:
            return get_rag_chain()
        except FileNotFoundError as e:
            st.error(f"Error: {e}")
            st.warning("Please ensure you have run `python ingest.py` to create the vector store.")
            st.stop() # Stop the app if crucial components are missing
        except ConnectionError as e:
            st.error(f"Connection Error: {e}")
            st.warning("Please ensure Ollama is running and the Qwen model is pulled. Check your OLLAMA_HOST environment variable if running in Docker.")
            st.stop()
        except Exception as e:
            st.error(f"An unexpected error occurred while loading the AI assistant: {e}")
            st.stop()

qa_chain = load_rag_chain()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="Hello! I'm your AI assistant for washing machine repairs, powered by the service manual. What problem are you seeing today?", type="ai")
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message("user" if message.type == "human" else "assistant"):
        st.markdown(message.content)

# Accept user input
if prompt := st.chat_input("Describe the washing machine problem..."):
    # Add user message to chat history
    st.session_state.messages.append(HumanMessage(content=prompt, type="human"))
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing the problem and consulting the manual..."):
            # Prepare chat history for the chain.
            # LangChain's ConversationalRetrievalChain memory handles the format internally
            # when using ConversationBufferMemory with return_messages=True.
            # We just need to pass the current question.
            try:
                # Construct chat_history for the chain from session_state.messages
                # This needs to be a list of BaseMessage objects (HumanMessage, AIMessage)
                chain_history = []
                for msg in st.session_state.messages[:-1]: # Exclude the current user prompt from history for the current turn
                    if msg.type == 'human':
                        chain_history.append(HumanMessage(content=msg.content))
                    elif msg.type == 'ai':
                        chain_history.append(AIMessage(content=msg.content))

                response = qa_chain.invoke({"question": prompt, "chat_history": chain_history})
                ai_response = response["answer"]
                st.markdown(ai_response)
                # Add AI response to chat history
                st.session_state.messages.append(AIMessage(content=ai_response, type="ai"))
            except Exception as e:
                st.error(f"An error occurred while getting a response: {e}")
                st.warning("Please check if the Ollama server is still running and accessible.")

st.markdown("---")
st.caption("Powered by Ollama (Qwen) and LangChain")