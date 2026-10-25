from pathlib import Path

import pymupdf
from django.core.management.base import BaseCommand
from sentence_transformers import SentenceTransformer

from rag.chunking import split_into_chunks
from rag.models import DocumentChunk


class Command(BaseCommand):
    help = "Read .txt and .pdf files from data/sources, chunk them, embed them and store in pgvector."

    def handle(self, *args, **options):
        folder = Path("data/sources")
        files = sorted(folder.glob("*.txt")) + sorted(folder.glob("*.pdf"))
        if not files:
            self.stderr.write("No .txt or .pdf files found in data/sources")
            return

        model = SentenceTransformer("all-MiniLM-L6-v2")

        for path in files:
            if path.suffix == ".txt":
                pages = [(1, path.read_text(encoding="utf-8"))]
            else:
                doc = pymupdf.open(str(path))
                pages = [(n, p.get_text() or "") for n, p in enumerate(doc, start=1)]

            rows = []
            for page_no, text in pages:
                for index, chunk in enumerate(split_into_chunks(text)):
                    rows.append((page_no, index, chunk))

            if not rows:
                self.stderr.write(f"No text found in {path.name}")
                continue

            DocumentChunk.objects.filter(source=path.name).delete()

            embeddings = model.encode(
                [r[2] for r in rows],
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            DocumentChunk.objects.bulk_create(
                [
                    DocumentChunk(
                        source=path.name,
                        page=page_no,
                        chunk_index=index,
                        text=chunk,
                        embedding=emb.tolist(),
                    )
                    for (page_no, index, chunk), emb in zip(rows, embeddings)
                ]
            )
            self.stdout.write(f"{path.name}: {len(rows)} chunks stored")