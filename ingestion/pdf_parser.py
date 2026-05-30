import fitz


def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""

    try:
        document = fitz.open(pdf_path)

        for page in document:
            text += page.get_text() + "\n"

        document.close()

    except Exception as error:
        raise RuntimeError(f"Failed to extract text from PDF: {error}")

    return text.strip()