from typing import List, Dict, Any

class DocumentChunker:
    def __init__(self, target_chunk_words: int = 400, overlap_words: int = 50):
        self.target_chunk_words = target_chunk_words
        self.overlap_words = overlap_words

    def create_chunks(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        chunk_counter = 0
        
        for sec in sections:
            doc_name = sec["document"]
            sec_num = sec["section"]
            sec_title = sec["title"]
            text = sec["text"]
            page = sec.get("page")
            source_type = sec.get("source_type", "markdown")
            
            words = text.split()
            if len(words) <= self.target_chunk_words + self.overlap_words:
                chunk_counter += 1
                chunks.append({
                    "chunk_id": f"{doc_name}_{sec_num}_{chunk_counter}".replace(" ", "_"),
                    "document": doc_name,
                    "section": sec_num,
                    "title": sec_title,
                    "text": text,
                    "page": page,
                    "source_type": source_type,
                    "word_count": len(words)
                })
            else:
                # Split large sections into overlapping chunks
                step = self.target_chunk_words - self.overlap_words
                for i in range(0, len(words), step):
                    chunk_words = words[i:i + self.target_chunk_words]
                    if len(chunk_words) < 50 and i > 0:
                        continue # avoid tiny residual trailing chunks
                    chunk_text = " ".join(chunk_words)
                    chunk_counter += 1
                    chunks.append({
                        "chunk_id": f"{doc_name}_{sec_num}_{chunk_counter}".replace(" ", "_"),
                        "document": doc_name,
                        "section": sec_num,
                        "title": sec_title,
                        "text": chunk_text,
                        "page": page,
                        "source_type": source_type,
                        "word_count": len(chunk_words)
                    })

        return chunks
