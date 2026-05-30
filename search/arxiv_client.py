from typing import List, Dict, Any
import arxiv


REQUIRED_TERMS = [
    "blind people",
    "blind person",
    "visually impaired",
    "visual impairment",
    "low vision",
    "assistive",
    "accessibility",
]


EXCLUDE_TERMS = [
    "blind equalization",
    "blind sparse",
    "blind channel",
    "blind source separation",
    "blind deconvolution",
    "blind estimation",
    "underwater navigation",
    "ancient mediterranean",
]


def is_relevant_paper(title: str, summary: str) -> bool:
    text = f"{title} {summary}".lower()

    if any(term in text for term in EXCLUDE_TERMS):
        return False

    return any(term in text for term in REQUIRED_TERMS)


def search_arxiv(query: str, max_results: int = 10, apply_filter: bool = True) -> List[Dict[str, Any]]:
    client = arxiv.Client()

    search = arxiv.Search(
        query=query,
        max_results=max_results * 3,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    papers = []

    for result in client.results(search):
        title = result.title.strip().replace("\n", " ")
        summary = result.summary.strip().replace("\n", " ")

        if apply_filter and not is_relevant_paper(title, summary):
            continue

        paper_id = result.entry_id.split("/")[-1]

        papers.append(
            {
                "paper_id": paper_id,
                "title": title,
                "authors": [author.name for author in result.authors],
                "published": result.published.strftime("%Y-%m-%d"),
                "summary": summary,
                "pdf_url": result.pdf_url,
                "entry_url": result.entry_id,
                "source": "arXiv",
                "venue": "arXiv",
                "doi": result.doi or "",
                "citation_count": 0,
            }
        )

        if len(papers) >= max_results:
            break

    return papers