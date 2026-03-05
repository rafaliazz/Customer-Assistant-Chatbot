"""
Benchmark similarity search performance using multiple distance metrics.
Runs 5 random queries and reports average timing.
"""

import os
import time
import psycopg2
import re
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# Connect to PostgreSQL
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------
# Normalization + Embedding
# ---------------------------

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = " ".join(text.split())
    return text.strip()


def generate_embedding(text: str):
    text = normalize_text(text)
    return model.encode(text, normalize_embeddings=True).tolist()


# ---------------------------
# Similarity Search Function
# ---------------------------

def run_similarity_search(query_vec, metric="l2", limit=5):

    operator = {
        "l2": "<->",
        "cosine": "<=>",
        "ip": "<#>",
    }[metric]

    sql = f"""
        SELECT id, prompt, response
        FROM documents
        ORDER BY embeddings {operator} %s::vector
        LIMIT {limit};
    """

    start = time.time()
    cur.execute(sql, (query_vec,))
    results = cur.fetchall()
    elapsed = time.time() - start

    return results, elapsed


# ---------------------------
# Benchmark Runner
# ---------------------------

if __name__ == "__main__":

    # Fetch 5 random prompts
    cur.execute("""
        SELECT prompt
        FROM documents
        ORDER BY RANDOM()
        LIMIT 5;
    """)

    queries = [row[0] for row in cur.fetchall()]

    print(f"\nRunning benchmark with {len(queries)} random queries...\n")

    metrics = ["l2", "cosine", "ip"]

    timing_summary = {m: [] for m in metrics}

    for i, user_query in enumerate(queries, start=1):

        print(f"\n==============================")
        print(f"Query {i}: {user_query}")
        print(f"==============================")

        query_vec = generate_embedding(user_query)

        for metric in metrics:

            results, elapsed = run_similarity_search(query_vec, metric)

            timing_summary[metric].append(elapsed)

            print(f"\n--- Metric: {metric.upper()} ---")
            print(f"Time: {elapsed:.4f}s")

            for idx, (doc_id, prompt, response) in enumerate(results, 1):
                print(
                    f"{idx}. ID {doc_id} | "
                    f"{prompt[:40]} | "
                    f"{response[:40]}"
                )

    # ---------------------------
    # Print averages
    # ---------------------------

    print("\n==============================")
    print("AVERAGE QUERY TIMES (5 runs)")
    print("==============================")

    for metric in metrics:
        avg = sum(timing_summary[metric]) / len(timing_summary[metric])
        print(f"{metric.upper():8}: {avg:.4f} seconds")

    cur.close()
    conn.close()

'''
HASIL RESULTS:- 
==============================
AVERAGE QUERY TIMES (5 runs)
==============================
L2      : 0.0024 seconds
COSINE  : 0.0020 seconds
IP      : 0.0024 seconds

SECARA SPEED SEMUANYA SAMA PERSIS PERFORMANYA JADI SAYA PILIH COSINE KARENA ITU DISTANCE METRIC YANG PALING 
DIPAKAI DALAM DOKUMENTASI 
'''
