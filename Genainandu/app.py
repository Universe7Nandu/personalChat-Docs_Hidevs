import sys
import os
import re
import json
import asyncio
import nest_asyncio
import streamlit as st
import plotly.graph_objs as go
import sympy
from sympy.parsing.sympy_parser import parse_expr
from langchain_groq import ChatGroq

# ==============================
#      CONFIGURATION
# ==============================
GROQ_API_KEY = "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"

# For demonstration, a minimal knowledge base:
MATH_CONCEPTS = {
    "derivative rules": """
**Derivative Rules**:
1. d/dx [x^n] = n x^(n-1)
2. d/dx [sin x] = cos x
3. d/dx [cos x] = -sin x
4. d/dx [e^x] = e^x
5. d/dx [ln x] = 1/x
... (etc.)
""",
    "integration rules": """
**Integration Rules**:
1. ∫ x^n dx = x^(n+1)/(n+1) + C
2. ∫ sin x dx = -cos x + C
3. ∫ cos x dx = sin x + C
4. ∫ e^x dx = e^x + C
5. ∫ 1/x dx = ln|x| + C
... (etc.)
""",
    "pythagorean theorem": """
**Pythagorean Theorem**:
For a right triangle with legs a, b and hypotenuse c:
a^2 + b^2 = c^2
"""
}

# ==============================
#     STRONG SYSTEM PROMPT
# ==============================
SYSTEM_PROMPT = """
You are an enterprise-grade mathematics assistant with these capabilities:
1. **Problem Solving**: Provide step-by-step solutions with advanced LaTeX. 
2. **Visualization**: Generate dynamic plots if the user requests a graph, e.g. "Plot x^2 from -2 to 2."
3. **Search**: If the user references a known math concept, incorporate it into your response or direct them to the concept if needed.
4. **Multi-turn Memory**: Always read the entire conversation so far. Refer to prior questions and answers if relevant.
5. **Clarity**: Avoid generic or overly convincing responses. Be direct, accurate, and professional.
6. **Workflow**: If the user specifically says "plot" or "graph," try to create a dynamic Plotly figure. 
7. **Tone**: Maintain a professional and instructive tone. Use LaTeX for math expressions.

Remember:
- Provide detailed steps for complex solutions.
- Summarize with a "Final Answer" in LaTeX if it's a calculation.
- If the user asks "What was my previous question?" respond with the stored conversation content.

Let's begin!
"""

# ==============================
#  ASYNC PATCH & APP START
# ==============================
nest_asyncio.apply()

