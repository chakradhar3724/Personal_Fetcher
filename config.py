import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
CHROMA_DB_DIR = os.path.join(DATA_DIR, "chroma_db")
SELECTED_PAPERS_DIR = os.path.join(DATA_DIR, "selected_papers")

DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "research_agent.db")

OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
LITERATURE_REVIEW_CSV = os.path.join(OUTPUTS_DIR, "literature_review.csv")
REPORT_MD = os.path.join(OUTPUTS_DIR, "report.md")

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
MAX_PAPERS = int(os.getenv("MAX_PAPERS", "10"))

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_DIR, exist_ok=True)
os.makedirs(SELECTED_PAPERS_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)