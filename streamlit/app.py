import streamlit as st
import requests
import os

# API endpoint - get from environment variable or use default
API_URL = os.environ.get("API_URL", "https://connect-sense-apis.vercel.app/")

# Set page config
st.set_page_config(
    page_title="ConnectSense RAG System",
    page_icon="📚",
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar
with st.sidebar:
    st.header("System Controls")
    
    # API URL input
    custom_api_url = st.text_input("API URL (optional)", value=API_URL)
    if custom_api_url != API_URL:
        API_URL = custom_api_url
    
    # Check index status
    if st.button("Check Index Status"):
        try:
            response = requests.get(f"{API_URL}/index/status")
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "success":
                    st.success(f"Index Ready: {data['document_count']} documents")
                else:
                    st.error(f"Index Not Ready")
            else:
                st.error("Failed to check index status")
        except Exception as e:
            st.error(f"Connection Error")
    
    # Clear chat button in sidebar
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# Main header
st.title("ConnectSense RAG System")

# Display chat messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
user_input = st.chat_input("Ask about your documents...")

# Process user input
if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat/simple",
                    json={"query": user_input}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["response"]
                    
                    # Handle sources if available
                    if data.get("sources") and len(data["sources"]) > 0:
                        sources_text = "\n\n**Sources:**\n" + "\n".join([f"- {source}" for source in data["sources"]])
                        answer += sources_text
                    
                    st.markdown(answer)
                    
                    # Add assistant message to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error: Could not get response from API"
                    st.markdown(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = "Failed to connect to the API"
                st.markdown(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

# Simple footer
st.caption("ConnectSense RAG System")