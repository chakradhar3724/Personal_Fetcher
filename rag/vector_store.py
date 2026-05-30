from typing import List, Dict, Any
import chromadb

from config import CHROMA_DB_DIR
from rag.embeddings import EmbeddingModel


class VectorStore:
    def __init__(self, collection_name: str = "research_papers"):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedding_model = EmbeddingModel()

    def add_chunks(
        self,
        paper_id: str,
        title: str,
        chunks: List[str],
        metadata: Dict[str, Any],
    ):
        if not chunks:
            return

        embeddings = self.embedding_model.embed_texts(chunks)

        ids = [f"{paper_id}_chunk_{i}" for i in range(len(chunks))]

        metadatas = []

        for i, _ in enumerate(chunks):
            item = {
                "paper_id": paper_id,
                "title": title,
                "chunk_index": i,
            }
            item.update(metadata)
            metadatas.append(item)

        self.collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(self, query_text: str, n_results: int = 5):
        query_embedding = self.embedding_model.embed_query(query_text)

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )