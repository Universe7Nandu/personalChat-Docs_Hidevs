import sys
import os
import asyncio
import nest_asyncio
import streamlit as st
from langchain_groq import ChatGroq

# 1. CONFIGURATION
GROQ_API_KEY = "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"

# 2. STRONG, STRUCTURED SYSTEM PROMPT
#    - Enforces line-by-line steps, labeled as Step 1, Step 2, etc.
#    - Uses LaTeX for each step as needed.
#    - Concludes with a "Final Answer" in LaTeX.
DEFAULT_SYSTEM_PROMPT = """
You are a strong mathematics assistant. When the user asks a question, do the following:
1. Provide a clear, step-by-step solution, labeling each step as "Step 1", "Step 2", etc.
2. In each step, if you use any math expressions, enclose them in LaTeX: $$ ... $$.
3. Conclude with a section labeled "Final Answer" that contains the result in LaTeX.
4. Maintain a professional and instructive tone.

Example Format:
Step 1: Explanation here with $$ \\text{LaTeX} $$ if needed.
Step 2: Explanation here with $$ \\text{LaTeX} $$ if needed.
...
Final Answer:
$$ \\text{Answer in LaTeX form} $$

Question: {user_query}
"""

# 3. APPLY ASYNC PATCH
nest_asyncio.apply()

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
        background: #BLACK;
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
        background: #000000 !important; /* black background for the input area */
        color:black;
        border-radius: 12px;
        padding: 10px;
        margin-top: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stChatInput>div>div>input {
        background-color: #000000 !important; /* black input box */
        color: #black !important;           /* white text */
        font-weight: 500;
        border-radius: 8px;
        border: 1px solid #bdc3c7;
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
- Line-by-line LaTeX usage  
- Professional & instructive tone
        """)
        st.markdown("---")
        st.header("How to Use")
        st.markdown("""
1. **Ask** a math question in the chat box below.  
2. **Receive** a step-by-step solution, labeled as Step 1, Step 2, etc.  
3. **Check** the final answer in a clear LaTeX form.  
4. **Use** "New Chat" to start fresh.
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
