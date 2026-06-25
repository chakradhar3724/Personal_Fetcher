# Personal Research Assistant Agent

A local AI-powered research assistant that searches academic papers online, lets users select relevant papers, stores selected papers locally, extracts structured information, and generates a literature review table and report.

This project is designed for academic literature survey workflows where a user wants to search papers, compare methods, and organize selected papers by topic.

---

## Features

- Search academic papers from multiple sources:
  - arXiv
  - OpenAlex
  - Semantic Scholar
- Display paper metadata:
  - title
  - authors
  - publication year
  - source
  - venue
  - citation count
  - abstract
  - PDF link when available
- Select only relevant papers for the literature survey
- Download selected PDFs locally when valid PDFs are available
- Fall back to abstracts when PDFs are unavailable or invalid
- Extract structured details from each paper:
  - problem
  - method
  - dataset
  - model
  - evaluation
  - limitations
  - contribution
- Store extracted information in SQLite
- Store paper chunks in ChromaDB for retrieval
- Use Ollama local LLM for extraction and report generation
- Generate:
  - literature review table
  - Markdown literature survey report
  - CSV export

---

## Tech Stack

- Python
- Streamlit
- SQLite
- ChromaDB
- Sentence Transformers
- Ollama
- PyMuPDF
- arXiv API
- OpenAlex API
- Semantic Scholar API

---

## Project Structure

```text
Personal_Fetcher/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── agents/
│   ├── extraction_agent.py
│   ├── comparison_agent.py
│   └── report_agent.py
│
├── database/
│   └── db_utils.py
│
├── ingestion/
│   ├── pdf_fetcher.py
│   ├── pdf_parser.py
│   └── chunker.py
│
├── llm/
│   └── ollama_client.py
│
├── prompts/
│   ├── extraction_prompt.txt
│   ├── comparison_prompt.txt
│   └── report_prompt.txt
│
├── rag/
│   ├── embeddings.py
│   └── vector_store.py
│
├── search/
│   ├── arxiv_client.py
│   ├── openalex_client.py
│   ├── semantic_scholar_client.py
│   └── multi_source_search.py
│
├── data/
│   ├── cache/
│   ├── chroma_db/
│   └── selected_papers/
│
└── outputs/


---

## Author

**Chakradhar Peddavenkatagari**  

Aspiring AI Engineer

Masters in Computer Science

The State University of New York at Buffalo 
