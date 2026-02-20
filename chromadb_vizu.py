#https://medium.com/@DevChris01/3d-embedding-visualization-with-python-and-chromadb-8189f696c8a8 # sklearn deprecated
# https://github.com/mtybadger/chromaviz
import chromadb
from chromadb.config import Settings
from sklearn.decomposition import PCA
import plotly.express as px


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
embeddings = collection.get(include=['embeddings'])['embeddings']
docs = collection.get(include=['embeddings'])['ids']


# Reduce the embedding dimensionality
pca = PCA(n_components=3)
vis_dims = pca.fit_transform(embeddings)# Create an interactive 3D plot
fig = px.scatter_3d(
    x=vis_dims[:, 0],
    y=vis_dims[:, 1],
    z=vis_dims[:, 2],
    text=docs,
    labels={'x': 'PCA Component 1', 'y': 'PCA Component 2', 'z': 'PCA Component 3'}, # Name it like you want
    title='3D PCA of Embeddings' # Name it like you want
)

fig.show()