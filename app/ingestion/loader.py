from pathlib import Path

from pypdf import PdfReader


def load_pdf(file_path: str) -> str:
    """
    Read a PDF file and return all extracted text.
    """

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    reader = PdfReader(str(pdf_path))

    pages_text = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages_text.append(text)

    return "\n\n".join(pages_text)