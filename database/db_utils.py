import sqlite3
import json
from typing import Dict, List, Any

from config import DATABASE_PATH


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def add_column_if_missing(cursor, table_name: str, column_name: str, column_type: str):
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if column_name not in existing_columns:
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS papers (
            paper_id TEXT PRIMARY KEY,
            title TEXT,
            authors TEXT,
            published TEXT,
            summary TEXT,
            pdf_url TEXT,
            entry_url TEXT,
            local_pdf_path TEXT,
            topic TEXT
        )
        """
    )

    add_column_if_missing(cursor, "papers", "source", "TEXT")
    add_column_if_missing(cursor, "papers", "venue", "TEXT")
    add_column_if_missing(cursor, "papers", "doi", "TEXT")
    add_column_if_missing(cursor, "papers", "citation_count", "INTEGER DEFAULT 0")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS extractions (
            paper_id TEXT PRIMARY KEY,
            problem TEXT,
            method TEXT,
            dataset TEXT,
            model TEXT,
            evaluation TEXT,
            limitations TEXT,
            contribution TEXT,
            raw_json TEXT,
            FOREIGN KEY (paper_id) REFERENCES papers(paper_id)
        )
        """
    )

    conn.commit()
    conn.close()


def save_paper(paper: Dict[str, Any], topic: str, local_pdf_path: str = ""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO papers (
            paper_id, title, authors, published, summary,
            pdf_url, entry_url, local_pdf_path, topic,
            source, venue, doi, citation_count
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            paper.get("paper_id", ""),
            paper.get("title", ""),
            json.dumps(paper.get("authors", [])),
            paper.get("published", ""),
            paper.get("summary", ""),
            paper.get("pdf_url", ""),
            paper.get("entry_url", ""),
            local_pdf_path,
            topic,
            paper.get("source", ""),
            paper.get("venue", ""),
            paper.get("doi", ""),
            int(paper.get("citation_count", 0) or 0),
        ),
    )

    conn.commit()
    conn.close()


def save_extraction(paper_id: str, extraction: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO extractions (
            paper_id, problem, method, dataset, model,
            evaluation, limitations, contribution, raw_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            paper_id,
            extraction.get("problem", ""),
            extraction.get("method", ""),
            extraction.get("dataset", ""),
            extraction.get("model", ""),
            extraction.get("evaluation", ""),
            extraction.get("limitations", ""),
            extraction.get("contribution", ""),
            json.dumps(extraction, ensure_ascii=False),
        ),
    )

    conn.commit()
    conn.close()


def get_literature_rows(topic: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            p.paper_id,
            p.title,
            p.authors,
            p.published,
            p.pdf_url,
            p.local_pdf_path,
            p.source,
            p.venue,
            p.doi,
            p.citation_count,
            e.problem,
            e.method,
            e.dataset,
            e.model,
            e.evaluation,
            e.limitations,
            e.contribution
        FROM papers p
        LEFT JOIN extractions e ON p.paper_id = e.paper_id
        WHERE p.topic = ?
        """,
        (topic,),
    )

    rows = cursor.fetchall()
    conn.close()

    result = []

    for row in rows:
        result.append(
            {
                "paper_id": row[0],
                "title": row[1],
                "authors": ", ".join(json.loads(row[2])) if row[2] else "",
                "published": row[3],
                "pdf_url": row[4],
                "local_pdf_path": row[5],
                "source": row[6],
                "venue": row[7],
                "doi": row[8],
                "citation_count": row[9],
                "problem": row[10],
                "method": row[11],
                "dataset": row[12],
                "model": row[13],
                "evaluation": row[14],
                "limitations": row[15],
                "contribution": row[16],
            }
        )

    return result