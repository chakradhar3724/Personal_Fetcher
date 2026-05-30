import os
import streamlit as st

from config import (
    MAX_PAPERS,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    LITERATURE_REVIEW_CSV,
    REPORT_MD,
)

from database.db_utils import (
    init_db,
    save_paper,
    save_extraction,
    get_literature_rows,
)

from search.multi_source_search import search_all_sources

from ingestion.pdf_fetcher import (
    save_selected_paper,
    save_metadata,
    clean_topic_name,
)

from ingestion.pdf_parser import extract_text_from_pdf
from ingestion.chunker import chunk_text

from rag.vector_store import VectorStore

from agents.extraction_agent import extract_paper_details
from agents.comparison_agent import create_literature_review_table
from agents.report_agent import generate_literature_report


st.set_page_config(
    page_title="Personal Research Assistant Agent",
    layout="wide",
)

init_db()


st.title("Personal Research Assistant Agent")
st.write(
    "Search papers online, select useful ones, store them locally, "
    "and generate a literature survey."
)


with st.sidebar:
    st.header("Settings")

    max_results = st.number_input(
        "Number of papers to search",
        min_value=1,
        max_value=50,
        value=MAX_PAPERS,
    )

    process_pdfs = st.checkbox(
        "Download and read PDFs when available",
        value=True,
    )

    use_vector_store = st.checkbox(
        "Store paper chunks in ChromaDB",
        value=True,
    )

    st.divider()

    st.caption("Search sources:")
    st.write("arXiv + OpenAlex + Semantic Scholar")


query = st.text_input(
    "Enter your research topic",
    placeholder="Example: assistive navigation visually impaired people",
)


if "papers" not in st.session_state:
    st.session_state.papers = []

if "selected_indices" not in st.session_state:
    st.session_state.selected_indices = []

if "search_topic" not in st.session_state:
    st.session_state.search_topic = ""


if st.button("Search Papers"):
    if not query.strip():
        st.warning("Please enter a research topic.")
    else:
        with st.spinner("Searching papers from multiple sources..."):
            papers = search_all_sources(
                query=query.strip(),
                max_results=max_results,
            )

            st.session_state.papers = papers
            st.session_state.selected_indices = []
            st.session_state.search_topic = query.strip()

        st.success(f"Found {len(st.session_state.papers)} papers.")


if st.session_state.papers:
    st.subheader("Search Results")

    if st.session_state.search_topic:
        st.caption(f"Current search topic: {st.session_state.search_topic}")

    selected_indices = []

    for index, paper in enumerate(st.session_state.papers):
        title = paper.get("title", "Untitled")
        authors = paper.get("authors", [])
        published = paper.get("published", "")
        source = paper.get("source", "")
        venue = paper.get("venue", "")
        citation_count = paper.get("citation_count", 0)
        pdf_url = paper.get("pdf_url", "")
        entry_url = paper.get("entry_url", "")
        summary = paper.get("summary", "Abstract not available")
        paper_id = paper.get("paper_id", f"paper_{index}")

        with st.expander(f"{index + 1}. {title}"):
            st.write(
                f"**Authors:** {', '.join(authors) if authors else 'Not available'}"
            )
            st.write(f"**Published:** {published if published else 'Not available'}")
            st.write(f"**Source:** {source if source else 'Not available'}")
            st.write(f"**Venue:** {venue if venue else 'Not available'}")
            st.write(f"**Citations:** {citation_count}")

            if pdf_url:
                st.write(f"**PDF:** {pdf_url}")
            else:
                st.write("**PDF:** Not available")

            if entry_url:
                st.write(f"**Paper Link:** {entry_url}")

            st.write("**Abstract / Summary:**")
            st.write(summary)

            selected = st.checkbox(
                "Use this paper for literature survey",
                key=f"select_{index}_{paper_id}",
            )

            if selected:
                selected_indices.append(index)

    st.session_state.selected_indices = selected_indices


if st.session_state.selected_indices:
    st.info(f"{len(st.session_state.selected_indices)} papers selected.")


