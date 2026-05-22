import fitz  # pymupdf


def extract_text_from_pdf(file_path: str) -> str:
    """
    Leser PDF og returnerer all tekst.
    """

    doc = fitz.open(file_path)

    full_text = []

    for page in doc:
        text = page.get_text()

        if text:
            full_text.append(text)

    doc.close()

    return "\n".join(full_text)


if __name__ == "__main__":
    text = extract_text_from_pdf("data/test.pdf")

    print(text[:2000])