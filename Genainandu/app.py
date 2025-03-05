import sys
import os
import asyncio
import nest_asyncio
import streamlit as st
from langchain_groq import ChatGroq

# ---------------- CONFIGURATION ----------------
GROQ_API_KEY = "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"

# ---------------- SYSTEM PROMPT ----------------
DEFAULT_SYSTEM_PROMPT = """
You are a strong mathematics assistant with multi-turn memory and a user-friendly approach.
Follow these guidelines:

1. Provide concise or step-by-step explanations in LaTeX as the user requests.
2. If a user specifically asks, "Who created this chatbot?" respond with "It was created by Nandesh Kalashetti."
3. If the user specifically asks for the email, respond with "nandeshkalshetti1@gmail.com."
4. Do NOT reveal personal info unless explicitly asked.
5. Provide strong external knowledge when needed and maintain a professional tone.

For detailed math explanations, use:
Step 1: ...
Step 2: ...
Final Answer: $$ ... $$

For minimal answers, be brief but clear.

You can handle various math topics, from algebra to advanced calculus.
Remember prior conversation context to answer follow-up questions accurately.

Let's begin!
"""

# Allow nested event loops (for async)
nest_asyncio.apply()

def main():
    st.set_page_config(page_title="Advanced Math Genius Chatbot", layout="wide")
    
    # Inject advanced CSS styling with animations and transitions
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    body {
        background: linear-gradient(135deg, #2C3E50, #4CA1AF);
        margin: 0; 
        padding: 0;
        overflow-x: hidden;
    }
    header, footer {
        display: none;
    }
    .chat-container {
        max-width: 900px;
        margin: 40px auto;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        animation: fadeIn 1s ease-in-out;
    }
    .chat-title {
        text-align: center;
        color: #2C3E50;
        font-size: 2.8rem;
        font-weight: 600;
        margin-bottom: 10px;
        animation: slideDown 0.8s ease forwards;
    }
    .chat-subtitle {
        text-align: center;
        color: #34495E;
        margin-top: 0;
        margin-bottom: 30px;
        font-size: 1.2rem;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    @keyframes slideDown {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    /* Sidebar styles */
    [data-testid="stSidebar"] {
        background: rgba(44, 62, 80, 0.85) !important;
        color: #ecf0f1;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        color: #ecf0f1;
    }
    [data-testid="stSidebar"] .stButton>button {
        background: #1ABC9C;
        color: #fff;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        transition: background 0.3s ease;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background: #16A085;
    }
    /* Animated chat messages */
    .stChatMessage {
        animation: fadeIn 0.5s ease-in-out;
        margin-bottom: 15px;
    }
    .chat-message-user {
        background-color: #3498DB;
        color: #fff;
        padding: 15px;
        border-radius: 12px;
        max-width: 75%;
        margin-left: auto;
        transition: transform 0.3s ease;
    }
    .chat-message-user:hover {
        transform: scale(1.02);
    }
    .chat-message-assistant {
        background-color: #ECF0F1;
        color: #2C3E50;
        padding: 15px;
        border-radius: 12px;
        max-width: 75%;
        margin-right: auto;
        transition: transform 0.3s ease;
    }
    .chat-message-assistant:hover {
        transform: scale(1.02);
    }
    /* Chat input styling */
    .stChatInput>div>div>input {
        background-color: #F7F9F9;
        color: #2C3E50;
        font-weight: 500;
        border-radius: 12px;
        border: 1px solid #BDC3C7;
        padding: 12px 20px;
        transition: box-shadow 0.3s ease, transform 0.3s ease;
    }
    .stChatInput>div>div>input:focus {
        outline: none;
        box-shadow: 0 0 10px rgba(26, 188, 156, 0.5);
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown("<h1 class='text-2xl font-bold mb-4'>About Math Genius</h1>", unsafe_allow_html=True)
        st.markdown("""
        <p class="text-gray-200">
            Math Genius Chatbot provides clear, step-by-step solutions to your mathematical problems with beautifully rendered LaTeX. Enjoy a multi-turn conversation designed to help you understand complex concepts.
        </p>
        """, unsafe_allow_html=True)
        st.markdown("<hr class='my-4' />", unsafe_allow_html=True)
        st.markdown("<h2 class='text-xl font-semibold mb-2'>How to Use</h2>", unsafe_allow_html=True)
        st.markdown("""
        <ul class="list-disc list-inside text-gray-200">
            <li>Type your math problem below.</li>
            <li>Receive detailed solutions or quick answers with LaTeX.</li>
            <li>Leverage follow-up questions to dive deeper.</li>
            <li>Click "New Chat" to restart the conversation.</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown("<hr class='my-4' />", unsafe_allow_html=True)
        st.markdown("<h2 class='text-xl font-semibold mb-2'>Conversation History</h2>", unsafe_allow_html=True)
        if st.button("New Chat", key="new_chat"):
            st.session_state.pop("chat_history", None)
            st.success("New conversation started!")
        if "chat_history" in st.session_state and st.session_state["chat_history"]:
            for i, item in enumerate(st.session_state["chat_history"], 1):
                st.markdown(f"<p class='mb-1'><strong>{i}. You:</strong> {item['question']}</p>", unsafe_allow_html=True)
        else:
            st.info("No conversation history yet.")
    
    # ---------------- MAIN CHAT AREA ----------------
    st.markdown("""
    <div class='chat-container'>
        <h1 class='chat-title'>Advanced Math Genius Chatbot</h1>
        <p class='chat-subtitle'>Ask math problems and receive multi-turn, context-aware solutions with LaTeX formatting.</p>
    """, unsafe_allow_html=True)
    
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    
    # Display existing conversation with animated chat bubbles
    for msg in st.session_state["chat_history"]:
        with st.chat_message("user"):
            st.markdown(f"<div class='chat-message-user'>{msg['question']}</div>", unsafe_allow_html=True)
        with st.chat_message("assistant"):
            st.markdown(f"<div class='chat-message-assistant'>{msg['answer']}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ---------------- CHAT INPUT ----------------
    user_query = st.chat_input("Type your math question here...")
    if user_query and user_query.strip():
        st.session_state["chat_history"].append({"question": user_query, "answer": ""})
        with st.chat_message("user"):
            st.markdown(f"<div class='chat-message-user'>{user_query}</div>", unsafe_allow_html=True)
        with st.spinner("Solving your problem..."):
            messages = []
            messages.append({"role": "system", "content": DEFAULT_SYSTEM_PROMPT})
            for turn in st.session_state["chat_history"][:-1]:
                messages.append({"role": "user", "content": turn["question"]})
                messages.append({"role": "assistant", "content": turn["answer"]})
            messages.append({"role": "user", "content": user_query})
            
            llm = ChatGroq(
                temperature=0.7,
                groq_api_key=GROQ_API_KEY,
                model_name="mixtral-8x7b-32768"
            )
            
            try:
                response = asyncio.run(llm.ainvoke(messages))
                bot_answer = response.content
            except Exception as e:
                bot_answer = f"An error occurred while processing your request: {str(e)}"
        
        st.session_state["chat_history"][-1]["answer"] = bot_answer
        with st.chat_message("assistant"):
            st.markdown(f"<div class='chat-message-assistant'>{bot_answer}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
