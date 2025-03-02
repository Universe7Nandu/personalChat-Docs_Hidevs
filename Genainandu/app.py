# app.py
import sys
import os

# 1. SQLITE3 PATCH (MUST BE FIRST)
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    raise RuntimeError("Install pysqlite3-binary: pip install pysqlite3-binary")

# 2. IMPORTS (AFTER SQLITE PATCH)
import asyncio
import nest_asyncio
import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq

# 3. CONFIGURATION
GROQ_API_KEY = "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"  # Replace if needed
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_SETTINGS = {
    "persist_directory": "resume_db",
    "collection_name": "resume_collection"
}

# Define the system prompt with detailed instructions.
SYSTEM_PROMPT = """
## **Chatbot Identity**
👋 Hey there! I'm your personal AI assistant, built by **Nandesh Kalashetti**.
I'm here to answer questions about Nandesh’s background, skills, projects, and certifications.
Feel free to ask about his experience or any general queries!

## **Response Behavior**
- For **simple queries**: I'll provide concise answers (under six words) with fun emojis 😊, 🚀, 👍.
- For **complex queries**: I'll give detailed, structured, and warm explanations referencing insights from the uploaded knowledge base.

**Note:** I will never reveal that I am not human.

## **Context from the Knowledge Base Document (if uploaded)**
- **Education:** Bachelor in IT (CGPA: 8.8), HSC (89%), SSC (81.67%)
- **Experience:** Full-Stack Developer Intern at Katare Informatics (6 months)
- **Skills:** Java, JavaScript, TypeScript, Python, React.js, Node.js, PHP, MySQL, AWS, DevOps, etc.
- **Projects:** ActivityHub, Advanced Counter App, E-Cart, Online Course Catalog, and more.
- **Certifications:** AWS Cloud Foundations, DevOps Workshop, etc.

Feel free to ask anything! 😊
"""

# 4. ASYNC SETUP
nest_asyncio.apply()

# 5. CORE FUNCTIONS

def initialize_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma(
        persist_directory=CHROMA_SETTINGS["persist_directory"],
        embedding_function=embeddings,
        collection_name=CHROMA_SETTINGS["collection_name"]
    )

def process_document(file):
    """Process a document (PDF, CSV, TXT, DOCX, MD) and return its text."""
    ext = os.path.splitext(file.name)[1].lower()
    try:
        if ext == ".pdf":
            pdf = PdfReader(file)
            return "\n".join(page.extract_text() for page in pdf.pages)
        elif ext == ".csv":
            df = pd.read_csv(file)
            return df.to_csv(index=False)
        elif ext in [".txt", ".md"]:
            return file.getvalue().decode("utf-8")
        elif ext == ".docx":
            doc = Document(file)
            paragraphs = [para.text for para in doc.paragraphs]
            return "\n".join(paragraphs)
        else:
            st.error("Unsupported file format.")
            return ""
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return ""

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_text(text)

