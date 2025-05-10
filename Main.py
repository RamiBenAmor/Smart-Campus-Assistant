import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def retrieve_relevant_texts(query, k=1,n=1):
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    if(n==1):
        with open("C:\\Users\\ramib\\Downloads\\HaCKATON\\HAChaton\\texts.pkl", "rb") as f:
           texts = pickle.load(f)
        #embeddings = np.load("embeddings.npy")
        index1 = faiss.read_index("faiss_index.index")
    else:
        with open("C:\\Users\\ramib\\Downloads\\HaCKATON\\HAChaton\\texts2.pkl", "rb") as f:
           texts = pickle.load(f)
        #embeddings = np.load("embeddings.npy")
        index1 = faiss.read_index("faiss_index2.index")   
    # Convertir la requête en embedding
    query_embedding = embedding_model.encode([query])

    # Recherche dans l'index FAISS
    _, indices = index1.search(np.array(query_embedding, dtype=np.float32), k)  # Recherche dans l'index

    # Récupérer les textes pertinents en fonction des indices retournés
    retrieved_texts = [texts[i] for i in indices[0]]

    return retrieved_texts

