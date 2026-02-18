import chromadb
client = chromadb.PersistentClient(path="./chroma_storage")
collection = client.get_collection("mon_pod")
all_docs = collection.get(include=["documents", "metadatas"])
for i, (doc, meta) in enumerate(zip(all_docs['documents'], all_docs['metadatas'])):
    if "Lila" in doc:
        print(f"Trouvé: {meta['uri']}")
        print(doc[:500])
        break
    else:
        print("pas trouvé dans ",len(all_docs))