import sys
import os
import asyncio
import nest_asyncio
import streamlit as st
from langchain_groq import ChatGroq
import matplotlib.pyplot as plt
import numpy as np

# ---------------- CONFIGURATION ----------------
GROQ_API_KEY = "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"

# ---------------- SYSTEM PROMPT ----------------
DEFAULT_SYSTEM_PROMPT = """
You are a friendly mathematics genius assistant 🤓. Follow these guidelines:

1. Provide clear explanations with LaTeX math formatting 💡
2. Use emojis to make responses approachable and engaging 🎯
3. Offer step-by-step solutions for complex problems 📝
4. Create visualizations/graphs when relevant 📊
5. Maintain multi-conversation memory 🔄
6. For basic questions, give concise answers with 1-2 emojis ⚡
7. For advanced topics, break down into numbered steps 📚
8. Always be encouraging and patient 🌟
9. Use these response starters:
   - "Great question! Let's break it down... 🔍"
   - "Wonderful! Here's how we solve this... 🚀"
   - "Excellent query! The solution involves... 💡"

Example Response:
"To solve ∫x² dx from 0 to 2:
1️⃣ First, find the antiderivative: ∫x² dx = (x³)/3 + C
2️⃣ Evaluate at bounds: (2³)/3 - (0³)/3 = 8/3
3️⃣ Final answer: $$\\frac{8}{3}$$ 📐

Need more details? Just ask! 😊"
"""

# ---------------- UI CONFIGURATION ----------------
BACKGROUND_GRADIENT = """
background: linear-gradient(135deg, 
    rgba(106,76,147,0.95) 0%, 
    rgba(72,152,176,0.95) 50%, 
    rgba(34,193,195,0.95) 100%);
"""

nest_asyncio.apply()