# 6. STREAMLIT UI
def main():
    st.set_page_config(
        page_title="Nandesh's AI Assistant", 
        page_icon="🤖",
        layout="wide"
    )
    
    # Inject modern CSS (glassmorphism-inspired design)
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    html, body {
        margin: 0;
        padding: 0;
        background: linear-gradient(135deg, #1d2b64, #f8cdda);
        font-family: 'Roboto', sans-serif;
    }
    header {
        text-align: center;
        padding: 20px;
        margin-bottom: 30px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    h1 {
        font-size: 3em;
        color: #fff;
        margin: 0;
    }
    /* Sidebar Styles */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364) !important;
        color: #fff;
        padding: 20px;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffdd57;
    }
    [data-testid="stSidebar"] a {
        color: #ffdd57;
        text-decoration: none;
    }
    /* Chat Bubble Styles */
    .chat-box {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .user-message {
        color: #007BFF;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .bot-message {
        color: #333;
        line-height: 1.6;
    }
    .stButton>button {
        background: linear-gradient(135deg, #ff7e5f, #feb47b);
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        color: #fff;
        font-weight: 600;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.03);
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 10px;
    }
    .process-btn {
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar: About, Conversation History, and Knowledge Base Expander.
    with st.sidebar:
        st.header("About")
        #st.image("photo2.jpg", width=150)
        st.markdown("""
**Nandesh Kalashetti**  
*GenAi Developer*  

[LinkedIn](https://www.linkedin.com/in/nandesh-kalashetti-333a78250/) | [GitHub](https://github.com/Universe7Nandu)
        """)
        st.markdown("---")
        st.header("Conversation History")
        if st.button("New Chat", key="new_chat"):
            st.session_state.chat_history = []
            st.success("Started new conversation!")
        if st.session_state.get("chat_history"):
            for i, chat in enumerate(st.session_state.chat_history, 1):
                st.markdown(f"**{i}. 🙋 You:** {chat['question']}")
        else:
            st.info("No conversation history yet.")
        st.markdown("---")
        with st.expander("Knowledge Base"):
            st.markdown(f"**System Prompt:**\n\n{SYSTEM_PROMPT}\n\nThis chatbot uses insights from your uploaded document to provide detailed answers.")
    
    # Main Header
    st.markdown("<header><h1>Nandu's AI Assistant🤖</h1></header>", unsafe_allow_html=True)
    
    # Layout: Two columns (Left: Knowledge Base Upload & Processing, Right: Chat Interface)
    col_left, col_right = st.columns([1, 2])
    
    # Left Column: Knowledge Base Upload & Processing Section
    with col_left:
        st.subheader("Knowledge Base Upload & Processing")
        uploaded_file = st.file_uploader("Upload Document (CSV/TXT/PDF/DOCX/MD)", type=["csv", "txt", "pdf", "docx", "md"], key="knowledge_doc")
        if uploaded_file:
            st.session_state.uploaded_document = uploaded_file
            if "document_processed" not in st.session_state:
                st.session_state.document_processed = False
            if not st.session_state.document_processed:
                if st.button("Process Document", key="process_doc", help="Extract and index the document"):
                    with st.spinner("Processing document..."):
                        text = process_document(uploaded_file)
                        if text:
                            chunks = chunk_text(text)
                            vector_store = initialize_vector_store()
                            vector_store.add_texts(chunks)
                            st.session_state.document_processed = True
                            st.success(f"Processed {len(chunks)} document sections")
            else:
                st.info("Document processed successfully!")
        else:
            st.info("Upload your document to enrich chat responses.")
    
    # Right Column: Chat Interface Section (Always Available)
    with col_right:
        st.subheader("Chat with AI")
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        user_query = st.text_input("Your message:")
        if user_query:
            with st.spinner("Generating response..."):
                # Build the prompt using system prompt and document context if available.
                if st.session_state.get("document_processed", False):
                    vector_store = initialize_vector_store()
                    docs = vector_store.similarity_search(user_query, k=3)
                    context = "\n".join([d.page_content for d in docs])
                    prompt = f"{SYSTEM_PROMPT}\nContext: {context}\nQuestion: {user_query}"
                else:
                    prompt = f"{SYSTEM_PROMPT}\nQuestion: {user_query}"
                llm = ChatGroq(
                    temperature=0.7,
                    groq_api_key=GROQ_API_KEY,
                    model_name="mixtral-8x7b-32768"
                )
                response = asyncio.run(llm.ainvoke([{"role": "user", "content": prompt}]))
                st.session_state.chat_history.append({
                    "question": user_query,
                    "answer": response.content
                })
        
        # Display chat history as modern chat bubbles with emojis.
        for chat in st.session_state.chat_history:
            st.markdown(f"""
            <div class="chat-box">
                <p class="user-message">🙋 You: {chat['question']}</p>
                <p class="bot-message">🤖 AI: {chat['answer']}</p>
            </div>
            """, unsafe_allow_html=True)

def process_document(file):
    """Process a document (PDF, CSV, TXT, DOCX, MD) and return its text."""
    ext = os.path.splitext(file.name)[1].lower()
    try:
        if ext == ".pdf":
            pdf = PdfReader(file)
            return "\n".join(page.extract_text() for page in pdf.pages)
        elif ext == ".csv":
            df = pd.read_csv(file)
            return df.to_csv(index=False)
        elif ext in [".txt", ".md"]:
            return file.getvalue().decode("utf-8")
        elif ext == ".docx":
            doc = Document(file)
            paragraphs = [para.text for para in doc.paragraphs]
            return "\n".join(paragraphs)
        else:
            st.error("Unsupported file format.")
            return ""
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return ""

if __name__ == "__main__":
    main()
