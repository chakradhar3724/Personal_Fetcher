from typing import List, Dict, Any

from search.arxiv_client import search_arxiv
from search.openalex_client import search_openalex
from search.semantic_scholar_client import search_semantic_scholar


def normalize_title(title: str) -> str:
    return " ".join(title.lower().strip().split())


def merge_and_deduplicate(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_titles = set()
    seen_dois = set()
    unique_papers = []

    for paper in results:
        title_key = normalize_title(paper.get("title", ""))
        doi_key = paper.get("doi", "").lower().strip()

        if doi_key and doi_key in seen_dois:
            continue

        if title_key and title_key in seen_titles:
            continue

        if doi_key:
            seen_dois.add(doi_key)

        if title_key:
            seen_titles.add(title_key)

        unique_papers.append(paper)

    return unique_papers


def score_paper(paper: Dict[str, Any], query: str) -> int:
    score = 0

    title = paper.get("title", "").lower()
    summary = paper.get("summary", "").lower()
    source = paper.get("source", "")
    pdf_url = paper.get("pdf_url", "")
    citation_count = paper.get("citation_count", 0) or 0

    query_terms = query.lower().split()

    for term in query_terms:
        if term in title:
            score += 4
        if term in summary:
            score += 1

    if pdf_url:
        score += 3

    if source == "Semantic Scholar":
        score += 2

    if source == "OpenAlex":
        score += 2

    if source == "arXiv":
        score += 1

    if citation_count >= 100:
        score += 4
    elif citation_count >= 50:
        score += 3
    elif citation_count >= 10:
        score += 2
    elif citation_count > 0:
        score += 1

    return score


def search_all_sources(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    all_results = []

    source_functions = [
        ("arXiv", search_arxiv),
        ("OpenAlex", search_openalex),
        ("Semantic Scholar", search_semantic_scholar),
    ]

    for source_name, search_function in source_functions:
        try:
            if source_name == "arXiv":
                results = search_function(query, max_results=max_results, apply_filter=False)
            else:
                results = search_function(query, max_results=max_results)

            all_results.extend(results)

        except Exception as error:
            print(f"{source_name} search failed: {error}")

    unique_results = merge_and_deduplicate(all_results)

    unique_results.sort(
        key=lambda paper: score_paper(paper, query),
        reverse=True,
    )

    return unique_results[:max_results]