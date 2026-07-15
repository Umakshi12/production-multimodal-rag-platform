"""Production-ready Streamlit web interface for Oceania RAG Chatbot"""

import streamlit as st
import os
from pathlib import Path
from rag_chatbot import create_chatbot
from logger import get_logger
from config import STREAMLIT_PAGE_TITLE, STREAMLIT_PAGE_ICON, STREAMLIT_LAYOUT

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title=STREAMLIT_PAGE_TITLE,
    page_icon=STREAMLIT_PAGE_ICON,
    layout=STREAMLIT_LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #264653;
    }

    /* Main Container */
    .main {
        background-color: #ffffff;
    }

    /* Chat Messages - General */
    [data-testid="stChatMessage"] {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }

    /* User Message Specifics (Avatar override if needed) */
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        font-size: 1rem;
    }

    /* Custom Header Styling */
    .custom-header {
        text-align: center;
        padding-top: 1rem;
        padding-bottom: 0.5rem;
        background: linear-gradient(135deg, #0077B6 0%, #00B4D8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
    }
    
    .custom-subheader {
        text-align: center;
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    /* Source Box */
    .source-box {
        background-color: #e0f2fe;
        border-left: 4px solid #0077B6;
        padding: 1rem;
        margin-top: 0.5rem;
        border-radius: 8px;
        font-size: 0.9rem;
    }

    /* Button Styling */
    .stButton button {
        background-color: #0077B6;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #023E8A;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }
    
    /* Footer & cleaner look */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = create_chatbot()
    logger.info("Chatbot initialized in session")

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'show_retrieval_details' not in st.session_state:
    st.session_state.show_retrieval_details = False


def display_chat_message(role: str, content: str):
    """Display a chat message"""
    if role == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(content)
    else:
        with st.chat_message("assistant", avatar=STREAMLIT_PAGE_ICON):
            st.markdown(content)


def display_sources(sources: list):
    """Display sources in a nice format"""
    if sources:
        with st.expander(f"Sources ({len(sources)})"):
            for source in sources:
                st.markdown(f'<div class="source-box">{source}</div>', unsafe_allow_html=True)


def display_images(images: list):
    """Display images if they exist"""
    if images:
        with st.expander(f"🖼️ Related Images ({len(images)})"):
            for img_path in images:
                if os.path.exists(img_path):
                    try:
                        st.image(img_path, use_column_width=True)
                    except Exception as e:
                        st.warning(f"Could not display image: {img_path}")
                        logger.error(f"Error displaying image: {e}")


# Header
# Header
st.markdown('<h1 class="custom-header">Oceanic6 AI Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="custom-subheader">Expert knowledge on Granite, Quartz, and Custom Solutions</p>', unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.markdown("### 💡 Sample Questions")
    sample_questions = [
        "What are your granite products?",
        "Tell me about quartz slabs",
        "What are your pricing and MOQs?",
        "Do you have quality certifications?"
    ]
    for question in sample_questions:
        if st.button(f"{question}", use_container_width=True, key=f"sample_{question}"):
            st.session_state.user_input = question
            
    st.divider()
    
    # Chat Controls
    if st.button("🔄 Clear History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chatbot.clear_history()
        st.success("History cleared!")
        st.rerun()

    st.divider()

    # Advanced Settings
    with st.expander("⚙️ Advanced Settings"):
        temperature = st.slider(
            "Temperature", 0.0, 1.0, 0.3, 0.1,
            help="Results might utilize this if backend supports it."
        )
        num_sources = st.slider("Sources to retrieve", 1, 10, 5)
        show_details = st.checkbox("Show Retrieval Details", key="show_details_toggle")



# Display chat history
for message in st.session_state.messages:
    display_chat_message(message["role"], message["content"])
    
    # Display sources and images if available
    if message["role"] == "assistant" and "metadata" in message:
        display_sources(message["metadata"].get("sources", []))
        display_images(message["metadata"].get("images", []))
        
        # Show retrieval details if enabled
        if show_details and "retrieval_details" in message["metadata"]:
            with st.expander("🔍 Retrieval Details"):
                details = message["metadata"]["retrieval_details"]
                st.write(f"**Query:** {details['query']}")
                st.write(f"**Retrieved:** {details['num_retrieved']} chunks")
                
                for doc in details['documents']:
                    st.write(f"\n**{doc['rank']}. {doc['source']}** ({doc['source_type']})")
                    st.write(f"__{doc['preview']}__")


# Chat input
st.divider()

user_input = st.chat_input(
    "Ask me anything about Oceanic6 Solutionz...",
    key="chat_input"
)

# Handle sample questions
if "user_input" in st.session_state and st.session_state.user_input:
    user_input = st.session_state.user_input
    st.session_state.user_input = None

if user_input:
    # Add user message to display
    display_chat_message("user", user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get response
    with st.spinner("🤔 Thinking..."):
        try:
            response = st.session_state.chatbot.chat(user_input)
            
            # Display assistant response
            display_chat_message("assistant", response["answer"])
            
            # Store message with metadata
            message_data = {
                "role": "assistant",
                "content": response["answer"],
                "metadata": {
                    "sources": response["sources"],
                    "images": response["images"],
                }
            }
            
            # Add retrieval details if requested
            if show_details:
                retrieval_details = st.session_state.chatbot.get_retrieval_details(user_input)
                message_data["metadata"]["retrieval_details"] = retrieval_details
            
            st.session_state.messages.append(message_data)
            
            # Display sources
            display_sources(response["sources"])
            
            # Display images
            display_images(response["images"])
            
            # Show retrieval details if enabled
            if show_details:
                with st.expander("🔍 Retrieval Details"):
                    retrieval_details = st.session_state.chatbot.get_retrieval_details(user_input)
                    st.write(f"**Query:** {retrieval_details['query']}")
                    st.write(f"**Retrieved:** {retrieval_details['num_retrieved']} chunks")
                    
                    for doc in retrieval_details['documents']:
                        st.write(f"\n**{doc['rank']}. {doc['source']}** ({doc['source_type']})")
                        st.write(f"__{doc['preview']}__")
            
            logger.info(f"Processed query: {user_input}")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            logger.error(f"Error processing query: {e}")

# Footer
st.divider()
st.markdown("""
---
<div style='text-align: center'>
    <p><small>Powered by Oceanic6 Solutionz | RAG Chatbot v1.0</small></p>
    <p><small>Built with LangChain, OpenAI, and Streamlit</small></p>
</div>
""", unsafe_allow_html=True)
