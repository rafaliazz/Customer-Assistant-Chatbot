-- L2 (Euclidean)
CREATE INDEX IF NOT EXISTS idx_documents_l2
ON documents USING ivfflat (embeddings vector_l2_ops)
WITH (lists = 100);

-- Cosine similarity
CREATE INDEX IF NOT EXISTS idx_documents_cos
ON documents USING ivfflat (embeddings vector_cosine_ops)
WITH (lists = 100);

-- Inner product
CREATE INDEX IF NOT EXISTS idx_documents_ip
ON documents USING ivfflat (embeddings vector_ip_ops)
WITH (lists = 100);

/* 
ALASAN PILIHAN SCHEMA:- 
Saya pilih 3 classical metrik distance dan bandingkan performa mereka secara retrieval speed
Saya pilih mereka karena mereka banyak dokumentasi
*/