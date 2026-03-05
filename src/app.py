import streamlit as st
import time

# ---------------------------
# IMPORT YOUR PIPELINE
# ---------------------------

from rag.rag_pipeline import rag_answer_with_groq
from user_proccessor.user_proccessing import process_user_prompt


# ---------------------------
# PAGE CONFIG
# ---------------------------

st.set_page_config(
    page_title="Customer Assistant RAG",
    layout="wide",
)

st.title("Customer Assistant Chatbot (RAG + Groq)")

st.caption(
    "Ask our super friendly RAG-Assistant for customer assistance"
)

# ---------------------------
# SESSION STATE
# ---------------------------

if "history" not in st.session_state:
    st.session_state.history = []


# ---------------------------
# INPUT BOX
# ---------------------------

query = st.text_input(
    "Ask a customer support question:",
    placeholder="My app keeps crashing and I cannot log into my account..."
)


# ---------------------------
# SUBMIT
# ---------------------------

if st.button("Ask") and query:

    with st.spinner("Searching knowledge base..."):

        start = time.time()

        cleaned = process_user_prompt(query)

        result = rag_answer_with_groq(cleaned)

        elapsed = time.time() - start

    st.session_state.history.append(
        (query, result["answer"])
    )


    # ---------------------------
    # OUTPUT
    # ---------------------------
    st.subheader("Assistant Response")
    st.write(result["answer"])

    st.subheader("Retrieved Documents")
    for i, (doc_id, prompt, response, score) in enumerate(
            result["documents"], 1
        ):
        st.write(
            f"{i}. [score={score:.3f}] {prompt}"
        )

    st.write(f"\nLatency: {result['latency']:.3f}s\n")



# ---------------------------
# CHAT HISTORY
# ---------------------------

if st.session_state.history:

    st.divider()
    st.subheader("Conversation History")

    for q, a in reversed(st.session_state.history):
        st.markdown(f"**User:** {q}")
        st.markdown(f"**Assistant:** {a}")