def main():
    st.set_page_config(page_title="MathPal 🤖", layout="wide", page_icon="🧮")
    
    # ---------------- CUSTOM STYLES ----------------
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    * {{
        font-family: 'Inter', sans-serif;
    }}
    
    body {{
        {BACKGROUND_GRADIENT}
        background-attachment: fixed;
    }}
    
    .chat-container {{
        max-width: 900px;
        margin: 2rem auto;
        backdrop-filter: blur(10px);
        background: rgba(255,255,255,0.9);
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        padding: 2rem;
        animation: slideUp 0.6s ease;
    }}
    
    @keyframes slideUp {{
        0% {{ transform: translateY(40px); opacity: 0; }}
        100% {{ transform: translateY(0); opacity: 1; }}
    }}
    
    .stChatInput textarea {{
        border-radius: 15px !important;
        padding: 1rem !important;
        font-size: 1.1rem !important;
        border: 2px solid #6a4c93 !important;
        transition: all 0.3s ease !important;
    }}
    
    .stChatInput textarea:focus {{
        box-shadow: 0 0 15px rgba(106,76,147,0.3) !important;
    }}
    
    .user-message {{
        background: #6a4c93 !important;
        color: white !important;
        border-radius: 15px 15px 0 15px !important;
        margin-left: auto;
        max-width: 70%;
        animation: fadeIn 0.4s ease;
    }}
    
    .assistant-message {{
        background: #f3f4f6 !important;
        border-radius: 15px 15px 15px 0 !important;
        margin-right: auto;
        max-width: 70%;
        animation: fadeIn 0.4s ease;
        position: relative;
    }}
    
    .assistant-message::before {{
        content: "🧮";
        position: absolute;
        left: -40px;
        top: 10px;
        font-size: 1.5rem;
    }}
    
    [data-testid="stSidebar"] {{
        background: rgba(42, 47, 79, 0.9) !important;
        backdrop-filter: blur(5px) !important;
        border-right: 1px solid rgba(255,255,255,0.1) !important;
    }}
    
    .sidebar-header {{
        color: white !important;
        font-size: 1.8rem !important;
        padding: 1rem !important;
        border-bottom: 2px solid rgba(255,255,255,0.1) !important;
    }}
    
    .history-item {{
        padding: 0.8rem;
        margin: 0.5rem 0;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    
    .history-item:hover {{
        background: rgba(255,255,255,0.2);
        transform: translateX(5px);
    }}
    </style>
    """, unsafe_allow_html=True)

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown("""
        <div class='sidebar-header'>
            MathPal History 📚
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ New Chat", use_container_width=True):
            st.session_state.pop("chat_history", None)
            st.success("New session started! 🎉")
        
        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
        
        if "chat_history" in st.session_state:
            for idx, item in enumerate(st.session_state.chat_history):
                st.markdown(f"""
                <div class='history-item'>
                    <div style='color: #ddd; font-size: 0.9rem;'>Q{idx+1}: {item['question'][:50]}...</div>
                </div>
                """, unsafe_allow_html=True)

    # ---------------- MAIN INTERFACE ----------------
    st.markdown("""
    <div class='chat-container'>
        <h1 style='
            text-align: center;
            color: #2d2d2d;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        '>
            MathPal 🤖
        </h1>
        <p style='
            text-align: center;
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        '>
            Your friendly mathematics companion • Ask anything from basic arithmetic to advanced calculus! 📚
        </p>
    """, unsafe_allow_html=True)

    # ---------------- CHAT HISTORY ----------------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message("user", avatar="🧑💻"):
            st.markdown(f"<div class='user-message'>{msg['question']}</div>", unsafe_allow_html=True)
        
        with st.chat_message("assistant", avatar="🤖"):
            response = msg['answer'].replace("$$", "$")  # Fix LaTeX rendering
            st.markdown(f"<div class='assistant-message'>{response}</div>", unsafe_allow_html=True)
            
            # Auto-generate graphs for relevant responses
            if "graph" in msg['question'].lower():
                x = np.linspace(-5, 5, 100)
                y = np.sin(x) if "sin" in msg['question'].lower() else x**2
                
                fig, ax = plt.subplots()
                ax.plot(x, y, color='#6a4c93')
                ax.set_title("Visualization 📈")
                st.pyplot(fig)

    # ---------------- CHAT INPUT ----------------
    user_input = st.chat_input("Ask any math question... 🚀 (E.g.: 'Explain integration basics')")
    
    if user_input and user_input.strip():
        # Add to chat history
        st.session_state.chat_history.append({
            "question": user_input,
            "answer": ""
        })
        
        # Display user message
        with st.chat_message("user", avatar="🧑💻"):
            st.markdown(f"<div class='user-message'>{user_input}</div>", unsafe_allow_html=True)
        
        # Process query
        with st.spinner("Analyzing your question... 🔍"):
            messages = [{"role": "system", "content": DEFAULT_SYSTEM_PROMPT}]
            
            # Add previous conversation context
            for turn in st.session_state.chat_history[:-1]:
                messages.append({"role": "user", "content": turn["question"]})
                messages.append({"role": "assistant", "content": turn["answer"]})
            
            messages.append({"role": "user", "content": user_input})
            
            try:
                llm = ChatGroq(
                    temperature=0.7,
                    groq_api_key=GROQ_API_KEY,
                    model_name="mixtral-8x7b-32768"
                )
                
                response = asyncio.run(llm.ainvoke(messages))
                bot_response = response.content
                
                # Add visualization for relevant responses
                if any(keyword in user_input.lower() for keyword in ["graph", "plot", "visualize"]):
                    x = np.linspace(-5, 5, 100)
                    y = np.sin(x) if "sin" in user_input.lower() else x**2
                    
                    fig, ax = plt.subplots()
                    ax.plot(x, y, color='#6a4c93')
                    ax.set_title("Visualization 📈")
                    st.pyplot(fig)
                
            except Exception as e:
                bot_response = f"Oops! Something went wrong 😟\nError: {str(e)}"
            
            # Update chat history
            st.session_state.chat_history[-1]["answer"] = bot_response
        
        # Display assistant response
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(f"<div class='assistant-message'>{bot_response}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
