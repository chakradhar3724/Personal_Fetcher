from typing import List, Dict, Any
import requests


def search_semantic_scholar(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    url = "https://api.semanticscholar.org/graph/v1/paper/search"

    params = {
        "query": query,
        "limit": max_results,
        "fields": "title,authors,year,abstract,url,openAccessPdf,citationCount,venue,externalIds",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    papers = []

    for item in data.get("data", []):
        authors = [
            author.get("name", "")
            for author in item.get("authors", [])
            if author.get("name")
        ]

        open_access_pdf = item.get("openAccessPdf") or {}
        external_ids = item.get("externalIds") or {}

        papers.append(
            {
                "paper_id": item.get("paperId", ""),
                "title": item.get("title", "Untitled"),
                "authors": authors,
                "published": str(item.get("year", "")),
                "summary": item.get("abstract") or "Abstract not available",
                "pdf_url": open_access_pdf.get("url") or "",
                "entry_url": item.get("url") or "",
                "source": "Semantic Scholar",
                "venue": item.get("venue") or "",
                "doi": external_ids.get("DOI", ""),
                "citation_count": item.get("citationCount", 0),
            }
        )

    return papers