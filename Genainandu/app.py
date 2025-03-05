import sys
import os
import asyncio
import nest_asyncio
import streamlit as st
from langchain_groq import ChatGroq

# ---------------- CONFIGURATION ----------------
GROQ_API_KEY = "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"

# ---------------- SYSTEM PROMPT ----------------
# Includes instructions for multi-turn math help,
# special developer info, and how to handle user requests.
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
    st.set_page_config(page_title="Strong Mathematics Chatbot", layout="wide")

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.header("About")
        st.markdown("""
**Strong Mathematics Chatbot**  
- Provides concise or detailed step-by-step solutions  
- Uses LaTeX for math expressions  
- Multi-turn memory (remembers context)  
- Created by Nandesh Kalashetti
        """)
        st.markdown("---")

        st.header("How to Use")
        st.markdown("""
1. **Ask** a math question in the chat box below.  
2. **Receive** either a brief answer or a detailed, step-by-step solution (with LaTeX).  
3. **Ask** follow-up questions referencing previous answers.  
4. **Click** "New Chat" to start over.
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

    # ---------------- MAIN CHAT AREA ----------------
    # Custom UI styling
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    body {
        background: linear-gradient(135deg, #B2FEFA 0%, #0ED2F7 100%);
        margin: 0; padding: 0;
    }
    header, footer {display: none;}
    .chat-container {
        max-width: 900px;
        margin: 40px auto;
        background: rgba(255,255,255,0.85);
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }
    .chat-title {
        text-align: center;
        color: #333;
        font-size: 2.4rem;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .chat-subtitle {
        text-align: center;
        color: #555;
        margin-top: 0;
        margin-bottom: 20px;
        font-size: 1.1rem;
    }
    /* Sidebar button styling */
    [data-testid="stSidebar"] .stButton>button {
        background: #2ecc71;
        color: #fff;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        transition: background 0.3s;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background: #27ae60;
    }
    /* Chat input styling */
    .stChatInput>div>div>input {
        background-color: #f0f0f0;
        color: #333;
        font-weight: 500;
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 10px;
    }
    .stChatInput>div>div>input:focus {
        outline: 2px solid #2ecc71;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <div class='chat-container'>
            <h1 class='chat-title'>Strong Mathematics Chatbot</h1>
            <p class='chat-subtitle'>
                Ask math questions and get multi-turn, context-aware solutions with LaTeX.
            </p>
        """,
        unsafe_allow_html=True
    )

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display existing conversation
    for msg in st.session_state["chat_history"]:
        with st.chat_message("user"):
            st.markdown(msg["question"])
        with st.chat_message("assistant"):
            st.markdown(msg["answer"])

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- CHAT INPUT ----------------
    user_query = st.chat_input("Type your math question here... (Press Enter)")

    if user_query and user_query.strip():
        # Save the user's new question in session state
        st.session_state["chat_history"].append({"question": user_query, "answer": ""})

        # Display user's message
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.spinner("Solving your problem..."):
            # Build the message list with system + prior turns
            messages = []
            messages.append({"role": "system", "content": DEFAULT_SYSTEM_PROMPT})

            # Add all previous conversation turns
            for turn in st.session_state["chat_history"][:-1]:
                messages.append({"role": "user", "content": turn["question"]})
                messages.append({"role": "assistant", "content": turn["answer"]})

            # Add the newest user query
            messages.append({"role": "user", "content": user_query})

            # Create the LLM instance
            llm = ChatGroq(
                temperature=0.7,
                groq_api_key=GROQ_API_KEY,
                model_name="mixtral-8x7b-32768"
            )

            # Invoke the LLM with the entire conversation
            try:
                response = asyncio.run(llm.ainvoke(messages))
                bot_answer = response.content
            except Exception as e:
                bot_answer = f"An error occurred while processing your request: {str(e)}"

        # Store the assistant's reply
        st.session_state["chat_history"][-1]["answer"] = bot_answer

        # Display assistant's response
        with st.chat_message("assistant"):
            st.markdown(bot_answer)

if __name__ == "__main__":
    main()
