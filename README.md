# Customer-Assistant-Chatbot 

A **Retrieval-Augmented Generation (RAG)** based **LLM chatbot** designed to answer technical customer service questions using a structured internal knowledge base.

The chatbot retrieves relevant policies from a **PostgreSQL** database, performs **vector similarity search** using **PgVector**, and generates accurate responses using the **Groq LLM API.**

# Instructions

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Customer-Assistant-Chatbot.git
cd Customer-Assistant-Chatbot
```

---

## 2. Create a Python Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

**Linux / macOS**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Install PostgreSQL

Install PostgreSQL if it is not already installed.

Then create a new database:

```sql
CREATE DATABASE customer_chatbot;
```

---

## 5. Enable PgVector Extension

Connect to the database and enable the extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 6. Create the Documents Table

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    embeddings VECTOR(1536)
);
```
## 7. Add Environment Variables

Create a `.env` file in the project root:

```
# Database
DB_HOST= your_db_host
DB_PORT= your_db_port
DB_NAME= your_db_name
DB_USER= your_db_user
DB_PASSWORD= your_db_password

# Groq
GROQ_API_KEY= your_groq_api_key
```
## 8. Generate and Store Embeddings

Run the embedding script to convert the **50 policies** into vectors and store them in PostgreSQL.

```bash
python embeddings/embeddings.py
```
## 9. Start the Chatbot

Run the chatbot:

```bash
python streamlit "src\app.py"
```