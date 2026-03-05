-- Enable the vector extension (needed for embeddings)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,

    category VARCHAR(50) NOT NULL,

    prompt TEXT NOT NULL,

    response TEXT NOT NULL,

    embeddings VECTOR(1536)
);
-- Index for fast filtering by category
CREATE INDEX IF NOT EXISTS idx_documents_kategori ON documents(category);

ALTER TABLE documents
ADD COLUMN IF NOT EXISTS tag TEXT[];

-- index for fast filtering of tags 
CREATE INDEX IF NOT EXISTS idx_documents_tags ON documents USING GIN(tag);

ALTER TABLE documents
DROP COLUMN embeddings;

ALTER TABLE documents
ADD COLUMN embeddings VECTOR(384);

/* 
ALASAN PILIHAN SCHEMA:- 
- ID: Untuk identifikasi beda beda rows 
- Category: Untuk filtering/explainability
- Tags: Untuk Untuk filtering/explainability 
- Embeddings: Dipakai untuk Semantic Search + RAG  

Kita pakai index untuk kolom Category dan Tag jadi bisa lebih cepat untuk retrieval 
*/
