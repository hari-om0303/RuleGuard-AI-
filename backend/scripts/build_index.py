import os
import sys

# Ensure backend parent path is in Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.scripts.generate_pdf import generate_pdf
from backend.rag.loader import DocumentLoader
from backend.rag.chunker import DocumentChunker
from backend.rag.embeddings import LocalVectorIndex

def main():
    print("=" * 60)
    print("      RuleGuard AI — Building Local Vector Index")
    print("=" * 60)

    # 1. Generate PDF file
    print("[1/5] Ensuring PDF document is generated...")
    generate_pdf()

    # 2. Load documents
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    print(f"[2/5] Loading documents from: {data_dir}")
    loader = DocumentLoader(data_dir=data_dir)
    raw_sections = loader.load_all_documents()

    # Calculate total word count
    total_words = sum(len(sec["text"].split()) for sec in raw_sections)
    print(f" -> Successfully loaded {len(raw_sections)} sections.")
    print(f" -> Total Corpus Word Count: {total_words:,} words.")

    if total_words < 6000:
        print(f"WARNING: Corpus word count ({total_words}) is below the required 6,000 words limit!")
    else:
        print(f" -> Corpus size check PASSED (>= 6,000 words requirement met).")

    # 3. Chunk sections
    print("[3/5] Chunking sections into metadata-aware chunks...")
    chunker = DocumentChunker(target_chunk_words=350, overlap_words=40)
    chunks = chunker.create_chunks(raw_sections)
    print(f" -> Generated {len(chunks)} chunks.")

    # 4. Build & save vector index
    print("[4/5] Computing embeddings & building TF-IDF cosine vector index...")
    index_path = os.path.join(data_dir, "index.json")
    vector_index = LocalVectorIndex(index_path=index_path)
    vector_index.build_index(chunks)

    print("[5/5] Index building complete! Ready for query evaluation.")
    print("=" * 60)

if __name__ == "__main__":
    main()
