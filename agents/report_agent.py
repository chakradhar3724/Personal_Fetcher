from typing import List, Dict, Any

from llm.ollama_client import generate_response


def generate_literature_report(topic: str, rows: List[Dict[str, Any]]) -> str:
    paper_summaries = ""

    for index, row in enumerate(rows, start=1):
        paper_summaries += f"""
Paper {index}
Title: {row.get("title", "")}
Authors: {row.get("authors", "")}
Published: {row.get("published", "")}
Problem: {row.get("problem", "")}
Method: {row.get("method", "")}
Dataset: {row.get("dataset", "")}
Model: {row.get("model", "")}
Evaluation: {row.get("evaluation", "")}
Limitations: {row.get("limitations", "")}
Contribution: {row.get("contribution", "")}
"""

    prompt = f"""
You are an academic research assistant.

Write a literature survey report for the topic:

{topic}

Use only the paper information given below.

Report structure:
1. Title
2. Introduction
3. Summary of Selected Papers
4. Method Comparison
5. Datasets and Evaluation Comparison
6. Common Limitations
7. Research Gaps
8. Conclusion

Do not invent papers, datasets, metrics, or claims.

Paper Information:
{paper_summaries}
"""

    return generate_response(prompt)