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
You are an enterprise-grade mathematics assistant capable of solving complex problems, providing interactive guidance, and visualizing solutions. Follow these guidelines:

1. Provide correct solutions with step-by-step explanations using LaTeX for mathematical clarity.
2. Include graphs or diagrams where applicable to enhance visualization.
3. Offer intuitive guidance for users unfamiliar with advanced math concepts.
4. Maintain multi-turn memory to handle follow-up questions effectively.
5. Respond professionally and adaptively based on user needs.
6. If the user asks "Who created this chatbot?", respond with "It was created by Nandesh Kalashetti."
7. If the user asks for contact information, respond with "nandeshkalshetti1@gmail.com."
8. Always prioritize user-friendly responses and professional formatting.

For detailed answers:
Step 1: ...
Step 2: ...
Final Answer: $$ ... $$

For concise answers:
Provide a brief but clear response.

Let's begin!
"""

# Allow nested event loops for async operations
nest_asyncio.apply()

def main():
    st.set_page_config(page_title="Enterprise Mathematics Platform", layout="wide")

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown("<h1 class='text-2xl font-bold mb-4'>About Math Genius</h1>", unsafe_allow_html=True)
        st.markdown("""
        <p class="text-gray-200">
            Welcome to Math Genius, an enterprise-grade platform designed for solving complex mathematical problems with interactive guidance and professional visualization capabilities.
        </p>
        """, unsafe_allow_html=True)
        st.markdown("<hr class='my-4' />", unsafe_allow_html=True)
        st.markdown("<h2 class='text-xl font-semibold mb-2'>Features</h2>", unsafe_allow_html=True)
        st.markdown("""
        <ul class="list-disc list-inside text-gray-200">
            <li>Step-by-step solutions with LaTeX formatting.</li>
            <li>Interactive graphs and diagrams for visualization.</li>
            <li>Multi-turn memory for context-aware problem solving.</li>
            <li>Professional tone and adaptive guidance.</li>
        </ul>
        """, unsafe_allow_html=True)
        st.markdown("<hr class='my-4' />", unsafe_allow_html=True)
        
        if st.button("Start New Chat", key="new_chat"):
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
        <h1 class='chat-title'>Enterprise Mathematics Platform</h1>
        <p class='chat-subtitle'>Solve complex problems with step-by-step solutions, interactive graphs, and professional LaTeX formatting.</p>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display existing conversation
    for msg in st.session_state["chat_history"]:
        with st.chat_message("user"):
            st.markdown(f"<div class='chat-message-user'>{msg['question']}</div>", unsafe_allow_html=True)
        with st.chat_message("assistant"):
            st.markdown(f"<div class='chat-message-assistant'>{msg['answer']}</div>", unsafe_allow_html=True)

    # Chat input field
    user_query = st.chat_input("Type your math question here...")
    if user_query and user_query.strip():
        # Append user's query to chat history
        st.session_state["chat_history"].append({"question": user_query, "answer": ""})
        
        # Display user's message
        with st.chat_message("user"):
            st.markdown(f"<div class='chat-message-user'>{user_query}</div>", unsafe_allow_html=True)

        # Processing the query via LLM
        with st.spinner("Solving your problem..."):
            messages = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
            
            # Add previous conversation turns
            for turn in st.session_state["chat_history"][:-1]:
                messages.append({"role": "user", "content": turn["question"]})
                messages.append({"role": "assistant", "content": turn["answer"]})
            
            # Add current query
            messages.append({"role": "user", "content": user_query})

            llm = ChatGroq(
                temperature=0.7,
                groq_api_key=GROQ_API_KEY,
                model_name="mixtral-8x7b-32768"
            )

            try:
                response = asyncio.run(llm.ainvoke(messages))
                bot_answer = response.content
                
                # Visualization example (e.g., graph rendering)
                if "plot" in user_query.lower():
                    import matplotlib.pyplot as plt
                    import numpy as np
                    
                    x = np.linspace(-10, 10, 100)
                    y = x**2
                    
                    fig, ax = plt.subplots()
                    ax.plot(x, y, label="y = x^2")
                    ax.legend()
                    ax.set_title("Graph of y = x^2")
                    
                    # Render graph in Streamlit
                    st.pyplot(fig)
                
            except Exception as e:
                bot_answer = f"An error occurred: {str(e)}"

        # Append assistant's reply to chat history
        st.session_state["chat_history"][-1]["answer"] = bot_answer
        
        # Display assistant's message
        with st.chat_message("assistant"):
            st.markdown(f"<div class='chat-message-assistant'>{bot_answer}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
