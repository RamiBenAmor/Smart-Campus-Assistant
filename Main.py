import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import ctransformers

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



def get_contextual_response(context,question):
    llm = ctransformers.AutoModelForCausalLM.from_pretrained(
    'C:\\Users\\ramib\\Downloads\\chatbot_interface1\\chatbot_interface\\llama-2-7b-chat.Q4_K_M.gguf',
    model_type='llama',
    max_new_tokens=256,
    temperature=0.5, #0.1 kenit
    gpu_layers=30,
    context_length=512  
)
    # Construction stricte du prompt LLaMA 2
    prompt = f"""<s>[INST] <<SYS>>
    Respond to the question using only this
    context:{context}
    <</SYS>>

    Question : {question} [/INST]"""
    try:
        # Génération contrôlée
        response = llm(
            prompt,
            max_new_tokens=512,
            temperature=0.5,  # Réduit les hallucinations
            top_p=0.95,        # Contrôle de la diversité
            stop=["</s>", "[INST]"]  # Tokens d'arrêt
        )

        # Nettoyage de la réponse
        response = response.split("[/INST]")[-1].strip()
        response = response.replace("<s>", "").replace("</s>", "").strip()

        return response

    except Exception as e:
        return f"Erreur de génération : {str(e)}"
    
