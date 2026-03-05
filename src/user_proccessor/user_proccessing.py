"""
Query Processing + Retrieval Pipeline (COSINE SIMILARITY)
-------------------------------------------------------

Features:
- Prompt normalization
- Embedding generation
- PgVector cosine search
- Relevance thresholding
- Hybrid semantic + keyword matching
- Ranking
- Logging analytics
"""

import os
import re
import time
import logging
import psycopg2
from typing import List, Tuple
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


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

MODEL_NAME = "all-MiniLM-L6-v2"

TOP_K = 8

# Tune after benchmarking
SIMILARITY_THRESHOLD = 0.25


# ---------------------------
# LOGGING
# ---------------------------

logging.basicConfig(
    filename="search_logs.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
)


# ---------------------------
# DB + MODEL
# ---------------------------

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

model = SentenceTransformer(MODEL_NAME)


# ---------------------------
# TEXT NORMALIZATION
# ---------------------------

def process_user_prompt(text: str) -> str:
    """Normalize user input same as ingestion."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = " ".join(text.split())
    return text.strip()


# ---------------------------
# EMBEDDING
# ---------------------------

def embed_text(text: str):
    text = process_user_prompt(text)
    return model.encode(
        text,
        normalize_embeddings=True,
    ).tolist()


# ---------------------------
# SEMANTIC SEARCH (COSINE)
# ---------------------------

def semantic_search(
    query_vec,
    limit: int = TOP_K,
):
    """
    Uses COSINE distance (<=>)
    Lower = better
    Converted to similarity = 1 - distance
    """

    sql = """
        SELECT
            id,
            prompt,
            response,
            1 - (embeddings <=> %s::vector) AS similarity
        FROM documents
        ORDER BY embeddings <=> %s::vector
        LIMIT %s;
    """

    cur.execute(sql, (query_vec, query_vec, limit))
    return cur.fetchall()


# ---------------------------
# EXACT MATCH BOOST
# ---------------------------

def exact_match_boost(results, query: str):

    tokens = set(query.split())
    boosted = []

    for doc_id, prompt, response, score in results:

        prompt_norm = process_user_prompt(prompt or "")
        overlap = len(tokens.intersection(prompt_norm.split()))

        bonus = 0.05 * overlap

        boosted.append(
            (doc_id, prompt, response, score + bonus)
        )

    return boosted


# ---------------------------
# RANK + FILTER
# ---------------------------

def rank_and_filter(results):

    filtered = [
        r for r in results if r[3] >= SIMILARITY_THRESHOLD
    ]

    return sorted(filtered, key=lambda x: x[3], reverse=True)


# ---------------------------
# PIPELINE ENTRYPOINT
# ---------------------------

def search_pipeline(user_query: str):

    start = time.time()

    cleaned = process_user_prompt(user_query)
    query_vec = embed_text(cleaned)

    semantic_results = semantic_search(query_vec)

    boosted = exact_match_boost(semantic_results, cleaned)

    ranked = rank_and_filter(boosted)

    latency = time.time() - start

    logging.info(
        f"QUERY='{user_query}' | "
        f"CLEAN='{cleaned}' | "
        f"RESULTS={len(ranked)} | "
        f"LATENCY={latency:.4f}s"
    )

    return ranked, latency


# ---------------------------
# CLI TEST MODE
# ---------------------------

if __name__ == "__main__":

    print("\nPgVector Cosine Search Pipeline Ready\n")

    while True:

        try:
            query = input("User query: ")

            results, latency = search_pipeline(query)

            print(f"\nReturned {len(results)} results in {latency:.3f}s\n")

            for i, (doc_id, prompt, response, score) in enumerate(results, 1):

                print(
                    f"{i}. [score={score:.3f}] "
                    f"{prompt[:80]}"
                )

        except KeyboardInterrupt:
            print("\nExiting.")
            break

"""
HASIL RESULTS:- 
SUKSES PROMPT YANG DI HASILKAN CUKUP RELEVAN UNTUK SAMPLE QUESTIONS 
- "I was charged twice for my order and I cannot find my receipt email. How do I fix this?" 
- "My app keeps crashing and I cannot log into my account anymore."
- "Can I get a refund for shipping fees if my order was delayed?"
Similarity threshold 0.25 cukup bagus
"""