if st.button("Generate Literature Survey"):
    if not st.session_state.search_topic:
        st.warning("Please search for papers first.")

    elif not st.session_state.selected_indices:
        st.warning("Please select at least one paper.")

    else:
        topic = st.session_state.search_topic

        selected_papers = [
            st.session_state.papers[i]
            for i in st.session_state.selected_indices
        ]

        vector_store = VectorStore() if use_vector_store else None
        metadata_records = []

        progress = st.progress(0)

        for count, paper in enumerate(selected_papers, start=1):
            title = paper.get("title", "Untitled")
            paper_id = paper.get("paper_id", f"paper_{count}")
            pdf_url = paper.get("pdf_url", "")
            summary = paper.get("summary", "")

            st.write(f"Processing: **{title}**")

            local_pdf_path = ""

            try:
                if process_pdfs and pdf_url:
                    local_pdf_path = save_selected_paper(
                        pdf_url=pdf_url,
                        title=title,
                        topic=topic,
                        index=count,
                    )

                    paper_text = extract_text_from_pdf(local_pdf_path)

                    if not paper_text.strip():
                        paper_text = summary

                else:
                    paper_text = summary

            except Exception as error:
                st.warning(
                    f"PDF processing failed for '{title}'. "
                    f"Using abstract instead. Error: {error}"
                )
                paper_text = summary

            save_paper(
                paper=paper,
                topic=topic,
                local_pdf_path=local_pdf_path,
            )

            with st.spinner(f"Extracting structured details from: {title}"):
                extraction = extract_paper_details(
                    title=title,
                    abstract=summary,
                    paper_text=paper_text,
                )

            save_extraction(
                paper_id=paper_id,
                extraction=extraction,
            )

            if use_vector_store and vector_store is not None:
                chunks = chunk_text(
                    text=paper_text,
                    chunk_size=CHUNK_SIZE,
                    overlap=CHUNK_OVERLAP,
                )

                vector_store.add_chunks(
                    paper_id=paper_id,
                    title=title,
                    chunks=chunks,
                    metadata={
                        "published": paper.get("published", ""),
                        "pdf_url": pdf_url,
                        "topic": topic,
                        "source": paper.get("source", ""),
                        "venue": paper.get("venue", ""),
                        "doi": paper.get("doi", ""),
                    },
                )

            metadata_records.append(
                {
                    "index": count,
                    "paper_id": paper_id,
                    "title": title,
                    "authors": paper.get("authors", []),
                    "published": paper.get("published", ""),
                    "pdf_url": pdf_url,
                    "entry_url": paper.get("entry_url", ""),
                    "source": paper.get("source", ""),
                    "venue": paper.get("venue", ""),
                    "doi": paper.get("doi", ""),
                    "citation_count": paper.get("citation_count", 0),
                    "local_pdf_path": local_pdf_path,
                }
            )

            progress.progress(count / len(selected_papers))

        metadata_path = save_metadata(topic, metadata_records)

        rows = get_literature_rows(topic)
        literature_df = create_literature_review_table(rows)

        literature_df.to_csv(LITERATURE_REVIEW_CSV, index=False)

        with st.spinner("Generating final literature survey report..."):
            report = generate_literature_report(
                topic=topic,
                rows=rows,
            )

        with open(REPORT_MD, "w", encoding="utf-8") as file:
            file.write(report)

        st.success("Literature survey generated successfully.")

        st.subheader("Literature Review Table")
        st.dataframe(literature_df, use_container_width=True)

        st.download_button(
            label="Download Literature Review CSV",
            data=literature_df.to_csv(index=False),
            file_name="literature_review.csv",
            mime="text/csv",
        )

        st.subheader("Generated Report")
        st.markdown(report)

        st.download_button(
            label="Download Report",
            data=report,
            file_name="report.md",
            mime="text/markdown",
        )

        topic_folder = os.path.join(
            "data",
            "selected_papers",
            clean_topic_name(topic),
        )

        st.info(f"Selected papers saved in: `{topic_folder}`")
        st.info(f"Metadata saved at: `{metadata_path}`")