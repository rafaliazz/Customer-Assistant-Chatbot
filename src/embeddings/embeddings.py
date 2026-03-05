"""
Generate embeddings for documents and normalize both text and vectors.
Also updates the prompt and response in the database for consistency.
"""

import os
import re
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

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

# Load embedding model (384 dims → matches schema)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Fetch rows WITHOUT embeddings
cur.execute("""
    SELECT id, prompt, response
    FROM documents
""")
rows = cur.fetchall()
print(f"Found {len(rows)} documents to embed.")

BATCH_SIZE = 64

def normalize_text(text: str) -> str:
    """Clean and normalize text for consistent embeddings."""
    text = text.lower()  # lowercase
    text = re.sub(r'[^\w\s]', '', text)  # remove punctuation
    text = ' '.join(text.split())  # remove extra spaces
    return text.strip()

for i in tqdm(range(0, len(rows), BATCH_SIZE)):
    batch = rows[i:i + BATCH_SIZE]

    texts = []
    ids = []
    clean_prompts = []
    clean_responses = []

    for doc_id, prompt, response in batch:
        # Normalize individual columns
        clean_prompt = normalize_text(prompt or '')
        clean_response = normalize_text(response or '')

        # Combine text for embedding
        combined_text = f"Question: {clean_prompt}\nAnswer: {clean_response}".strip()
        if combined_text:
            texts.append(combined_text)
            ids.append(doc_id)
            clean_prompts.append(clean_prompt)
            clean_responses.append(clean_response)

    if not texts:
        continue

    # Generate normalized embeddings
    embeddings = model.encode(texts, normalize_embeddings=True)

    # Update embeddings and cleaned text in database
    for doc_id, emb, clean_prompt, clean_response in zip(ids, embeddings, clean_prompts, clean_responses):
        cur.execute(
            "UPDATE documents SET embeddings = %s, prompt = %s, response = %s WHERE id = %s",
            (emb.tolist(), clean_prompt, clean_response, doc_id)
        )

    conn.commit()

cur.close()
conn.close()

print("Embedding generation completed.")

"""
DOKUMENTASI DATA INGESTION:- 
- CSV yang dipakai sudah ada 5 kolom: ID, Category, Prompt, Response, Embeddings
- Embeddings/Tags awalnya kosong tapi di isikan sesuai:- 
    * Embeddings: kita pakai .py file ini 
    (normalizasi text -> Prompt+response di gabungkan -> Embed -> Ingest ke SQL Table (Prompt, Response, Embeddings))
    * Tags: pakai skripsi .sql bisa ditemukan di "create_tags.sql". Saya pakai fungsi "CASE WHEN" untuk cari untuk 
    keywords yang relevan untuk setiap Tag, dan tambahkan Tag itu pas bisa ditemukan di prompt-nya. 
"""