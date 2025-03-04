import sys
import os
import asyncio
import nest_asyncio
import streamlit as st
from langchain_groq import ChatGroq

# 1. CONFIGURATION
GROQ_API_KEY = "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"

# 2. SYSTEM PROMPT (STRONG, STEP-BY-STEP, LaTeX-FOCUSED)
DEFAULT_SYSTEM_PROMPT = """
## Strong Mathematics Assistant
You are an advanced mathematics assistant with a strong emphasis on step-by-step solutions. 
When a user asks a question, you must:
1. Provide a clear step-by-step derivation or explanation.
2. Use LaTeX formatting for all math expressions (surrounded by $$).
3. Provide the final answer in LaTeX as well.
4. Maintain a professional, instructive tone.
5. If possible, give additional insights or alternative methods.

Question: {user_query}
"""

# 3. APPLY ASYNC PATCH
nest_asyncio.apply()

# 4. MAIN APPLICATION FUNCTION
def main():
    st.set_page_config(page_title="Strong Mathematics Chatbot", layout="wide")
    
    # --- Modern CSS for a Professional Look & Feel ---
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background: linear-gradient(135deg, #eef1f5 0%, #ffffff 100%);
    }
    header, footer { display: none; }

    /* Container for chat */
    .chat-container {
        max-width: 900px;
        margin: 40px auto;
        background: #ffffff;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }

    /* Title & subtitle styling */
    .chat-title {
        text-align: center;
        color: #2c3e50;
        font-size: 2.2rem;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .chat-subtitle {
        text-align: center;
        color: #4f5f6f;
        margin-top: 0;
        margin-bottom: 20px;
        font-size: 1.1rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #2c3e50 !important;
        color: #ecf0f1 !important;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #e74c3c !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #ecf0f1 !important;
    }
    [data-testid="stSidebar"] .stButton>button {
        background: #e74c3c !important;
        color: #fff !important;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        transition: background 0.3s;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background: #c0392b !important;
    }

    /* Chat input styling */
    .stChatInput {
        position: sticky;
        bottom: 0;
        background: #f7f9fb;
        color:black;
        border-radius: 12px;
        padding: 10px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stChatInput>div>div>input {
        color: #2c3e50;
        font-weight: 500;
        border-radius: 8px;
        border: 1px solid #bdc3c7;
        background-color: #ffffff;
        padding: 10px;
    }
    .stChatInput>div>div>input:focus {
        outline: 2px solid #2980b9;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.header("About")
        st.markdown("""
**Strong Mathematics Assistant**  
- Step-by-step solutions  
- LaTeX-formatted derivations  
- Professional & instructive tone
        """)
        st.markdown("---")
        st.header("How to Use")
        st.markdown("""
1. **Ask** a math question in the chat box.  
2. **Receive** a detailed, line-by-line solution with LaTeX.  
3. **Follow up** for clarifications or alternative methods.
        """)
        st.markdown("---")
        st.header("Conversation History")
        if st.button("New Chat"):
            st.session_state.pop("chat_history", None)
            st.success("New conversation started! 🆕")
        if "chat_history" in st.session_state and st.session_state["chat_history"]:
            for i, item in enumerate(st.session_state["chat_history"], 1):
                st.markdown(f"{i}. **You**: {item['question']}")
        else:
            st.info("No conversation history yet.")

    # --- MAIN CHAT AREA ---
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    st.markdown("<h1 class='chat-title'>Strong Mathematics Chatbot</h1>", unsafe_allow_html=True)
    st.markdown("<p class='chat-subtitle'>Ask your math questions and get step-by-step, LaTeX-enhanced solutions.</p>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display existing conversation
    for msg in st.session_state["chat_history"]:
        with st.chat_message("user"):
            st.markdown(msg["question"])
        with st.chat_message("assistant"):
            st.markdown(msg["answer"])
    st.markdown("</div>", unsafe_allow_html=True)

    # --- CHAT INPUT ---
    user_query = st.chat_input("Type your math question here... (Press Enter)")
    if user_query:
        st.session_state["chat_history"].append({"question": user_query, "answer": ""})
        with st.chat_message("user"):
            st.markdown(user_query)
        with st.spinner("Solving your problem..."):
            # Build the prompt
            prompt = DEFAULT_SYSTEM_PROMPT.format(user_query=user_query)
            llm = ChatGroq(
                temperature=0.7,
                groq_api_key=GROQ_API_KEY,
                model_name="mixtral-8x7b-32768"
            )
            # Invoke the LLM asynchronously
            response = asyncio.run(llm.ainvoke([{"role": "user", "content": prompt}]))
            bot_answer = response.content
        
        st.session_state["chat_history"][-1]["answer"] = bot_answer
        with st.chat_message("assistant"):
            st.markdown(bot_answer)

if __name__ == "__main__":
    main()
