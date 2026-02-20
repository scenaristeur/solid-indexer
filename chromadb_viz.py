# pip install git+https://github.com/mtybadger/chromaviz/
# pip install flask flask-cors numpy chromadb pandas scikit-learn

from chromaviz import visualize_collection
import chromadb
from chromadb.config import Settings

collection_name= "mon_pod"
persist_directory="./chroma_storage"
# Get embeddings
# chroma = chromadb.HttpClient(host="localhost", port=8000)
# collection = chroma.get_collection("my_collection")
client = chromadb.PersistentClient(path=persist_directory, settings=Settings(anonymized_telemetry=False))
collection = client.get_collection(
    name=collection_name,
    # metadata={"hnsw:space": "cosine"}
)

visualize_collection(collection)

# ERROR

# [21 rows x 384 columns]
# Size of the dataframe: (21, 384)
# [2026-02-20 14:15:46,993] ERROR in app: Exception on /data [GET]
# raise ValueError(
# ValueError: n_components=50 must be between 0 and min(n_samples, n_features)=21 with svd_solver='full'
# 127.0.0.1 - - [20/Feb/2026 14:15:46] "GET /data HTTP/1.1" 500 -