def main():
    st.set_page_config(
        page_title="Enterprise MathPal",
        layout="wide",
        page_icon="🧮"
    )

    # ===========================
    #         CUSTOM UI
    # ===========================
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    body {
        background: linear-gradient(135deg, #22C1C3 0%, #FDBB2D 100%);
        margin: 0;
        padding: 0;
    }
    .chat-container {
        max-width: 950px;
        margin: 40px auto;
        background: rgba(255,255,255,0.95);
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        animation: fadeIn 1s ease-in-out;
    }
    .chat-title {
        text-align: center;
        color: #333;
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .chat-subtitle {
        text-align: center;
        color: #555;
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
    .user-bubble {
        background-color: #3498DB;
        color: #fff;
        padding: 10px 15px;
        border-radius: 12px;
        margin-left: auto;
        max-width: 80%;
    }
    .assistant-bubble {
        background-color: #ECF0F1;
        color: #333;
        padding: 10px 15px;
        border-radius: 12px;
        margin-right: auto;
        max-width: 80%;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(44,62,80,0.9) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ===========================
    #       SIDEBAR
    # ===========================
    with st.sidebar:
        st.title("Enterprise MathPal 🏢🔢")
        st.markdown("""
**An enterprise-grade mathematics platform** with:
- **Step-by-step solutions** using LaTeX
- **Dynamic plotting** for graphs and diagrams
- **Multi-turn memory** for context-aware answers
- **Quick concept search** to reference math rules

---
        """)
        # Quick search for math concepts
        st.subheader("Search Math Concepts")
        concept_query = st.text_input("Enter a concept (e.g. 'derivative rules')")
        if concept_query:
            # Basic lookup
            lower_query = concept_query.strip().lower()
            if lower_query in MATH_CONCEPTS:
                st.markdown(MATH_CONCEPTS[lower_query])
            else:
                st.warning("No matching concept found. Try 'derivative rules' or 'integration rules'.")

        st.markdown("---")
        # New Chat
        if st.button("New Chat"):
            st.session_state.pop("chat_history", None)
            st.success("New conversation started!")

    # ===========================
    #    MAIN CHAT CONTAINER
    # ===========================
    st.markdown("""
    <div class='chat-container'>
      <h1 class='chat-title'>Enterprise MathPal</h1>
      <p class='chat-subtitle'>Ask your math questions, request plots, or reference math concepts!</p>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display existing conversation
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            with st.chat_message("assistant"):
                st.markdown(f"<div class='assistant-bubble'>{msg['content']}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ===========================
    #       CHAT INPUT
    # ===========================
    user_input = st.chat_input("Type your math query here (e.g., 'Solve x^2=4' or 'Plot x^2 from -2 to 2')")

    if user_input and user_input.strip():
        # Show user bubble
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(f"<div class='user-bubble'>{user_input}</div>", unsafe_allow_html=True)

        # Attempt to parse a "plot" command before calling LLM
        # If recognized, we'll generate a dynamic plot and show it,
        # then let LLM handle the rest of the conversation too.
        plot_generated = False
        plot_figure = None
        parsed_plot = parse_plot_command(user_input)

        if parsed_plot:
            plot_figure = generate_plot(*parsed_plot)  # (expr, x_min, x_max)
            plot_generated = True

        with st.spinner("Thinking..."):
            # Build messages for LLM
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for entry in st.session_state["chat_history"]:
                messages.append({"role": entry["role"], "content": entry["content"]})

            llm = ChatGroq(
                temperature=0.7,
                groq_api_key=GROQ_API_KEY,
                model_name="mixtral-8x7b-32768"
            )

            try:
                response = asyncio.run(llm.ainvoke(messages))
                assistant_response = response.content
            except Exception as e:
                assistant_response = f"Error: {str(e)}"

        # If we made a plot, embed it in the assistant's message:
        if plot_generated and plot_figure is not None:
            # Convert Plotly figure to HTML for embedding
            plot_html = st.plotly_chart(plot_figure, use_container_width=True)
            # We'll add a short text that a plot was generated
            assistant_response += "\n\n(Generated a dynamic plot based on your request.)"

        # Show assistant bubble
        st.session_state["chat_history"].append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(f"<div class='assistant-bubble'>{assistant_response}</div>", unsafe_allow_html=True)

# ===========================
#    PLOT HELPER FUNCTIONS
# ===========================
def parse_plot_command(text):
    """
    Attempts to parse user input like 'plot x^2 from -2 to 2'
    Returns (expr, x_min, x_max) if found, else None
    """
    # Basic detection
    text_lower = text.lower()
    if "plot" not in text_lower:
        return None
    # Example pattern: "plot x^2 from -2 to 2"
    match = re.search(r"plot\s+(.+)\s+from\s+(-?\d+)\s+to\s+(-?\d+)", text_lower)
    if match:
        expr_str = match.group(1).strip()
        try:
            x_min = float(match.group(2))
            x_max = float(match.group(3))
            return (expr_str, x_min, x_max)
        except ValueError:
            return None
    return None

def generate_plot(expr_str, x_min, x_max):
    """
    Generates a Plotly figure for the given expression and range.
    """
    x = sympy.Symbol('x', real=True)
    try:
        parsed_expr = parse_expr(expr_str, transformations=sympy.parsing.sympy_parser.standard_transformations)
    except:
        return None

    # Create data points
    import numpy as np
    xs = np.linspace(x_min, x_max, 200)
    # Evaluate expression
    f = sympy.lambdify(x, parsed_expr, 'numpy')
    try:
        ys = f(xs)
    except:
        return None

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', name=f"{expr_str}"))
    fig.update_layout(
        title=f"Plot of {expr_str} from {x_min} to {x_max}",
        xaxis_title="x",
        yaxis_title="y",
        template="plotly_white"
    )
    return fig

# ===========================
#       ENTRY POINT
# ===========================
if __name__ == "__main__":
    main()
