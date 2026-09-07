import os
from typing import List, Dict, Any
from backend.rag.embeddings import LocalVectorIndex

class Retriever:
    def __init__(self, index_path: str = None):
        self.index = LocalVectorIndex(index_path=index_path)
        self.loaded = self.index.load_index()

    def retrieve(self, query: str, top_k: int = 6) -> List[Dict[str, Any]]:
        if not self.loaded:
            # Attempt reloading
            self.loaded = self.index.load_index()
            if not self.loaded:
                raise RuntimeError("Vector index could not be loaded. Please run 'python backend/scripts/build_index.py' first.")

        search_results = self.index.search(query, top_k=top_k)
        retrieved_passages = []
        
        for chunk, score in search_results:
            passage_item = {
                "document": chunk["document"],
                "section": chunk["section"],
                "title": chunk["title"],
                "passage": chunk["text"],
                "similarity": round(score, 4),
                "page": chunk.get("page"),
                "source_type": chunk.get("source_type", "markdown")
            }
            retrieved_passages.append(passage_item)

        return retrieved_passages
