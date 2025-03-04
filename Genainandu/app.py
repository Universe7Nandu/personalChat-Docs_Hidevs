import sys
import os
import asyncio
import nest_asyncio
import streamlit as st
from langchain_groq import ChatGroq

# 1. CONFIGURATION
GROQ_API_KEY = "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"

# 2. STRONG, STRUCTURED SYSTEM PROMPT
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

    # 4. BRAND-NEW UI STYLING
    #    - Changed background gradient
    #    - Updated chat container styles
    #    - New colors for the sidebar
    #    - Input box with a different look
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    body {
        /* A fresh, vibrant gradient background */
        background: linear-gradient(135deg, #00c9ff 0%, #92fe9d 100%);
        margin: 0; padding: 0;
    }
    header, footer { display: none; }

    /* Main chat container */
    .chat-container {
        max-width: 900px;
        margin: 40px auto;
        background: rgba(255,255,255,0.85);
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }

    /* Title and subtitle styling */
    .chat-title {
        text-align: center;
        color: #333333;
        font-size: 2.4rem;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .chat-subtitle {
        text-align: center;
        color: #555555;
        margin-top: 0;
        margin-bottom: 20px;
        font-size: 1.1rem;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #34495e !important;
        color: #ecf0f1 !important;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #e67e22 !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #ecf0f1 !important;
    }
    [data-testid="stSidebar"] .stButton>button {
        background: #e67e22 !important;
        color: #fff !important;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        transition: background 0.3s;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background: #d35400 !important;
    }

    /* Chat input styling */
    .stChatInput {
        position: sticky;
        bottom: 0;
        background: #ffffff;
        backdrop-filter: blur(6px);
        padding: 10px;
        margin-top: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .stChatInput>div>div>input {
        background-color: #f0f0f0;
        color: #333333;
        font-weight: 500;
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 10px;
    }
    .stChatInput>div>div>input:focus {
        outline: 2px solid #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

    # -------- SIDEBAR --------
    with st.sidebar:
        st.header("About")
        st.markdown("""
**Strong Mathematics Assistant**  
- Step-by-step solutions  
- LaTeX for math expressions  
- Professional & instructive tone
        """)
        st.markdown("---")
        st.header("How to Use")
        st.markdown("""
1. **Ask** a math question in the chat box below.  
2. **Receive** a step-by-step solution, labeled as Step 1, Step 2, etc.  
3. **Check** the final answer in LaTeX form.  
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

    # -------- MAIN CHAT AREA --------
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    st.markdown("<h1 class='chat-title'>Strong Mathematics Chatbot</h1>", unsafe_allow_html=True)
    st.markdown("<p class='chat-subtitle'>Ask your math questions and get step-by-step, LaTeX-enhanced solutions.</p>", unsafe_allow_html=True)

    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display existing conversation
    for msg in st.session_state["chat_history"]:
        with st.chat_message("user"):
            st.markdown(msg["question"])
        with st.chat_message("assistant"):
            st.markdown(msg["answer"])
    st.markdown("</div>", unsafe_allow_html=True)

    # -------- CHAT INPUT --------
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
