# 🧠 VectorMind AI

### Enterprise RAG Assistant (Generative AI – RAG)

VectorMind AI is a Retrieval-Augmented Generation (RAG) platform that enables users to upload documents and interact with them through natural language queries. The system combines Large Language Models (LLMs), semantic search, vector databases, and document intelligence to deliver accurate, context-aware responses.

---

## 🚀 Features

- 📄 Document Upload & Processing
- 🔍 Semantic Search using Vector Embeddings
- 🤖 AI-Powered Question Answering
- 📝 Document Summarization
- 📊 Document Comparison
- 💡 AI Insights Generation
- ❓ Automatic Question Generation
- 🧠 Context-Aware Responses
- 🌐 Interactive Streamlit Interface

---

## 🏗️ Architecture

```text
User Documents
      │
      ▼
Document Loader
      │
      ▼
Text Chunking
      │
      ▼
Embedding Generation
      │
      ▼
Chroma Vector Database
      │
      ▼
Semantic Retrieval
      │
      ▼
Google Gemini LLM
      │
      ▼
Generated Response
```

---

## 🛠️ Tech Stack

### Frontend
- Streamlit

### Generative AI
- Google Gemini
- LangChain

### Vector Database
- ChromaDB

### Embeddings
- Google Generative AI Embeddings

### Backend
- Python

### Document Processing
- PyPDF
- Text Processing Utilities

---

## 📂 Project Structure

```text
VectorMind-AI/
│
├── app.py
├── requirements.txt
├── .env
├── README.md
│
├── data/
├── chroma_db/
├── uploads/
│
├── utils/
├── embeddings/
└── vectorstore/
```

---

## ⚙️ Prerequisites

### Python

Recommended:

```text
Python 3.10+
```

Check Version:

```bash
python --version
```

---

## 🔑 API Key Setup

Create a `.env` file in the project root.

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY
```

Get your API Key:

https://aistudio.google.com

---

## 📦 Installation

### Clone Repository

```bash
git clone https://github.com/Varunkurhade1674/VectorMind-AI-Enterprise-RAG-Assistant-Generative-AI-RAG-.git

cd VectorMind-AI-Enterprise-RAG-Assistant-Generative-AI-RAG-
```

---

### Create Virtual Environment

Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Application

```bash
python -m streamlit run app.py
```

Application URL:

```text
http://localhost:8505
```

---

## 📖 How It Works

### Step 1

Upload PDF or text documents.

### Step 2

The system:

- Extracts document content
- Splits text into chunks
- Generates embeddings
- Stores vectors in ChromaDB

### Step 3

Ask questions in natural language.

### Step 4

Relevant document chunks are retrieved.

### Step 5

Gemini generates an accurate context-aware answer.

---

## 🔥 Core AI Features

### Semantic Search

Find relevant information using meaning rather than keywords.

### Question Answering

Ask questions directly from uploaded documents.

### Summarization

Generate concise summaries from large documents.

### AI Insights

Automatically identify important concepts and findings.

### Document Comparison

Compare multiple uploaded documents.

---

## 📸 Example Queries

```text
Summarize this document.
```

```text
What are the key findings?
```

```text
Compare Document A and Document B.
```

```text
Generate interview questions from this document.
```

```text
Explain the main concepts in simple terms.
```

---

## 📈 Future Enhancements

- Multi-PDF Chat
- Voice-Based Queries
- Citation-Based Answers
- GraphRAG Integration
- Multi-Language Support
- Local LLM Support (Ollama)
- Cloud Deployment

---

## 💼 Resume Description

### VectorMind AI – Enterprise RAG Assistant (Generative AI – RAG)

- Built a Retrieval-Augmented Generation (RAG) platform for document search, summarization, and contextual question answering.
- Integrated Google Gemini, LangChain, and ChromaDB to enable semantic search and intelligent knowledge retrieval.
- Developed AI-powered features including document comparison, question generation, and context-aware responses through a Streamlit interface.

---

## 🏷️ Category

```text
Generative AI
    ↓
Retrieval-Augmented Generation (RAG)
    ↓
Document Intelligence
```

---

## 👨💻 Author

**Varun Kurhade**

---

## 📜 License

MIT License
