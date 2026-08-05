"""One-time (well, re-runnable) ingestion of the owner's manual PDFs into
manual_chunks for RAG. Per the Phase 4.5 addendum's §5.6 note, this is
scoped to a single vehicle_id per run - re-run per vehicle if a second
car's manuals are ever added, rather than being a single fixed script
against one hardcoded PDF.

Chunking never crosses a page boundary, on purpose: a chunk that spans two
pages would need a page *range* citation ("pages 103-105") instead of an
exact page number, and search_manual's whole point is a precise citation
the user can actually go check. Short pages just become one (small) chunk;
long pages get split into ~500-word pieces with a 75-word overlap so a
sentence that happens to fall on a chunk boundary still shows up whole in
at least one chunk.

Usage: python ingest_manuals.py --vehicle-id 2
"""

import argparse
from pathlib import Path

import pdfplumber

from database import SessionLocal
from embeddings import embed_text
from models import ManualChunk, Vehicle

MANUALS_DIR = Path(__file__).resolve().parent.parent / "manuals"

# 2A1313OM.pdf (the old Honda manual) is deliberately excluded - see
# CLAUDE.md, it's stale leftover from before the Lexus switch.
SOURCE_FILES = ["OM33566U.pdf", "SMG202.pdf"]

CHUNK_WORDS = 500
OVERLAP_WORDS = 75


def chunk_page_text(text: str) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + CHUNK_WORDS
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - OVERLAP_WORDS
    return chunks


def extract_chunks(pdf_path: Path):
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text or not text.strip():
                continue
            for chunk_text in chunk_page_text(text):
                yield page_number, chunk_text


def main(vehicle_id: int):
    db = SessionLocal()
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if vehicle is None:
            raise SystemExit(f"No vehicle with id {vehicle_id}")

        deleted = db.query(ManualChunk).filter(ManualChunk.vehicle_id == vehicle_id).delete()
        db.commit()
        print(f"Cleared {deleted} existing chunk(s) for vehicle {vehicle_id} ({vehicle.year} {vehicle.make} {vehicle.model})")

        total = 0
        for source_file in SOURCE_FILES:
            pdf_path = MANUALS_DIR / source_file
            if not pdf_path.exists():
                raise SystemExit(f"Missing PDF: {pdf_path}")

            file_count = 0
            for page_number, chunk_text in extract_chunks(pdf_path):
                embedding = embed_text(chunk_text)
                db.add(
                    ManualChunk(
                        vehicle_id=vehicle_id,
                        source_file=source_file,
                        page_number=page_number,
                        chunk_text=chunk_text,
                        embedding=embedding,
                    )
                )
                file_count += 1
                if file_count % 25 == 0:
                    print(f"  {source_file}: {file_count} chunks embedded so far...")

            db.commit()
            total += file_count
            print(f"{source_file}: {file_count} chunks ingested")

        print(f"Done. {total} total chunks for vehicle {vehicle_id}.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vehicle-id", type=int, required=True)
    args = parser.parse_args()
    main(args.vehicle_id)
