def split_text_into_chunks(text: str, chunk_size: int = 800):
    """
    Simple chunker for PDF text
    """

    words = text.split()
    chunks = []

    current_chunk = []

    for word in words:
        current_chunk.append(word)

        if len(current_chunk) >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks