"""
RAG Pipeline 
"""

import os
import time
import logging
import psycopg2
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from user_proccessor.user_proccessing import(
    process_user_prompt,
    embed_text,
    semantic_search,
    exact_match_boost,
    rank_and_filter,
)


# ---------------------------
# CONFIG
# ---------------------------

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

TOP_K = 8
SIMILARITY_THRESHOLD = 0.25

GROQ_MODEL = "llama-3.1-8b-instant"


# ---------------------------
# LOGGING
# ---------------------------

logging.basicConfig(
    filename="search_logs.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
)


# ---------------------------
# DB + LLM
# ---------------------------

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name=GROQ_MODEL,
    temperature=0.2,
)


# ---------------------------
# RAG PIPELINE
# ---------------------------

def rag_answer_with_groq(user_query: str):

    start = time.time()

    cleaned = process_user_prompt(user_query)

    # embed + retrieve 
    query_vec = embed_text(cleaned)

    semantic_results = semantic_search(query_vec)

    boosted = exact_match_boost(semantic_results, cleaned)

    ranked = rank_and_filter(boosted)

    # ---- build context
    context_chunks = []

    for doc_id, prompt, response, score in ranked[:5]:

        chunk = (
            f"[Score: {score:.3f}]\n"
            f"Q: {prompt}\n"
            f"A: {response}"
        )

        context_chunks.append(chunk)

    context_text = "\n\n".join(context_chunks)

    system_prompt = f"""
You are a customer assistant chatbot.

Answer ONLY using the information in the provided context.
If the context does not contain the answer, say you do not know
and suggest contacting customer support.

CONTEXT:
{context_text}
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query),
    ]

    response = llm.invoke(messages)

    latency = time.time() - start

    logging.info(
        f"RAG_QUERY='{user_query}' | "
        f"CTX={len(context_chunks)} | "
        f"LATENCY={latency:.4f}s"
    )

    return {
        "answer": response.content,
        "documents": ranked[:5],
        "latency": latency,
    }


# ---------------------------
# CLI TEST MODE
# ---------------------------

if __name__ == "__main__":

    print("\nPgVector + Groq RAG Pipeline Ready\n")

    while True:

        try:
            query = input("User query: ")

            result = rag_answer_with_groq(query)

            print("\nANSWER:\n")
            print(result["answer"])

            print("\nSOURCE DOCUMENTS:\n")

            for i, (doc_id, prompt, response, score) in enumerate(
                result["documents"], 1
            ):
                print(
                    f"{i}. [score={score:.3f}] {prompt}"
                )

            print(f"\nLatency: {result['latency']:.3f}s\n")

        except KeyboardInterrupt:
            print("\nExiting.")
            break
