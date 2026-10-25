def split_into_chunks(text, chunk_words=180, overlap_words=40, min_words=30):
    words = text.split()
    step = chunk_words - overlap_words
    chunks = []
    for start in range(0, len(words), step):
        piece = words[start:start + chunk_words]
        if len(piece) >= min_words:
            chunks.append(" ".join(piece))
    return chunks