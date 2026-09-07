import os
import json
import re
import math
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict

class LocalVectorIndex:
    def __init__(self, index_path: str = None):
        if index_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            index_path = os.path.join(base_dir, "data", "index.json")
        self.index_path = index_path
        self.chunks: List[Dict[str, Any]] = []
        self.vocab = {}
        self.idf = {}
        self.doc_vectors = []
        self.is_built = False
        self.use_sklearn = False

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            self.sklearn_vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words='english')
            self.sklearn_matrix = None
            self.use_sklearn = True
        except ImportError:
            self.use_sklearn = False

    def build_index(self, chunks: List[Dict[str, Any]]) -> None:
        self.chunks = chunks
        corpus_texts = [c["text"] for c in chunks]

        if self.use_sklearn:
            from sklearn.metrics.pairwise import cosine_similarity
            self.sklearn_matrix = self.sklearn_vectorizer.fit_transform(corpus_texts)
            index_data = {
                "engine": "sklearn",
                "vocabulary": self.sklearn_vectorizer.vocabulary_,
                "idf": self.sklearn_vectorizer.idf_.tolist(),
                "chunks": chunks
            }
        else:
            # Pure Python TF-IDF engine
            doc_count = len(corpus_texts)
            df = defaultdict(int)
            doc_tokens_list = [self._tokenize(txt) for txt in corpus_texts]

            for tokens in doc_tokens_list:
                for token in set(tokens):
                    df[token] += 1

            sorted_words = sorted(df.keys())
            self.vocab = {w: i for i, w in enumerate(sorted_words)}
            self.idf = {w: math.log((1.0 + doc_count) / (1.0 + df[w])) + 1.0 for w in sorted_words}
            self.doc_vectors = [self._vectorize(tokens) for tokens in doc_tokens_list]

            index_data = {
                "engine": "pure_python",
                "vocab": self.vocab,
                "idf": self.idf,
                "doc_vectors": self.doc_vectors,
                "chunks": chunks
            }

        self.is_built = True
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)

        print(f"Successfully built local vector index with {len(chunks)} chunks at {self.index_path}")

    def load_index(self) -> bool:
        if not os.path.exists(self.index_path):
            print(f"Warning: Index file not found at {self.index_path}")
            return False

        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.chunks = data["chunks"]

            if data.get("engine") == "sklearn" and self.use_sklearn:
                from sklearn.feature_extraction.text import TfidfVectorizer
                import numpy as np
                self.sklearn_vectorizer = TfidfVectorizer(
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                    stop_words='english',
                    vocabulary=data["vocabulary"]
                )
                self.sklearn_vectorizer.idf_ = np.array(data["idf"])
                corpus_texts = [c["text"] for c in self.chunks]
                self.sklearn_matrix = self.sklearn_vectorizer.transform(corpus_texts)
            else:
                # Use pure Python vectors
                self.use_sklearn = False
                if "vocab" in data:
                    self.vocab = data["vocab"]
                    self.idf = data["idf"]
                    self.doc_vectors = data["doc_vectors"]
                else:
                    # Recompute pure python index
                    corpus_texts = [c["text"] for c in self.chunks]
                    doc_count = len(corpus_texts)
                    df = defaultdict(int)
                    doc_tokens_list = [self._tokenize(txt) for txt in corpus_texts]
                    for tokens in doc_tokens_list:
                        for token in set(tokens):
                            df[token] += 1
                    sorted_words = sorted(df.keys())
                    self.vocab = {w: i for i, w in enumerate(sorted_words)}
                    self.idf = {w: math.log((1.0 + doc_count) / (1.0 + df[w])) + 1.0 for w in sorted_words}
                    self.doc_vectors = [self._vectorize(tokens) for tokens in doc_tokens_list]

            self.is_built = True
            return True
        except Exception as e:
            print(f"Error loading index from {self.index_path}: {e}")
            return False

    def search(self, query: str, top_k: int = 6) -> List[Tuple[Dict[str, Any], float]]:
        if not self.is_built:
            raise ValueError("Vector index is not built or loaded.")

        if self.use_sklearn and self.sklearn_matrix is not None:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            query_vec = self.sklearn_vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.sklearn_matrix)[0]
            top_indices = np.argsort(similarities)[::-1][:top_k]
            return [(self.chunks[idx], float(similarities[idx])) for idx in top_indices]
        else:
            q_tokens = self._tokenize(query)
            q_vec = self._vectorize(q_tokens)
            scores = []
            for idx, doc_vec in enumerate(self.doc_vectors):
                sim = self._cosine_similarity(q_vec, doc_vec)
                scores.append((idx, sim))
            
            scores.sort(key=lambda x: x[1], reverse=True)
            return [(self.chunks[idx], score) for idx, score in scores[:top_k]]

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'\b\w+\b', text.lower())
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        return words + bigrams

    def _vectorize(self, tokens: List[str]) -> Dict[str, float]:
        counts = Counter(tokens)
        vec = {}
        for token, count in counts.items():
            if token in self.vocab:
                tf = 1.0 + math.log(count)
                vec[token] = tf * self.idf[token]
        return vec

    def _cosine_similarity(self, q_vec: Dict[str, float], d_vec: Dict[str, float]) -> float:
        dot = sum(val * d_vec.get(term, 0.0) for term, val in q_vec.items())
        norm_q = math.sqrt(sum(val * val for val in q_vec.values()))
        norm_d = math.sqrt(sum(val * val for val in d_vec.values()))
        if norm_q == 0.0 or norm_d == 0.0:
            return 0.0
        return dot / (norm_q * norm_d)
