from typing import List, Dict, Any
import pandas as pd


def create_literature_review_table(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    table_rows = []

    for row in rows:
        table_rows.append(
            {
                "Title": row.get("title", ""),
                "Authors": row.get("authors", ""),
                "Published": row.get("published", ""),
                "Source": row.get("source", ""),
                "Venue": row.get("venue", ""),
                "Citations": row.get("citation_count", ""),
                "Problem": row.get("problem", ""),
                "Method": row.get("method", ""),
                "Dataset": row.get("dataset", ""),
                "Model": row.get("model", ""),
                "Evaluation": row.get("evaluation", ""),
                "Limitations": row.get("limitations", ""),
                "Contribution": row.get("contribution", ""),
                "DOI": row.get("doi", ""),
                "PDF URL": row.get("pdf_url", ""),
                "Local PDF": row.get("local_pdf_path", ""),
            }
        )

    return pd.DataFrame(table_rows)