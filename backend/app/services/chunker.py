def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
):
    """
    Splitter tekst i overlappende chunks.
    """

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


if __name__ == "__main__":

    sample_text = """
    Dette er en testtekst.
    """ * 200

    chunks = chunk_text(sample_text)

    print(f"Antall chunks: {len(chunks)}")
    print()
    print(chunks[0])