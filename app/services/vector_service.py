import chromadb
from sentence_transformers import SentenceTransformer


class VectorService:

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path="chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="aec_documents"
        )

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def store_chunks(self,chunks: list[dict],filename: str) -> int:

        # Extract only the text for embedding
        documents = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = self.embedding_model.encode(
            documents
        ).tolist()

        ids = [
            f"{filename}_{index}"
            for index in range(len(chunks))
        ]

        metadatas = [
            {
                "filename": filename,
                "page": chunk["page"],
                "chunk_index": index
            }
            for index, chunk in enumerate(chunks)
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return len(chunks)

    def search(self,question: str,top_k: int = 5):

     # Convert the user's question into an embedding
     question_embedding = self.embedding_model.encode([question]).tolist()

     # Search ChromaDB for the most similar chunks
     results = self.collection.query(query_embeddings=question_embedding,n_results=top_k)

     return results