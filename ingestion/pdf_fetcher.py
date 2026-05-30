import os
import re
import json
import requests
from typing import Dict, Any, List

from config import SELECTED_PAPERS_DIR


def clean_filename(text: str, max_length: int = 120) -> str:
    text = text.strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "_", text)
    return text[:max_length]


def clean_topic_name(topic: str, max_length: int = 80) -> str:
    topic = topic.lower().strip()
    topic = re.sub(r"[^\w\s-]", "", topic)
    topic = re.sub(r"\s+", "_", topic)
    return topic[:max_length]


def get_topic_folder(topic: str) -> str:
    folder_name = clean_topic_name(topic)
    folder_path = os.path.join(SELECTED_PAPERS_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path


def is_valid_pdf(file_path: str) -> bool:
    if not os.path.exists(file_path):
        return False

    if os.path.getsize(file_path) < 1024:
        return False

    try:
        with open(file_path, "rb") as file:
            header = file.read(5)

        return header == b"%PDF-"

    except Exception:
        return False


def download_pdf(pdf_url: str, save_path: str) -> bool:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    response = requests.get(
        pdf_url,
        headers=headers,
        timeout=60,
        allow_redirects=True,
    )

    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").lower()
    content = response.content

    if len(content) < 1024:
        return False

    if not content.startswith(b"%PDF"):
        if "application/pdf" not in content_type:
            return False

    with open(save_path, "wb") as file:
        file.write(content)

    return is_valid_pdf(save_path)


def save_selected_paper(pdf_url: str, title: str, topic: str, index: int) -> str:
    topic_folder = get_topic_folder(topic)

    clean_title = clean_filename(title)
    filename = f"{index:02d}_{clean_title}.pdf"
    save_path = os.path.join(topic_folder, filename)

    if os.path.exists(save_path):
        if is_valid_pdf(save_path):
            return save_path
        os.remove(save_path)

    success = download_pdf(pdf_url, save_path)

    if not success:
        if os.path.exists(save_path):
            os.remove(save_path)

        raise RuntimeError(
            "Downloaded file is not a valid PDF. "
            "The URL may point to a webpage, blocked publisher page, or empty file."
        )

    return save_path


def save_metadata(topic: str, metadata: List[Dict[str, Any]]) -> str:
    topic_folder = get_topic_folder(topic)
    metadata_path = os.path.join(topic_folder, "metadata.json")

    with open(metadata_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4, ensure_ascii=False)

    return metadata_path