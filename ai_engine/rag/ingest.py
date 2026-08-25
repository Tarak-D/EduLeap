import json
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ai_engine.rag.vector_store import vector_store

def ingest_curriculum(file_path: str):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    documents = []
    ids = []
    metadatas = []
    
    for i, item in enumerate(data.get("concepts", [])):
        doc = f"Concept: {item['name']}\nLevel: {item['level']}\nDescription: {item['description']}\nExamples: {item.get('examples', '')}\nCommon Mistakes: {item.get('common_mistakes', '')}"
        documents.append(doc)
        ids.append(f"concept_{i}")
        metadatas.append({"level": item["level"], "topic": item["name"], "type": "concept"})
    
    if documents:
        vector_store.add_documents(documents, ids, metadatas)
        print(f"Ingested {len(documents)} concepts into vector store.")
    else:
        print("No concepts found.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ingest_curriculum(sys.argv[1])
    else:
        # Default path
        ingest_curriculum("ai_engine/knowledge_base/curriculum/math_foundation.json")