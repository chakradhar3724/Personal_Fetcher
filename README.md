# Personal Research Assistant Agent

This project searches academic papers online, lets the user select papers for a literature survey, stores selected papers locally, extracts structured information, and generates a literature review table and report.

## Features

- Search papers from arXiv
- Select papers for literature survey
- Download selected PDFs locally
- Store selected papers by research topic
- Extract paper text using PyMuPDF
- Store chunks in ChromaDB
- Use Ollama local LLM for extraction and report generation
- Generate literature review CSV
- Generate Markdown report

## Folder for selected papers

Selected literature survey papers are stored in:

```text
data/selected_papers/<research_topic>/