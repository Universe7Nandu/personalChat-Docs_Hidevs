import sys
import os
import asyncio
import nest_asyncio
import streamlit as st
from langchain_groq import ChatGroq

# ---------------- CONFIG ----------------
GROQ_API_KEY = "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"

# ---------------- SYSTEM PROMPT ----------------
DEFAULT_SYSTEM_PROMPT = """
You are a strong mathematics assistant with expertise in providing both concise and detailed explanations. When the user asks a question, follow these guidelines:
1. If the user requests a minimal response, provide a brief, clear answer.
2. If the user requests a detailed or step-by-step explanation, provide a clear, step-by-step solution, labeling each step as "Step 1", "Step 2", etc.
3. Enclose any math expressions in LaTeX using $$ ... $$.
4. Conclude with a section labeled "Final Answer" that contains the result in LaTeX.
5. Provide strong external knowledge and proper formatting when needed.
6. Maintain a professional and instructive tone.

Example Format for Detailed Answers:
Step 1: Explanation here with $$ \\text{{LaTeX}} $$ if needed.
Step 2: Explanation here with $$ \\text{{LaTeX}} $$ if needed.
...
Final Answer:
$$ \\text{{Answer in LaTeX form}} $$
"""

# Allow nested event loops (for async)
nest_asyncio.apply()

def main():
    st.set_page_config(page_title="Strong Mathematics Chatbot", layout="wide")

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.header("About")
        st.markdown("""
**Strong Mathematics Assistant**  
- Provides both concise and detailed step-by-step solutions  
- Uses LaTeX for math expressions  
- Incorporates strong external knowledge  
- Professional & user-friendly tone
        """)
        st.markdown("---")

        st.header("How to Use")
        st.markdown("""
1. **Ask** a math question in the chat box below.  
2. **Receive** either a brief answer or a detailed, step-by-step solution.  
3. **Ask** follow-up questions referencing previous answers.  
4. **Review** the final answer in LaTeX format.  
5. **Click** "New Chat" to start over.
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
    st.markdown(
        """
        <div class='chat-container' style="
            max-width: 900px; 
            margin: 40px auto; 
            background: rgba(255,255,255,0.85); 
            border-radius: 16px; 
            padding: 25px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        ">
        """, unsafe_allow_html=True
    )

    st.markdown(
        """
        <h1 class='chat-title' style="text-align: center; color: #333333; font-size: 2.4rem; font-weight: 600; margin-bottom: 5px;">
            Strong Mathematics Chatbot
        </h1>
        <p class='chat-subtitle' style="text-align: center; color: #555555; margin-top: 0; margin-bottom: 20px; font-size: 1.1rem;">
            Ask your math questions and get multi-turn, context-aware solutions with LaTeX.
        </p>
        """,
        unsafe_allow_html=True
    )

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
        # Store the user's new question
        st.session_state["chat_history"].append({"question": user_query, "answer": ""})

        # Display user's message
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.spinner("Solving your problem..."):
            # 1. Build the message list with system + prior turns
            messages = []
            # Add system prompt first
            messages.append({"role": "system", "content": DEFAULT_SYSTEM_PROMPT})

            # Add all previous conversation turns
            for turn in st.session_state["chat_history"][:-1]:
                messages.append({"role": "user", "content": turn["question"]})
                messages.append({"role": "assistant", "content": turn["answer"]})

            # Add the newest user query
            messages.append({"role": "user", "content": user_query})

            # 2. Create the LLM instance
            llm = ChatGroq(
                temperature=0.7,
                groq_api_key=GROQ_API_KEY,
                model_name="mixtral-8x7b-32768"
            )

            # 3. Call the LLM with the entire conversation
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
