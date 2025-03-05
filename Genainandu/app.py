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
"""

# Allow nested event loops for async operations
nest_asyncio.apply()

def main():
    st.set_page_config(page_title="Math Genius Chatbot", layout="wide")
    
    # Inject Tailwind CSS via CDN and add custom styles
    tailwind_css = """
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
      /* Custom styles for the chatbot interface */
      .chat-container {
          background: rgba(255,255,255,0.9);
          border-radius: 1rem;
          padding: 2rem;
          box-shadow: 0 10px 30px rgba(0,0,0,0.1);
      }
      .chat-title {
          font-size: 2.5rem;
          font-weight: 700;
          color: #2c3e50;
      }
      .chat-subtitle {
          font-size: 1.125rem;
          color: #34495e;
      }
    </style>
    """
    st.markdown(tailwind_css, unsafe_allow_html=True)
    
    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown("<h1 class='text-2xl font-bold mb-4'>About Math Genius Chatbot</h1>", unsafe_allow_html=True)
        st.markdown("""
        <p class="text-gray-700">
            Math Genius Chatbot is your go-to assistant for solving and understanding math problems. Enjoy clear explanations, step-by-step walkthroughs, and beautifully formatted LaTeX solutions.
        </p>
        """, unsafe_allow_html=True)
        st.markdown("<hr class='my-4' />", unsafe_allow_html=True)
        st.markdown("<h2 class='text-xl font-semibold mb-2'>How to Use</h2>", unsafe_allow_html=True)
        st.markdown("""
        <ul class="list-disc list-inside text-gray-700">
            <li>Ask your math question in the chat box below.</li>
            <li>Receive either a quick answer or a detailed step-by-step explanation.</li>
            <li>Follow up on earlier answers if needed.</li>
            <li>Review the final answer in elegant LaTeX format.</li>
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
    <div class="chat-container max-w-4xl mx-auto my-10">
        <h1 class="chat-title text-center">Math Genius Chatbot</h1>
        <p class="chat-subtitle text-center mb-6">Your smart assistant for solving and understanding math problems with clarity.</p>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    
    # Display existing conversation messages with custom styling
    for msg in st.session_state["chat_history"]:
        with st.chat_message("user"):
            st.markdown(f"<div class='p-4 bg-blue-50 rounded-lg mb-2'><p>{msg['question']}</p></div>", unsafe_allow_html=True)
        with st.chat_message("assistant"):
            st.markdown(f"<div class='p-4 bg-green-50 rounded-lg mb-2'><p>{msg['answer']}</p></div>", unsafe_allow_html=True)
    
    # End of main chat container
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ---------------- CHAT INPUT ----------------
    user_query = st.chat_input("Type your math question here...")
    if user_query and user_query.strip():
        st.session_state["chat_history"].append({"question": user_query, "answer": ""})
        
        with st.chat_message("user"):
            st.markdown(f"<div class='p-4 bg-blue-50 rounded-lg mb-2'><p>{user_query}</p></div>", unsafe_allow_html=True)
        
        with st.spinner("Solving your math problem..."):
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
                bot_answer = f"An error occurred: {str(e)}"
        
        st.session_state["chat_history"][-1]["answer"] = bot_answer
        
        with st.chat_message("assistant"):
            st.markdown(f"<div class='p-4 bg-green-50 rounded-lg mb-2'><p>{bot_answer}</p></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
