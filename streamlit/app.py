import streamlit as st
import requests
import json
import time

# API endpoint
API_URL = "http://localhost:8000"

# Set page config
st.set_page_config(
    page_title="ConnectSense RAG System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("ConnectSense RAG System")
st.subheader("Retrieve information from your PDF documents using AI")

# Sidebar
with st.sidebar:
    st.header("System Controls")
    
    # Check index status
    if st.button("Check Index Status"):
        with st.spinner("Checking index status..."):
            try:
                response = requests.get(f"{API_URL}/index/status")
                if response.status_code == 200:
                    data = response.json()
                    if data["status"] == "success":
                        st.success(f"✅ Index Ready: {data['message']} Documents indexed: {data['document_count']}")
                    else:
                        st.error(f"❌ Index Not Ready: {data['message']}")
                else:
                    st.error(f"❌ Error: Failed to check index status. Status code: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection Error: Failed to connect to the API: {str(e)}")
                st.error(f"Make sure the FastAPI server is running at {API_URL}")

# Main content
st.header("Ask Questions About Your Documents")

# Initialize chat history if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.info(f"You: {message['content']}")
    else:
        st.success(f"Assistant: {message['content']}")

# Query input
query = st.text_input("Enter your question:", placeholder="e.g., What are the main challenges in connectivity in South Asia?")

if st.button("Ask") and query:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": query})
    
    # Display user message
    st.info(f"You: {query}")
    
    # Send query to API
    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{API_URL}/chat/simple",
                json={"query": query}
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data["response"]
                
                # Add assistant message to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                
                # Display assistant message
                st.success(f"Assistant: {answer}")
                
                # Display sources if available
                if data.get("sources") and len(data["sources"]) > 0:
                    st.subheader("Sources:")
                    for source in data["sources"]:
                        st.write(f"- {source}")
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Failed to connect to the API: {str(e)}")

# Clear chat button
if st.button("Clear Chat") and len(st.session_state.chat_history) > 0:
    st.session_state.chat_history = []
    st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("ConnectSense RAG System - Powered by LlamaIndex, FAISS, and FastAPI")
