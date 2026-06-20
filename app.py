import os
import shutil
import tempfile
from pathlib import Path
import streamlit as st
import pandas as pd

# Import dotenv to read local .env files if present
from dotenv import load_dotenv

load_dotenv()

import json
import datetime
import time

DATA_STORE_PATH = "data_store.json"

# --- Multiple Document Collections ---
COLLECTIONS = {
    "Resume Collection": "chroma_db/resumes",
    "Research Papers Collection": "chroma_db/research",
    "Project Reports Collection": "chroma_db/reports",
    "General Documents Collection": "chroma_db/general"
}

def load_data_store():
    default_store = {
        "analytics": {
            "queries_count": 0,
            "total_response_time": 0.0,
            "latency_history": []
        },
        "collections_meta": {
            "Resume Collection": {"files": [], "chunks_count": 0},
            "Research Papers Collection": {"files": [], "chunks_count": 0},
            "Project Reports Collection": {"files": [], "chunks_count": 0},
            "General Documents Collection": {"files": [], "chunks_count": 0}
        }
    }
    if os.path.exists(DATA_STORE_PATH):
        try:
            with open(DATA_STORE_PATH, "r", encoding="utf-8") as f:
                store = json.load(f)
                # Ensure latency_history exists
                if "analytics" in store and "latency_history" not in store["analytics"]:
                    store["analytics"]["latency_history"] = []
                return store
        except Exception:
            return default_store
    return default_store

