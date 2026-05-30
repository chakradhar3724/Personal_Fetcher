from typing import List, Dict, Any
import requests


def search_openalex(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    url = "https://api.openalex.org/works"

    params = {
        "search": query,
        "per-page": max_results,
        "sort": "relevance_score:desc",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    papers = []

    for item in data.get("results", []):
        title = item.get("title") or "Untitled"

        authors = []
        for authorship in item.get("authorships", []):
            author = authorship.get("author", {})
            if author.get("display_name"):
                authors.append(author["display_name"])

        abstract = reconstruct_openalex_abstract(
            item.get("abstract_inverted_index")
        )

        pdf_url = ""

        open_access = item.get("open_access") or {}
        if open_access.get("oa_url"):
            pdf_url = open_access.get("oa_url")

        primary_location = item.get("primary_location") or {}
        source = primary_location.get("source") or {}

        papers.append(
            {
                "paper_id": item.get("id", "").split("/")[-1],
                "title": title,
                "authors": authors,
                "published": str(item.get("publication_year", "")),
                "summary": abstract or "Abstract not available",
                "pdf_url": pdf_url,
                "entry_url": item.get("doi") or item.get("id", ""),
                "source": "OpenAlex",
                "venue": source.get("display_name", ""),
                "doi": item.get("doi") or "",
                "citation_count": item.get("cited_by_count", 0),
            }
        )

    return papers


def reconstruct_openalex_abstract(inverted_index):
    if not inverted_index:
        return ""

    word_positions = []

    for word, positions in inverted_index.items():
        for position in positions:
            word_positions.append((position, word))

    word_positions.sort(key=lambda x: x[0])

    return " ".join(word for _, word in word_positions)