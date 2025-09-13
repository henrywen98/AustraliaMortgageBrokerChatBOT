"""CLI for ingesting PDF files into the Chroma knowledge base."""

import argparse
from utils.knowledge_base import KnowledgeBase


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest PDF into knowledge base")
    parser.add_argument("path", help="Path to PDF file")
    parser.add_argument("--source", help="Optional source name", default=None)
    args = parser.parse_args()

    kb = KnowledgeBase()
    added = kb.ingest_pdf(args.path, source=args.source)
    print(f"Ingested {added} chunks from {args.path}")


if __name__ == "__main__":
    main()
