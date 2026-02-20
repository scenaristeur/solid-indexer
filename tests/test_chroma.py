# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../')

import chromadb
client = chromadb.PersistentClient(path="../chroma_storage")
collection = client.get_collection("mon_pod")
all_docs = collection.get(include=["documents", "metadatas"])
for i, (doc, meta) in enumerate(zip(all_docs['documents'], all_docs['metadatas'])):
    print("\n",doc, meta)
    if "gateau" in doc:
        print(f"Trouvé: {meta['uri']}")
        print(doc[:500])
        break
    else:
        print("pas trouvé dans ",len(all_docs))

# requete mixte vectorielle + filtre sur graphe
# results = collection.query(
#     query_texts=["personne habitant à Paris"],
#     n_results=10,
#     where={"type": "entity", "based_near": "Paris"}  # si based_near est une métadonnée
# )

# print(results)