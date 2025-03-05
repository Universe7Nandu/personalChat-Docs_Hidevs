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
You are a mathematics assistant with multi-turn memory. Follow these guidelines:

1. Always read and analyze the entire conversation history before responding.
2. Provide direct answers to the user's specific queries based on the context of previous questions.
3. Use LaTeX formatting for mathematical clarity.
4. Include step-by-step solutions when solving complex problems.
5. If a user asks for clarification or follow-up, refer to previous questions and answers in your response.
6. Avoid generic or convincing responses. Be direct, clear, and accurate.

Example:
User: Solve 2x + 3 = 7.
Assistant: Step 1: Subtract 3 from both sides: 2x = 4.  
Step 2: Divide both sides by 2: x = 2.  
Final Answer: $$x = 2$$.

If the user asks "What was my previous question?", respond with:
"Your previous question was: [question]."

Let's begin!
"""

# Allow nested event loops for async operations
nest_asyncio.apply()

def main():
    st.set_page_config(page_title="MathPal - Multi-Turn Memory 🤖", layout="wide", page_icon="🧮")

    # ---------------- CUSTOM UI STYLING ----------------
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    body {
        background: linear-gradient(135deg, rgba(34,193,195,1) 0%, rgba(253,187,45,1) 100%);
        margin: 0;
        padding: 0;
    }
    
    .chat-container {
        max-width: 900px;
        margin: 40px auto;
        background: rgba(255,255,255,0.95);
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        animation: fadeIn 1s ease-in-out;
    }
    
    .chat-title {
        text-align: center;
        color: #333333;
        font-size: 2.4rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .chat-subtitle {
        text-align: center;
        color: #555555;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stChatInput textarea {
        border-radius: 12px !important;
        padding: 15px !important;
        font-size: 1rem !important;
    }
    
    .user-message {
        background-color: #3498DB !important;
        color: white !important;
        padding: 15px !important;
        border-radius: 12px !important;
        margin-left: auto !important;
    }
    
    .assistant-message {
        background-color: #ECF0F1 !important;
        color: #333333 !important;
        padding: 15px !important;
        border-radius: 12px !important;
        margin-right: auto !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: rgba(44,62,80,0.9) !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.header("MathPal - Multi-Turn Memory 🤖")
        
        st.markdown("""
            MathPal is a smart mathematics assistant that remembers your entire conversation history and provides direct answers based on context.
            
            ### Features:
            - Multi-turn memory for context-aware answers.
            - Step-by-step solutions with LaTeX formatting.
            - Clear and concise responses without generic explanations.
            
            ### How to Use:
            - Ask any math-related question (e.g., solve equations, calculus problems).
            - Follow up with clarifications or related queries.
            - Start a new chat anytime by clicking below.
            
            ---
            """)
        
        if st.button("Start New Chat"):
            st.session_state.pop("chat_history", None)
            st.success("New chat started!")

    # ---------------- MAIN CHAT AREA ----------------
    st.markdown("""
    <div class='chat-container'>
      <h1 class='chat-title'>MathPal 🤖</h1>
      <p class='chat-subtitle'>Ask your math questions and get accurate solutions with memory-aware responses!</p>
      """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display chat history
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(f"<div class='user-message'>{msg['content']}</div>", unsafe_allow_html=True)
        
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(f"<div class='assistant-message'>{msg['content']}</div>", unsafe_allow_html=True)

    # Chat input box
    user_input = st.chat_input("Type your math question here...")
    
    if user_input:
        
        # Add user's message to chat history
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        
        # Display user's message in real-time
        with st.chat_message("user"):
            st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)
        
        # Process user input and generate assistant's response
        with st.spinner("Thinking... 🤔"):
            messages = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
            
            # Add conversation history to messages for context-awareness
            messages.extend(st.session_state["chat_history"])
            
            llm = ChatGroq(
                temperature=0.7,
                groq_api_key=GROQ_API_KEY,
                model_name="mixtral-8x7b-32768"
            )
            
            try:
                response = asyncio.run(llm.ainvoke(messages))
                assistant_response = response.content
                
                # Append assistant's response to chat history
                st.session_state["chat_history"].append({"role": "assistant", "content": assistant_response})
                
                # Display assistant's response in real-time
                with st.chat_message("assistant"):
                    st.markdown(f"<div class='assistant-message'>{assistant_response}</div>", unsafe_allow_html=True)
            
            except Exception as e:
                error_message = f"An error occurred while processing your request 😟\nError details:\n{str(e)}"
                st.session_state["chat_history"].append({"role": "assistant", "content": error_message})
                
                with st.chat_message("assistant"):
                    st.markdown(f"<div class='assistant-message'>{error_message}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