def save_data_store(store):
    try:
        with open(DATA_STORE_PATH, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error saving data store: {e}")

def get_current_time_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_markdown_export(messages):
    lines = ["# Chat History Export - VectorMind AI\n", f"Generated on: {get_current_time_str()}\n\n---\n"]
    for msg in messages:
        role = "Assistant" if msg["role"] == "assistant" else "User"
        timestamp = msg.get("timestamp", get_current_time_str())
        
        lines.append(f"### 🕒 [{timestamp}] **{role}**\n")
        lines.append(f"{msg['content']}\n\n")
        
        if role == "Assistant" and "citations" in msg and msg["citations"]:
            lines.append("#### 📚 Sources Referenced:\n")
            for idx, cite in enumerate(msg["citations"]):
                page_info = f", Page {cite['page'] + 1}" if cite.get("page") is not None else ""
                lines.append(f"- **[{idx+1}] {cite['source_name']}**{page_info} (Distance: {cite['score']:.4f})\n")
                lines.append(f"  > *\"{cite['content']}\"*\n")
            lines.append("\n")
        lines.append("---\n\n")
    return "".join(lines)

def generate_txt_export(messages):
    lines = ["Chat History Export - VectorMind AI\n", f"Generated on: {get_current_time_str()}\n", "="*50 + "\n\n"]
    for msg in messages:
        role = "Assistant" if msg["role"] == "assistant" else "User"
        timestamp = msg.get("timestamp", get_current_time_str())
        
        lines.append(f"[{timestamp}] {role}:\n")
        lines.append(f"{msg['content']}\n\n")
        
        if role == "Assistant" and "citations" in msg and msg["citations"]:
            lines.append("Sources Referenced:\n")
            for idx, cite in enumerate(msg["citations"]):
                page_info = f", Page {cite['page'] + 1}" if cite.get("page") is not None else ""
                lines.append(f"  [{idx+1}] {cite['source_name']}{page_info} (Distance: {cite['score']:.4f})\n")
                lines.append(f"      \"{cite['content']}\"\n")
            lines.append("\n")
        lines.append("-"*50 + "\n\n")
    return "".join(lines)

if "data_store" not in st.session_state:
    st.session_state["data_store"] = load_data_store()

# --- Page Configuration ---
st.set_page_config(
    page_title="VectorMind AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS Section for Premium SaaS Styling ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Hide default Streamlit visual headers & footprint */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {
        background: transparent !important;
        z-index: 99 !important;
    }
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stActionButton"] {display: none !important;}
    
    /* Global Application styling */
    .stApp {
        background: radial-gradient(circle at top left, #0e121a 0%, #07090d 100%) !important;
        color: #f1f5f9 !important;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.15);
    }
    
    /* Premium Collapsible Sidebar */
    [data-testid="stSidebar"] {
        background-color: #090c13 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.04) !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding: 2rem 1.5rem !important;
    }
    
    /* Sidebar Headers */
    .sidebar-section-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin: 24px 0 12px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        padding-bottom: 6px;
    }
    
    /* Hero Branding Layout */
    .hero-container {
        display: flex;
        align-items: center;
        padding: 24px;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.4) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(245, 158, 11, 0.04) 0%, transparent 60%);
        pointer-events: none;
    }
    .hero-logo {
        font-size: 2.2rem;
        background: linear-gradient(135deg, #d4af37, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-color: rgba(245, 158, 11, 0.08);
        padding: 12px;
        border-radius: 16px;
        border: 1px solid rgba(245, 158, 11, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        margin-right: 20px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    .hero-content {
        flex-grow: 1;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #ffffff, #cbd5e1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        margin: 4px 0 0 0;
        font-weight: 400;
    }
    
    /* Metrics Grid & Glassmorphism Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.015) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        border-radius: 16px !important;
        padding: 18px 14px !important;
        text-align: center !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.3s ease !important;
    }
    .metric-card:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(245, 158, 11, 0.25) !important;
        box-shadow: 0 8px 24px rgba(245, 158, 11, 0.08) !important;
        background: rgba(255, 255, 255, 0.03) !important;
    }
    .metric-icon {
        font-size: 1.8rem;
        margin-bottom: 8px;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    }
    .metric-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #f59e0b;
        margin-bottom: 4px;
        background: linear-gradient(135deg, #f59e0b, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-subtitle {
        font-size: 0.7rem;
        color: #64748b;
    }
    
    /* Expander override */
    .stExpander {
        background: rgba(255, 255, 255, 0.01) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
        margin-bottom: 24px !important;
        overflow: hidden !important;
    }
    .stExpander > details > summary {
        background-color: rgba(255, 255, 255, 0.01) !important;
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        padding: 14px 18px !important;
        font-size: 0.9rem !important;
        border-bottom: 1px solid transparent !important;
        transition: all 0.2s ease !important;
    }
    .stExpander > details[open] > summary {
        border-bottom: 1px solid rgba(255, 255, 255, 0.04) !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
    }
    .stExpander > details > summary:hover {
        color: #d4af37 !important;
        background-color: rgba(255, 255, 255, 0.02) !important;
    }
    
    /* Document Drag-and-drop & Ingest Container */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.005) !important;
        border: 2px dashed rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        padding: 14px !important;
        transition: border-color 0.3s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #d4af37 !important;
    }
    
    /* Buttons & Inputs styling */
    .stButton>button {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px rgba(217, 119, 6, 0.2) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    .stButton>button:active {
        transform: translateY(1px) !important;
    }
    
    .stTextInput input, .stSelectbox [data-baseweb="select"], .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.015) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 10px !important;
        color: #f1f5f9 !important;
        transition: border-color 0.2s ease !important;
    }
    .stTextInput input:focus, .stSelectbox [data-baseweb="select"]:focus {
        border-color: #d4af37 !important;
    }
    
    /* Custom Pill Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.015) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 6px !important;
        border-radius: 14px !important;
        gap: 6px !important;
        margin-bottom: 24px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        color: #94a3b8 !important;
        padding: 10px 20px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(245, 158, 11, 0.1) !important;
        color: #fbbf24 !important;
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
    }
    
    /* Modern Chat Bubble System */
    /* Hide Streamlit default chat borders & backgrounds */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0px !important;
        margin-bottom: 0px !important;
    }
    
    /* User Chat Bubble Class */
    div[data-testid="stChatMessage"]:has(.user-chat-bubble-content) {
        background: linear-gradient(135deg, #78350f 0%, #451a03 100%) !important;
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
        border-radius: 18px 18px 4px 18px !important;
        padding: 16px 20px !important;
        max-width: 80% !important;
        margin-left: auto !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
        margin-bottom: 18px !important;
    }
    
    /* Assistant Chat Bubble Class */
    div[data-testid="stChatMessage"]:has(.assistant-chat-bubble-content) {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-left: 3px solid #d4af37 !important;
        border-radius: 18px 18px 18px 4px !important;
        padding: 16px 20px !important;
        max-width: 80% !important;
        margin-right: auto !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
        margin-bottom: 18px !important;
    }
    
    /* Avatars styling */
    div[data-testid="chatAvatarIcon-user"], div[data-testid="chatAvatarIcon-assistant"] {
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 50% !important;
    }
    
    /* Pulsing Typing Cursor Indicator */
    @keyframes pulse {
        0% { opacity: 0.2; }
        50% { opacity: 1; }
        100% { opacity: 0.2; }
    }
    .typing-cursor {
        display: inline-block;
        width: 6px;
        height: 14px;
        background-color: #d4af37;
        margin-left: 6px;
        animation: pulse 1s infinite;
        vertical-align: middle;
    }
    
    /* Citation Cards Layout */
    .citation-card {
        background: rgba(255, 255, 255, 0.015) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        border-left: 3px solid #d4af37 !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        margin-top: 10px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        transition: all 0.2s ease !important;
    }
    .citation-card:hover {
        background: rgba(255, 255, 255, 0.03) !important;
        border-color: rgba(245, 158, 11, 0.2) !important;
    }
    .citation-meta {
        font-size: 0.8rem;
        font-weight: 600;
        color: #f59e0b;
        margin-bottom: 4px;
    }
    .citation-content {
        font-size: 0.85rem;
        color: #cbd5e1;
        font-style: italic;
        line-height: 1.4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Hero / Branding Header ---
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-logo">🤖</div>
        <div class="hero-content">
            <h1 class="hero-title">VectorMind AI</h1>
            <p class="hero-subtitle">Powered by RAG and Semantic Search</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Dashboard Home Screen / Analytics Rendering ---
def render_analytics_dashboard():
    store = st.session_state["data_store"]
    total_docs = sum(len(meta["files"]) for meta in store["collections_meta"].values())
    total_chunks = sum(meta["chunks_count"] for meta in store["collections_meta"].values())
    total_embeddings = total_chunks
    queries = store["analytics"]["queries_count"]
    total_time = store["analytics"]["total_response_time"]
    avg_time = total_time / queries if queries > 0 else 0.0
    total_collections = len(COLLECTIONS)
    
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-icon">📁</div>
                <div class="metric-title">Total Documents</div>
                <div class="metric-value">{total_docs}</div>
                <div class="metric-subtitle">Across folders</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">🗂️</div>
                <div class="metric-title">Total Collections</div>
                <div class="metric-value">{total_collections}</div>
                <div class="metric-subtitle">Isolated stores</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">✂️</div>
                <div class="metric-title">Total Chunks</div>
                <div class="metric-value">{total_chunks}</div>
                <div class="metric-subtitle">Text segments</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">❓</div>
                <div class="metric-title">Total Queries</div>
                <div class="metric-value">{queries}</div>
                <div class="metric-subtitle">Served requests</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">⚡</div>
                <div class="metric-title">Avg Latency</div>
                <div class="metric-value">{avg_time:.2f}s</div>
                <div class="metric-subtitle">Response speed</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Collection statistics charts
    col_names = list(store["collections_meta"].keys())
    col_files = [len(store["collections_meta"][c]["files"]) for c in col_names]
    col_chunks = [store["collections_meta"][c]["chunks_count"] for c in col_names]
    
    chart_data = pd.DataFrame({
        "Collection": col_names,
        "Documents": col_files,
        "Chunks": col_chunks
    }).set_index("Collection")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("<p style='font-size: 0.9rem; font-weight: 600; color: #94a3b8; margin-top: 10px; margin-bottom: 8px;'>📦 Chunk Allocation per Collection</p>", unsafe_allow_html=True)
        st.bar_chart(chart_data["Chunks"], use_container_width=True)
        
    with col_c2:
        st.markdown("<p style='font-size: 0.9rem; font-weight: 600; color: #94a3b8; margin-top: 10px; margin-bottom: 8px;'>📈 Query Latency History (seconds)</p>", unsafe_allow_html=True)
        latency_history = store["analytics"].get("latency_history", [])
        if not latency_history:
            latency_history = [0.0]
        st.line_chart(latency_history, use_container_width=True)

with st.expander("📊 SYSTEM DASHBOARD & ANALYTICS", expanded=False):
    st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
    render_analytics_dashboard()

# --- Sidebar Configuration ---
st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 10px 0;">
        <span style="font-size: 2.2rem; filter: drop-shadow(0 2px 4px rgba(245,158,11,0.3));">🤖</span>
        <h2 style="font-size: 1.3rem; font-weight: 800; color: #ffffff; margin: 10px 0 2px 0;">VectorMind AI</h2>
        <p style="font-size: 0.75rem; color: #94a3b8; font-weight: 400; margin: 0 0 15px 0;">Powered by RAG and Semantic Search</p>
    </div>
    """,
    unsafe_allow_html=True
)

# API Key check from env
env_api_key = os.getenv("GEMINI_API_KEY", "")
with st.sidebar.expander("⚙️ Gemini API Configuration", expanded=not env_api_key):
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        value=env_api_key,
        placeholder="Enter API Key (or set GEMINI_API_KEY env variable)"
    )

st.sidebar.markdown("<div class='sidebar-section-title'>📂 Active Collection</div>", unsafe_allow_html=True)
selected_collection = st.sidebar.selectbox(
    "Select Active Collection",
    list(COLLECTIONS.keys()),
    label_visibility="collapsed"
)
DB_DIR = COLLECTIONS[selected_collection]

st.sidebar.markdown("<div class='sidebar-section-title'>📁 Ingest Documents</div>", unsafe_allow_html=True)
uploaded_files = st.sidebar.file_uploader(
    "Choose PDF or Text files",
    type=["pdf", "txt"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

# --- Import Libraries Dynamically to Handle API Key Checking Promptly ---
def get_rag_components(google_api_key):
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        try:
            from langchain_chroma import Chroma
        except ImportError:
            from langchain_community.vectorstores import Chroma

        # Configure Embeddings Model
        embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001", 
            google_api_key=google_api_key
        )
        
        # Configure LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0.01,
            streaming=True
        )
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        
        return embeddings, llm, splitter, Chroma
    except Exception as e:
        st.error(f"Error loading LangChain Google modules: {e}")
        return None, None, None, None

# Run sanity check on API key
if not api_key:
    st.warning("⚠️ Please provide your Google Gemini API Key in the sidebar expander to run the application.")
    st.sidebar.info("You can get a Gemini API key for free from Google AI Studio.")
    st.stop()

# Initialize LangChain components
embeddings, llm, splitter, Chroma = get_rag_components(api_key)

if not embeddings:
    st.stop()

# Helper to get or load database
def get_db():
    if not st.session_state.get("db_initialized", {}).get(selected_collection, False):
        return None
    if not os.path.exists(DB_DIR):
        return None
        
    if "db_instance" not in st.session_state or st.session_state["db_instance"] is None:
        try:
            st.session_state["db_instance"] = Chroma(
                persist_directory=DB_DIR,
                embedding_function=embeddings
            )
        except Exception as e:
            st.error(f"Error loading Chroma DB: {e}")
            return None
    return st.session_state["db_instance"]

# Helper to fetch all segments of a document from Chroma DB
def get_all_document_segments(file_name, db_dir, embeddings):
    if not os.path.exists(db_dir):
        return []
    try:
        db = get_db()
        if db is None:
            return []
        collection = db._collection
        data = collection.get()
        docs = []
        for doc_id, text, metadata in zip(data["ids"], data["documents"], data["metadatas"]):
            source = metadata.get("source", "")
            if os.path.basename(source) == file_name:
                docs.append(text)
        return docs
    except Exception as e:
        st.error(f"Error retrieving document chunks: {e}")
        return []

# Helper to unload database before deletion
def unload_db():
    if "db_instance" in st.session_state and st.session_state["db_instance"] is not None:
        db = st.session_state["db_instance"]
        if hasattr(db, "_client") and hasattr(db._client, "close"):
            try:
                db._client.close()
            except Exception:
                pass
        st.session_state["db_instance"] = None
    import gc
    gc.collect()

# Helper to safely delete database folder
def delete_db_dir(db_dir):
    import gc
    import time
    
    if st.session_state.get("db_in_use", False):
        st.error("Cannot delete database: Database is currently loaded and in use.")
        return False
        
    unload_db()
    gc.collect()
    time.sleep(0.5)
    
    if os.path.exists(db_dir):
        try:
            shutil.rmtree(db_dir)
            return True
        except PermissionError as e:
            st.error(f"PermissionError: Unable to delete database folder. It is locked by the system or another process (Windows File Lock). Details: {e}")
            return False
        except Exception as e:
            st.error(f"Error deleting database: {e}")
            return False
    return True

# Helper to render source citations in professional card layouts
def render_citations(citations):
    if not citations:
        return
    st.markdown("<div style='margin-top: 15px; margin-bottom: 8px; font-weight: 600; color: #f59e0b; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px;'>📚 Source Citations</div>", unsafe_allow_html=True)
    
    for idx, cite in enumerate(citations):
        source_name = cite.get("source_name", "Unknown Document")
        page = cite.get("page", None)
        score = cite.get("score", None)
        content = cite.get("content", "")
        
        score_text = f"Distance: {score:.4f}" if score is not None else ""
        page_text = f"Page {page + 1}" if page is not None else ""
        
        meta_info = " • ".join(filter(None, [source_name, page_text, score_text]))
        
        st.markdown(
            f"""
            <div class="citation-card">
                <div class="citation-meta">[{idx+1}] {meta_info}</div>
                <div class="citation-content">"{content}"</div>
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Process Uploaded Files ---
def process_documents(files):
    documents = []
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            file_path = Path(temp_dir) / file.name
            with open(file_path, "wb") as f:
                f.write(file.getvalue())
            
            try:
                if file.name.endswith(".pdf"):
                    loader = PyPDFLoader(str(file_path))
                    documents.extend(loader.load())
                elif file.name.endswith(".txt"):
                    loader = TextLoader(str(file_path), encoding="utf-8")
                    documents.extend(loader.load())
            except Exception as e:
                st.error(f"Failed to load {file.name}: {e}")
                
    if not documents:
        return None
        
    chunks = splitter.split_documents(documents)
    return chunks

# Button to index uploaded documents with progress animation
if uploaded_files:
    if st.sidebar.button("Index Documents ⚡", use_container_width=True):
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        status_text.markdown("<p style='font-size:0.85rem;color:#f59e0b;'>Reading & processing files...</p>", unsafe_allow_html=True)
        progress_bar.progress(20)
        chunks = process_documents(uploaded_files)
        
        if chunks:
            progress_bar.progress(50)
            status_text.markdown("<p style='font-size:0.85rem;color:#f59e0b;'>Generating embeddings & indexing...</p>", unsafe_allow_html=True)
            
            st.session_state["db_in_use"] = True
            try:
                if os.path.exists(DB_DIR):
                    db = get_db()
                    if db is None:
                        db = Chroma.from_documents(
                            documents=chunks,
                            embedding=embeddings,
                            persist_directory=DB_DIR
                        )
                        st.session_state["db_instance"] = db
                    else:
                        db.add_documents(chunks)
                else:
                    db = Chroma.from_documents(
                        documents=chunks,
                        embedding=embeddings,
                        persist_directory=DB_DIR
                    )
                    st.session_state["db_instance"] = db
                
                progress_bar.progress(90)
                st.session_state["db_initialized"][selected_collection] = True
                
                # Update local persistent data store
                store = st.session_state["data_store"]
                current_files = set(store["collections_meta"][selected_collection]["files"])
                for f in uploaded_files:
                    current_files.add(f.name)
                store["collections_meta"][selected_collection]["files"] = list(current_files)
                store["collections_meta"][selected_collection]["chunks_count"] += len(chunks)
                save_data_store(store)
                
                progress_bar.progress(100)
                status_text.markdown("<p style='font-size:0.85rem;color:#10b981;font-weight:600;'>Indexing Complete! 🎉</p>", unsafe_allow_html=True)
                st.sidebar.success("Success: Documents indexed in collection!")
                time.sleep(1.5)
                
            except Exception as e:
                st.sidebar.error(f"Error indexing documents: {e}")
                status_text.markdown("<p style='font-size:0.85rem;color:#ef4444;font-weight:600;'>Indexing Failed ❌</p>", unsafe_allow_html=True)
            finally:
                st.session_state["db_in_use"] = False
                progress_bar.empty()
                status_text.empty()
                st.rerun()

# Display indexed files if database exists on disk
if "db_initialized" not in st.session_state:
    st.session_state["db_initialized"] = {}
    for col_name, col_path in COLLECTIONS.items():
        st.session_state["db_initialized"][col_name] = os.path.exists(col_path)

if os.path.exists(DB_DIR):
    st.session_state["db_initialized"][selected_collection] = True
else:
    st.session_state["db_initialized"][selected_collection] = False

# Render document preview cards and clear database button
store = st.session_state["data_store"]
files = store["collections_meta"][selected_collection].get("files", [])

if st.session_state["db_initialized"].get(selected_collection, False):
    st.sidebar.markdown("<div class='sidebar-section-title'>📚 Indexed Documents</div>", unsafe_allow_html=True)
    if files:
        for f in files:
            icon = "📄" if f.lower().endswith(".pdf") else "📝"
            st.sidebar.markdown(
                f"""
                <div style="
                    background: rgba(255, 255, 255, 0.02);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    padding: 8px 12px;
                    margin-bottom: 8px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                ">
                    <span style="font-size: 1rem;">{icon}</span>
                    <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 0.8rem; color: #cbd5e1; flex-grow: 1;" title="{f}">
                        {f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.sidebar.markdown("<p style='font-size:0.85rem;color:#64748b;'>No files in collection.</p>", unsafe_allow_html=True)
        
    if st.sidebar.button("Clear Vector DB 🗑️", use_container_width=True):
        if delete_db_dir(DB_DIR):
            st.session_state["db_initialized"][selected_collection] = False
            store = st.session_state["data_store"]
            store["collections_meta"][selected_collection]["files"] = []
            store["collections_meta"][selected_collection]["chunks_count"] = 0
            save_data_store(store)
            st.sidebar.success(f"{selected_collection} cleared successfully!")
            st.rerun()

# --- Export Conversation ---
if st.session_state.get("messages", []):
    st.sidebar.markdown("<div class='sidebar-section-title'>📥 Export Workspace</div>", unsafe_allow_html=True)
    md_history = generate_markdown_export(st.session_state["messages"])
    txt_history = generate_txt_export(st.session_state["messages"])
    
    col_d1, col_d2 = st.sidebar.columns(2)
    with col_d1:
        st.sidebar.download_button(
            label="Markdown 📄",
            data=md_history,
            file_name=f"chat_history_{selected_collection.lower().replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col_d2:
        st.sidebar.download_button(
            label="Plain Text 📝",
            data=txt_history,
            file_name=f"chat_history_{selected_collection.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant", 
            "content": "Hello! I am your AI assistant powered by Gemini. Ask me anything, or upload files in the sidebar to search local custom knowledge.",
            "timestamp": get_current_time_str(),
            "citations": []
        }
    ]

# --- Tabs Navigation ---
tabs = st.tabs([
    "💬 AI Chat", 
    "📝 Summarizer", 
    "🔍 Information Extractor", 
    "🧠 Question Generator", 
    "📑 Document Comparison", 
    "💡 AI Insights"
])

with tabs[0]:
    # Render chat history
    for msg in st.session_state["messages"]:
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        marker_class = "assistant-chat-bubble-content" if msg["role"] == "assistant" else "user-chat-bubble-content"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(f'<div class="{marker_class}"></div>', unsafe_allow_html=True)
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "citations" in msg and msg["citations"]:
                render_citations(msg["citations"])

    # --- Handle User Query & Response Pipeline ---
    if query := st.chat_input("Ask a question about your documents..."):
        start_time = time.time()
        user_time_str = get_current_time_str()
        
        # Render user query
        st.session_state["messages"].append({
            "role": "user", 
            "content": query,
            "timestamp": user_time_str
        })
        with st.chat_message("user", avatar="👤"):
            st.markdown('<div class="user-chat-bubble-content"></div>', unsafe_allow_html=True)
            st.markdown(query)
            
        # Generate RAG response
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown('<div class="assistant-chat-bubble-content"></div>', unsafe_allow_html=True)
            
            # Placeholder for streaming text
            response_placeholder = st.empty()
            full_response = ""
            
            # Check if vector DB is available to retrieve context
            context = ""
            retrieved_docs_with_scores = []
            
            db_init = st.session_state.get("db_initialized", {}).get(selected_collection, False)
            if db_init and os.path.exists(DB_DIR):
                try:
                    st.session_state["db_in_use"] = True
                    db = get_db()
                    if db:
                        # Query Vector DB with score
                        retrieved_docs_with_scores = db.similarity_search_with_score(query, k=4)
                        context = "\n\n".join([doc.page_content for doc, _ in retrieved_docs_with_scores])
                except Exception as e:
                    st.error(f"Error reading vector database: {e}")
                finally:
                    st.session_state["db_in_use"] = False
            
            # Construct RAG Prompt template
            if context:
                prompt = f"""
### You are a helpful, respectful and honest assistant to help the user with questions.
Please refer to the search results obtained from the local knowledge base.
But be careful to not incorporate the information that you think is not relevant to the question.
If you don't know the answer to a question, please don't share false information.

### Search results:
{context}

### Question:
{query}

### Answer:
"""
            else:
                prompt = query
                
            citations = []
            for doc, score in retrieved_docs_with_scores:
                source = doc.metadata.get("source", "Unknown")
                page = doc.metadata.get("page", None)
                citations.append({
                    "source_name": os.path.basename(source),
                    "page": page,
                    "score": float(score),
                    "content": doc.page_content
                })

            if retrieved_docs_with_scores:
                with st.expander("📚 View Retrieved Document Context Chunks", expanded=False):
                    for idx, (doc, score) in enumerate(retrieved_docs_with_scores):
                        source = doc.metadata.get("source", "Unknown")
                        page = doc.metadata.get("page", None)
                        page_text = f" | Page {page + 1}" if page is not None else ""
                        st.markdown(f"**Chunk {idx+1}** (Source: `{os.path.basename(source)}` {page_text} | Similarity Distance: {score:.4f}):")
                        st.info(doc.page_content)
            
            # Run streaming LLM query
            try:
                for chunk in llm.stream(prompt):
                    full_response += chunk.content
                    response_placeholder.markdown(full_response + '<span class="typing-cursor"></span>', unsafe_allow_html=True)
                response_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"Error invoking Google Gemini model: {e}")
                full_response = "Sorry, I encountered an error while communicating with the model API."
                response_placeholder.markdown(full_response)
                
            if citations:
                render_citations(citations)
                
            duration = time.time() - start_time
            
            # Save query analytics
            store = st.session_state["data_store"]
            if "latency_history" not in store["analytics"]:
                store["analytics"]["latency_history"] = []
            store["analytics"]["queries_count"] += 1
            store["analytics"]["total_response_time"] += duration
            store["analytics"]["latency_history"].append(duration)
            if len(store["analytics"]["latency_history"]) > 20:
                store["analytics"]["latency_history"].pop(0)
            save_data_store(store)
            
            st.session_state["messages"].append({
                "role": "assistant", 
                "content": full_response,
                "citations": citations,
                "timestamp": get_current_time_str()
            })
            st.rerun()

with tabs[1]:
    st.markdown("### 📝 Smart Document Summarization")
    store = st.session_state["data_store"]
    doc_list = store["collections_meta"][selected_collection]["files"]
    if not doc_list:
        st.info("No documents uploaded yet in this collection. Upload files in the sidebar first.")
    else:
        selected_doc = st.selectbox("Select Document to Summarize", doc_list, key="sum_doc_select")
        summary_type = st.radio(
            "Select Summary Type",
            ["Executive Summary", "Detailed Summary", "Bullet Point Summary"],
            horizontal=True
        )
        
        if st.button("Generate Summary ✨"):
            with st.spinner("Analyzing document content..."):
                chunks = get_all_document_segments(selected_doc, DB_DIR, embeddings)
                if chunks:
                    full_text = "\n\n".join(chunks)[:100000]
                    
                    if summary_type == "Executive Summary":
                        prompt = f"Provide a high-level executive summary of the following document. Keep it concise, professional, and focus on the main objective:\n\n{full_text}"
                    elif summary_type == "Detailed Summary":
                        prompt = f"Provide a detailed section-by-section summary of the following document. Cover all key arguments, sections, and findings in detail:\n\n{full_text}"
                    else:
                        prompt = f"Extract the core key points from the following document and present them as a clean, bulleted list. Highlight the most crucial facts:\n\n{full_text}"
                        
                    try:
                        response = llm.invoke(prompt)
                        st.markdown(f"#### 📋 Generated {summary_type}")
                        st.info(response.content)
                    except Exception as e:
                        st.error(f"Error generating summary: {e}")
                else:
                    st.error("Could not retrieve document chunks from the vector store.")

with tabs[2]:
    st.markdown("### 🔍 Key Information Extraction")
    store = st.session_state["data_store"]
    doc_list = store["collections_meta"][selected_collection]["files"]
    if not doc_list:
        st.info("No documents uploaded yet in this collection. Upload files in the sidebar first.")
    else:
        selected_doc = st.selectbox("Select Document for Extraction", doc_list, key="extract_doc_select")
        
        if st.button("Extract Key Information 🔍"):
            with st.spinner("Extracting metadata and key entities..."):
                chunks = get_all_document_segments(selected_doc, DB_DIR, embeddings)
                if chunks:
                    full_text = "\n\n".join(chunks)[:100000]
                    prompt = f"""
                    Analyze the following document text and extract the key information.
                    Structure your response EXACTLY into these four sections, using the headings below:

                    ### 💻 Technologies & Tools
                    (List all frameworks, programming languages, software, databases, or technologies mentioned. If none, say "None detected".)

                    ### 🎯 Core Skills & Competencies
                    (List key professional skills, methodologies, or capabilities mentioned. If none, say "None detected".)

                    ### 📅 Key Dates & Milestones
                    (List important years, dates, timelines, or milestone descriptions. If none, say "None detected".)

                    ### 🏢 Key Entities (Organizations & Locations)
                    (List major companies, schools, institutes, cities, or locations. If none, say "None detected".)

                    Document Text:
                    {full_text}
                    """
                    try:
                        response = llm.invoke(prompt)
                        st.markdown(response.content)
                    except Exception as e:
                        st.error(f"Error extracting information: {e}")
                else:
                    st.error("Could not retrieve document chunks from the vector store.")

with tabs[3]:
    st.markdown("### 🧠 Educational Question Generator")
    store = st.session_state["data_store"]
    doc_list = store["collections_meta"][selected_collection]["files"]
    if not doc_list:
        st.info("No documents uploaded yet in this collection. Upload files in the sidebar first.")
    else:
        selected_doc = st.selectbox("Select Document to Generate Questions From", doc_list, key="qgen_doc_select")
        q_type = st.selectbox("Select Question Type", ["Multiple Choice Questions (MCQs)", "Quiz Questions", "Interview Questions"])
        q_num = st.slider("Number of Questions", min_value=3, max_value=10, value=5)
        
        if st.button("Generate Questions 🧠"):
            with st.spinner("Generating questions from content..."):
                chunks = get_all_document_segments(selected_doc, DB_DIR, embeddings)
                if chunks:
                    full_text = "\n\n".join(chunks)[:100000]
                    
                    if q_type == "Multiple Choice Questions (MCQs)":
                        prompt = f"Based on the following document content, generate {q_num} high-quality Multiple Choice Questions (MCQs). Each question must have 4 options (A, B, C, D) and specify the correct answer with a short explanation:\n\n{full_text}"
                    elif q_type == "Quiz Questions":
                        prompt = f"Based on the following document content, generate {q_num} short-answer quiz questions. Provide the correct answers below each question:\n\n{full_text}"
                    else:
                        prompt = f"Analyze the following document content and generate {q_num} typical technical or behavioral interview questions. Provide suggested high-quality answers that a candidate should give:\n\n{full_text}"
                        
                    try:
                        response = llm.invoke(prompt)
                        st.markdown(f"#### 💡 Generated {q_type}")
                        st.info(response.content)
                    except Exception as e:
                        st.error(f"Error generating questions: {e}")
                else:
                    st.error("Could not retrieve document chunks from the vector store.")

with tabs[4]:
    st.markdown("### 📑 Document Comparison Workspace")
    store = st.session_state["data_store"]
    doc_list = store["collections_meta"][selected_collection]["files"]
    if len(doc_list) < 2:
        st.info("Upload at least two documents in this collection to compare them.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            doc_a = st.selectbox("Select Document A", doc_list, index=0)
        with col2:
            doc_b = st.selectbox("Select Document B", doc_list, index=1 if len(doc_list) > 1 else 0)
            
        if doc_a == doc_b:
            st.warning("Please select two different documents to run a comparison.")
        else:
            if st.button("Compare Selected Documents 📑"):
                with st.spinner(f"Comparing '{doc_a}' with '{doc_b}'..."):
                    chunks_a = get_all_document_segments(doc_a, DB_DIR, embeddings)
                    chunks_b = get_all_document_segments(doc_b, DB_DIR, embeddings)
                    
                    if chunks_a and chunks_b:
                        text_a = "\n\n".join(chunks_a)[:50000]
                        text_b = "\n\n".join(chunks_b)[:50000]
                        
                        prompt = f"""
                        You are an expert analyst. Compare the following two documents.
                        Analyze their content, topics, and structure, and identify:
                        1. **Similarities**: What concepts, facts, skills, or data do they share?
                        2. **Differences**: What is unique to Document A vs Document B?
                        
                        ---
                        ### Document A: {doc_a}
                        {text_a}
                        
                        ---
                        ### Document B: {doc_b}
                        {text_b}
                        """
                        try:
                            response = llm.invoke(prompt)
                            st.markdown("### 🔍 Comparison Results")
                            st.info(response.content)
                        except Exception as e:
                            st.error(f"Error running document comparison: {e}")
                    else:
                        st.error("Could not load vector segments for one or both files.")

with tabs[5]:
    st.markdown("### 💡 AI Insights & Takeaways")
    store = st.session_state["data_store"]
    doc_list = store["collections_meta"][selected_collection]["files"]
    if not doc_list:
        st.info("No documents uploaded yet in this collection. Upload files in the sidebar first.")
    else:
        selected_doc = st.selectbox("Select Document for Strategic Insights", doc_list, key="insights_doc_select")
        
        if st.button("Generate AI Insights 💡"):
            with st.spinner("Extracting strategic insights..."):
                chunks = get_all_document_segments(selected_doc, DB_DIR, embeddings)
                if chunks:
                    full_text = "\n\n".join(chunks)[:100000]
                    prompt = f"""
                    Analyze the following document and output exactly three sections with the headings below:

                    ### 📌 Main Topics & Focus
                    (A high-level view of what this document centers around, listing the major themes.)

                    ### 🔑 Key Takeaways
                    (Identify the most critical takeaways or actionable knowledge points from this document.)

                    ### 🛠️ Recommended Actions
                    (Provide concrete, logical next steps or recommended actions based on the document's content.)

                    Document Content:
                    {full_text}
                    """
                    try:
                        response = llm.invoke(prompt)
                        st.markdown(response.content)
                    except Exception as e:
                        st.error(f"Error generating insights: {e}")
                else:
                    st.error("Could not retrieve document chunks from the vector store.")
