import os

class VectorStore:
    def __init__(self):
        self.host = os.getenv("CHROMA_HOST", "localhost")
        self.port = int(os.getenv("CHROMA_PORT", "8001"))
        self.available = False
        self._fallback_docs = []
        
        try:
            from chromadb import HttpClient
            self.client = HttpClient(host=self.host, port=self.port)
            self.collection = self.client.get_or_create_collection("eduleap_knowledge")
            self.available = True
        except Exception:
            pass  # Silently fail, fallback mode
    
    def add_documents(self, documents: list, ids: list, metadatas: list = None):
        if not self.available:
            self._fallback_docs.extend(zip(ids, documents, metadatas or []))
            return
        self.collection.add(documents=documents, ids=ids, metadatas=metadatas)
    
    def query(self, query_text: str, n_results: int = 3, filter_dict: dict = None):
        if not self.available:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        return self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=filter_dict
        )
    
    def count(self):
        if not self.available:
            return len(self._fallback_docs)
        return self.collection.count()

vector_store = VectorStore()