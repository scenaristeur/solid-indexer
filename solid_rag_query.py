import os
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Chargement des variables d'environnement (pour le LLM optionnel)
load_dotenv()
# logger = logging.getLogger("solid_rag")
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# handler = RotatingFileHandler(
#     'logs/solid_rag_query.log',  # Nom du fichier de log
#     mode='a',
#     maxBytes=5*1024*1024, 
#     backupCount=3,
#     encoding=None,
#     delay=0
#     )
# # Configurer le format et le niveau
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
logger = logging.getLogger("solid_rag_query")
# logger.addHandler(handler)

# logger.info("********** Loading rag_query")

# Tentative d'import d'OpenAI uniquement si la clé est présente
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    from openai import OpenAI

class SolidRAG:
    """
    Moteur de question-réduction utilisant l'index ChromaDB.
    La recherche vectorielle est gérée nativement par ChromaDB (embedding par défaut).
    Si une clé OpenAI est fournie, une réponse est générée par LLM.
    """

    def __init__(self, collection_name="mon_pod", persist_directory="./chroma_storage"):
        # Connexion à la base ChromaDB persistante
        self.client = chromadb.PersistentClient(path=persist_directory, settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_collection(collection_name)

        # Configuration optionnelle pour la génération via LLM
        self.use_llm = OPENAI_API_KEY is not None
        if self.use_llm:
            self.openai_client = OpenAI(
                base_url=os.getenv("OPENAI_BASE_URL"),
                api_key=OPENAI_API_KEY,
            )
            self.chat_model = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")

    def retrieve(self, query, n_results=5):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        docs = results['documents'][0]
        metas = results['metadatas'][0]
        dists = results['distances'][0]
        for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists)):
            logger.info(f"Résultat {i+1}: {meta.get('uri')} (dist={dist:.4f}) - extrait: {doc[:50]}...")
        return list(zip(docs, metas, dists))

    # def retrieve(self, query, n_results=5):
    #     """
    #     Recherche les n passages les plus proches de la requête.
    #     Utilise la fonction d'embedding par défaut de ChromaDB.
    #     Retourne une liste de tuples (document, métadonnées, distance).
    #     """
    #     results = self.collection.query(
    #         query_texts=[query],
    #         n_results=n_results,
    #         include=["documents", "metadatas", "distances"]
    #     )
    #     docs = results['documents'][0]
    #     metas = results['metadatas'][0]
    #     dists = results['distances'][0]
    #     return list(zip(docs, metas, dists))

    def build_prompt(self, query, context_items):
        """Construit un prompt à partir de la question et des documents trouvés."""
        context_text = "\n\n---\n\n".join(
            f"Document (source: {item[1]['uri']}):\n{item[0]}"
            for item in context_items
        )
        prompt = f"""Tu es un assistant utile qui répond aux questions en te basant uniquement sur le contexte fourni.
Si la réponse ne se trouve pas dans le contexte, dis que tu ne sais pas.

Contexte :
{context_text}

Question : {query}

Réponse :"""
        return prompt

    def ask(self, query, n_results=5):
        """
        Pose une question et retourne :
        - si LLM disponible : une réponse générée
        - sinon : les passages bruts trouvés
        """
        context = self.retrieve(query, n_results)
        if not context:
            return "Aucun contexte trouvé pour cette question."

        if self.use_llm:
            prompt = self.build_prompt(query, context)
            logger.info(f"Prompt envoyé au LLM (longueur: {len(prompt)} caractères)")
            response = self.openai_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "Tu réponds de manière précise et concise."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            return response.choices[0].message.content
        else:
            # Affichage simple des résultats
            output = "Résultats de la recherche :\n"
            for i, (doc, meta, dist) in enumerate(context):
                output += f"\n--- Résultat {i+1} (distance: {dist:.4f}) ---\n"
                output += f"Source : {meta.get('uri', 'inconnue')}\n"
                output += f"Type   : {meta.get('type', 'inconnu')}\n"
                output += f"Extrait: {doc[:200]}...\n"
            return output

def main():
    # Paramètres : à adapter selon votre configuration
    rag = SolidRAG(
        collection_name="mon_pod",
        persist_directory="./chroma_storage"
    )
    print("Assistant RAG prêt. Tapez votre question (ou 'quit' pour quitter).")
    while True:
        query = input("\nQuestion: ").strip()
        if query.lower() in ('quit', 'exit'):
            break
        if not query:
            continue
        answer = rag.ask(query)
        print(f"\n{answer}\n")

if __name__ == "__main__":
    main()