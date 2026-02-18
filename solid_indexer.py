import os
import hashlib
import requests
from urllib.parse import urlparse, urljoin
from datetime import datetime
from dateutil import parser as date_parser
import chromadb
from chromadb.config import Settings
import rdflib
from rdflib import Graph, URIRef
import pypdf
import json
import time
import logging
from solid_auth import SolidAuthenticatedSession

from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file and sets them in os.environ

from urllib.parse import urlparse

# Configuration du logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SolidIndexer:
    """
    Indexeur incrémental pour pods Solid avec ChromaDB.
    Parcourt les conteneurs, extrait les métadonnées, vectorise les textes et suit les URI RDF.
    """

    def __init__(self, collection_name="solid_memory", persist_directory="./chroma_db"):
        """
        Initialise le client ChromaDB et crée/récupère une collection.
        """
        self.base_domain = None
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        # self.session = requests.Session()
        self.session = SolidAuthenticatedSession(
            idp_url=os.getenv("SOLID_IDP_URL"),  # ex: https://solid.example.com
            client_id=os.getenv("SOLID_CLIENT_ID"),
            client_secret=os.getenv("SOLID_CLIENT_SECRET")
        )

        # Pour les requêtes non authentifiées (ex: HEAD sur des ressources publiques ?), gardez aussi une session requests simple.
        self.public_session = requests.Session()
        # Ajouter ici vos en-têtes d'authentification Solid si nécessaire
        # self.session.headers.update({"Authorization": "Bearer votre_token"})

        
        # si on ne veut pas charger les url déjà scannées
        #self.load_visited()
        self.visited_urls = set()  # pour éviter les cycles

    def save_visited(self, filename="visited.json"):
        with open(filename, "w") as f:
            json.dump(list(self.visited_urls), f)

    def load_visited(self, filename="visited.json"):
        try:
            with open(filename, "r") as f:
                self.visited_urls = set(json.load(f))
        except FileNotFoundError:
            self.visited_urls = set()

    def fetch_headers(self, url):
        """
        Envoie une requête HEAD pour obtenir les métadonnées HTTP.
        Retourne un dict des en-têtes ou None si erreur.
        """
        try:
            resp = self.session.request('HEAD', url, allow_redirects=True, timeout=10)
            resp.raise_for_status()
            return resp.headers
        except Exception as e:
            logger.warning(f"HEAD {url} a échoué: {e}")
            return None

    def fetch_resource(self, url, accept_header="*/*"):
        """
        Télécharge le contenu d'une ressource avec l'en-tête Accept spécifié.
        Retourne (contenu_binaire, en-têtes_de_réponse) ou (None, None) en cas d'erreur.
        """
        try:
            # Utiliser la session authentifiée (self.session) pour faire la requête
            resp = self.session.request('GET', url, headers={"Accept": accept_header}, timeout=30)
            resp.raise_for_status()
            return resp.content, resp.headers
        except Exception as e:
            logger.error(f"GET {url} a échoué: {e}")
            return None, None
    # def fetch_resource(self, url, accept_header="*/*"):
    #     """
    #     Télécharge le contenu d'une ressource avec l'en-tête Accept spécifié.
    #     Retourne (contenu_binaire, en-têtes_de_réponse) ou (None, None) en cas d'erreur.
    #     """
    #     try:
    #         # resp = self.session.get(url, headers={"Accept": accept_header}, timeout=30)
    #         self.session.request('GET', url, headers={"Accept": accept_header}, timeout=30)
    #         resp.raise_for_status()
    #         return resp.content, resp.headers
    #     except requests.exceptions.RequestException as e:
    #         logger.error(f"GET {url} a échoué: {e}")
    #         return None, None

    def should_reindex(self, uri, etag=None, last_modified=None):
        """
        Vérifie si une ressource doit être réindexée en comparant avec les métadonnées stockées.
        Retourne True si la ressource est nouvelle ou modifiée.
        """
        # Cherche dans la collection les documents ayant cet URI comme métadonnée
        results = self.collection.get(where={"uri": uri})
        if not results or len(results['ids']) == 0:
            return True  # nouvelle ressource

        # Récupère les métadonnées du premier document (on suppose un seul par URI)
        meta = results['metadatas'][0]
        stored_etag = meta.get('etag')
        stored_last_modified = meta.get('last_modified')

        if etag and stored_etag and etag == stored_etag:
            return False  # pas de changement
        if last_modified and stored_last_modified:
            try:
                if date_parser.parse(last_modified) <= date_parser.parse(stored_last_modified):
                    return False
            except:
                pass
        return True

    def extract_text_from_pdf(self, content):
        """Extrait le texte d'un PDF à partir de son contenu binaire."""
        try:
            from io import BytesIO
            reader = pypdf.PdfReader(BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Erreur extraction PDF: {e}")
            return ""

    def extract_text_from_txt(self, content):
        """Décode le contenu texte (suppose UTF-8)."""
        try:
            return content.decode('utf-8')
        except:
            return content.decode('latin-1', errors='ignore')

    def chunk_text(self, text, max_chunk_size=500, overlap=50):
        """
        Découpe un texte en chunks avec chevauchement.
        Version simple par paragraphes puis par phrases si nécessaire.
        """
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current_chunk) + len(para) < max_chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        if current_chunk:
            chunks.append(current_chunk.strip())

        # Si un chunk est trop grand, on le redécoupe par phrases (simple)
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > max_chunk_size:
                sentences = chunk.replace('!', '.').replace('?', '.').split('.')
                sub_chunk = ""
                for sent in sentences:
                    if len(sub_chunk) + len(sent) < max_chunk_size:
                        sub_chunk += sent + ". "
                    else:
                        if sub_chunk:
                            final_chunks.append(sub_chunk.strip())
                        sub_chunk = sent + ". "
                if sub_chunk:
                    final_chunks.append(sub_chunk.strip())
            else:
                final_chunks.append(chunk)

        # Ajout du chevauchement simple (on recolle la fin d'un chunk au début du suivant)
        # Pour garder le code simple, on ne gère pas le chevauchement ici, mais on pourrait.
        return final_chunks

    def index_text_resource(self, uri, content, headers, mime_type):
        """
        Indexe une ressource textuelle (txt, md, pdf) : chunking, embeddings, stockage.
        """
        if 'pdf' in mime_type:
            text = self.extract_text_from_pdf(content)
        else:
            text = self.extract_text_from_txt(content)

        if not text.strip():
            logger.info(f"Ressource {uri} vide, ignorée.")
            return

        chunks = self.chunk_text(text)
        logger.info(f"Indexation de {uri} : {len(chunks)} chunks")

        # Préparer les métadonnées communes
        base_meta = {
            "uri": uri,
            "mime_type": mime_type,
            "etag": headers.get('etag', ''),
            "last_modified": headers.get('last-modified', ''),
            "type": "text"
        }
        # Ajouter d'autres métadonnées si disponibles (auteur via Link? À implémenter plus tard)

        ids = []
        documents = []
        metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_id = hashlib.md5(f"{uri}#chunk{i}".encode()).hexdigest()
            ids.append(chunk_id)
            documents.append(chunk)
            meta = base_meta.copy()
            meta["chunk_index"] = i
            meta["total_chunks"] = len(chunks)
            metadatas.append(meta)

        # Ajouter ou mettre à jour dans ChromaDB
        # On utilise upsert pour remplacer si l'ID existe déjà (cas de mise à jour)
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        logger.info(f"Indexation de {uri} : {len(ids)} chunks/entités insérés (embeddings calculés par ChromaDB)")

    def extract_rdf_entities(self, graph, base_uri):
        """
        Extrait les entités (sujets) d'un graphe RDF et retourne un ensemble d'URI absolues.
        Ne suit que les URI HTTP(S) qui sont dans le même pod ou externes (selon votre choix).
        Ici, on suit toutes les URI HTTP(S) (on pourra filtrer plus tard).
        """
        entities = set()
        for s, p, o in graph:
            if isinstance(s, URIRef) and str(s).startswith(('http://', 'https://')):
                entities.add(str(s))
            if isinstance(o, URIRef) and str(o).startswith(('http://', 'https://')):
                entities.add(str(o))
        return entities

    def index_rdf_resource(self, uri, content, headers, mime_type, depth=0, max_depth=3):
        """
        Parse une ressource RDF (ttl, json-ld, n3, etc.) et indexe ses triplets sous forme de texte.
        On crée un document textuel par entité (sujet) qui décrit ses propriétés.
        """
        graph = Graph()
        try:
            if 'json' in mime_type or 'json-ld' in mime_type:
                graph.parse(data=content.decode('utf-8'), format='json-ld', publicID=uri)
            elif 'turtle' in mime_type or 'ttl' in mime_type:
                graph.parse(data=content.decode('utf-8'), format='turtle', publicID=uri)
            elif 'n3' in mime_type:
                graph.parse(data=content.decode('utf-8'), format='n3', publicID=uri)
            else:
                graph.parse(data=content.decode('utf-8'), publicID=uri)
            logger.info(f"RDF parsé depuis {uri} : {len(graph)} triplets")
        except Exception as e:
            logger.error(f"Erreur parsing RDF pour {uri}: {e}")
            return

    # Extraire les entités (sujets)
        entities = self.extract_rdf_entities(graph, uri)
        logger.info(f"Entités extraites de {uri} : {list(entities)[:10]}...")  # max 10 pour éviter trop de logs

        # Pour chaque entité, on construit une description textuelle
        ids = []
        documents = []
        metadatas = []
        for entity in entities:
            triples = list(graph.triples((URIRef(entity), None, None)))
            if not triples:
                continue
            lines = [f"Entité: {entity}"]
            for s, p, o in triples:
                pred = str(p).split('/')[-1].split('#')[-1]
                obj = str(o) if isinstance(o, URIRef) else o.value if hasattr(o, 'value') else str(o)
                lines.append(f"{pred}: {obj}")
            text = "\n".join(lines)
            # Log un extrait du texte généré (première ligne + quelques suivantes)
            preview = text[:200].replace('\n', ' ')
            logger.info(f"Document généré pour entité {entity} : {preview}...")

            doc_id = hashlib.md5(entity.encode()).hexdigest()
            meta = {
                "uri": entity,
                "source_uri": uri,
                "mime_type": mime_type,
                "etag": headers.get('etag', ''),
                "last_modified": headers.get('last-modified', ''),
                "type": "entity"
            }
            ids.append(doc_id)
            documents.append(text)
            metadatas.append(meta)

        if not ids:
            logger.info(f"Aucune entité à indexer pour {uri}")
            return

        # Calculer les embeddings (selon la version)
        if hasattr(self, 'get_embeddings'):  # Version OpenAI
            batch_size = 100
            all_embeddings = []
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                embeddings = self.get_embeddings(batch_docs)
                if embeddings:
                    all_embeddings.extend(embeddings)
                else:
                    logger.error(f"Échec calcul embeddings pour entités de {uri}")
                    return
            self.collection.upsert(
                ids=ids,
                embeddings=all_embeddings,
                metadatas=metadatas,
                documents=documents
            )
        else:
            self.collection.upsert(
                ids=ids,
                metadatas=metadatas,
                documents=documents
            )
        logger.info(f"✅ Indexation RDF terminée pour {uri} : {len(ids)} entités insérées dans ChromaDB")

        # # Extraire les entités (sujets) de ce graphe
        # entities = self.extract_rdf_entities(graph, uri)

        # # Pour chaque entité, on construit une description textuelle à partir des triplets
        # for entity in entities:
        #     # Récupérer tous les triplets où cette entité est sujet
        #     triples = list(graph.triples((URIRef(entity), None, None)))
        #     if not triples:
        #         continue
        #     # Construire un texte lisible
        #     lines = [f"Entité: {entity}"]
        #     for s, p, o in triples:
        #         pred = str(p).split('/')[-1].split('#')[-1]  # simplifier le prédicat
        #         obj = str(o) if isinstance(o, URIRef) else o.value if hasattr(o, 'value') else str(o)
        #         lines.append(f"{pred}: {obj}")
        #     text = "\n".join(lines)

        #     # Métadonnées pour ce document
        #     meta = {
        #         "uri": entity,  # l'URI de l'entité
        #         "source_uri": uri,  # la ressource d'origine
        #         "mime_type": mime_type,
        #         "etag": headers.get('etag', ''),
        #         "last_modified": headers.get('last-modified', ''),
        #         "type": "entity"
        #     }

        #     # Générer un ID unique pour ce document d'entité
        #     doc_id = hashlib.md5(entity.encode()).hexdigest()

        #     # On utilise upsert pour mettre à jour si l'entité existe déjà
        #     self.collection.upsert(
        #         ids=[doc_id],
        #         documents=[text],
        #         metadatas=[meta]
        #     )
        #     logger.info(f"Entité indexée : {entity}")
        #     if entity != uri and entity.startswith(('http://', 'https://')) and entity.startswith(self.base_domain):
        #         self.process_resource(entity, depth+1, max_depth)

        # Option : on pourrait aussi indexer le graphe complet comme un document texte
        # (mais on se concentre sur les entités)

    def process_resource(self, uri, depth=0, max_depth=3):
        """
        Traite une ressource identifiée par son URI.
        - Si c'est un conteneur (se termine par / ou en-tête Link: type container), on liste son contenu.
        - Si c'est une ressource RDF, on l'indexe et on suit les entités.
        - Si c'est un fichier texte, on l'indexe.
        - On évite les cycles via self.visited_urls.
        """
        logger.info(f"Traitement de {uri} (profondeur {depth})")
        if uri in self.visited_urls or depth > max_depth:
            return
        self.visited_urls.add(uri)

        logger.info(f"Traitement de {uri} (profondeur {depth})")

        # Étape 1 : obtenir les en-têtes HEAD pour décider si on doit indexer
        headers = self.fetch_headers(uri)
        if not headers:
            # Peut-être que HEAD n'est pas supporté, on tente GET avec Range: bytes=0-0 ?
            # On va plutôt considérer que la ressource est accessible et on passera à l'étape suivante.
            # Mais on ne peut pas vérifier la modification. On va forcer le téléchargement si on ne peut pas vérifier.
            logger.warning(f"HEAD non disponible pour {uri}, on va télécharger (risque de surcharge).")
            etag = None
            last_modified = None
            doit_indexer = True  # on ne peut pas savoir
        else:
            # Récupérer les infos de cache
            content_type = headers.get('content-type', '').split(';')[0].strip()
            etag = headers.get('etag')
            last_modified = headers.get('last-modified')
            # Vérifier si c'est un conteneur LDP (Link: <http://www.w3.org/ns/ldp#Container>; rel="type")
            link = headers.get('link', '')
            is_container = 'rel="type"' in link and 'ldp#Container' in link or uri.endswith('/')
            # Vérifier si la ressource a changé
            doit_indexer = self.should_reindex(uri, etag, last_modified)

        if not doit_indexer:
            logger.info(f"{uri} non modifié, ignoré.")
            # Même si la ressource n'a pas changé, il faut peut-être explorer ses liens (si conteneur)
            # On va quand même vérifier si c'est un conteneur pour lister son contenu, car le contenu peut avoir changé même si le conteneur lui-même est inchangé.
            # Mais les en-têtes du conteneur peuvent ne pas refléter les changements des enfants. On va donc toujours lister les conteneurs, sans re-télécharger la ressource elle-même.
            # On simule un appel pour obtenir la liste des enfants si c'est un conteneur.
            if is_container:
                self.list_container(uri, depth)
            return

        # Télécharger la ressource
        accept = "*/*"
        if uri.endswith('.ttl'):
            accept = "text/turtle"
        elif uri.endswith('.jsonld') or uri.endswith('.json'):
            accept = "application/ld+json, application/json"
        elif uri.endswith('.n3'):
            accept = "text/n3"
        elif uri.endswith('.pdf'):
            accept = "application/pdf"
        elif uri.endswith('.md') or uri.endswith('.txt'):
            accept = "text/plain"

        content, resp_headers = self.fetch_resource(uri, accept_header=accept)
        if content is None:
            return

        # Mise à jour des headers avec ceux de la réponse GET (peuvent différer)
        headers = resp_headers or headers
        content_type = headers.get('content-type', '').split(';')[0].strip()
        etag = headers.get('etag', etag)
        last_modified = headers.get('last-modified', last_modified)
        logger.info(f"content: {content} ")
        # Détecter si c'est un conteneur (via Link header ou fin par /)
        link = headers.get('link', '')
        is_container = 'rel="type"' in link and 'ldp#Container' in link or uri.endswith('/')
        logger.info(f"is_container: {is_container} ")
        if is_container:
            self.list_container(uri, depth)
            logger.info(f"Conteneur {uri} listé, mais non indexé directement")
            return
        elif 'text/turtle' in content_type or 'application/ld+json' in content_type or 'text/n3' in content_type or 'application/rdf+xml' in content_type or uri.endswith(('.ttl','.jsonld','.n3','.rdf')):
            # Ressource RDF
            logger.info(f"Ressource RDF détectée : {uri}")
            self.index_rdf_resource(uri, content, headers, content_type)
            # Après avoir indexé les entités de cette ressource, on peut suivre les URI des entités pour indexer leur description
            # Mais attention à ne pas créer de boucles infinies. On peut décider de suivre uniquement les URI qui sont dans le même domaine ou pod.
            # Ici, pour l'exemple, on va suivre toutes les URI HTTP découvertes (avec limite de profondeur)
            # On extrait les entités de la ressource (sujets et objets)
            graph = Graph()
            try:
                graph.parse(data=content, format=self._guess_format(uri, content_type), publicID=uri)
                entities = self.extract_rdf_entities(graph, uri)
                for ent in entities:
                    # On évite de se suivre soi-même et on limite la profondeur
                    if ent != uri and ent.startswith(('http://', 'https://')):
                        self.process_resource(ent, depth+1, max_depth)
            except Exception as e:
                logger.error(f"Erreur parsing RDF pour extraction d'entités: {e}")
        elif 'text/plain' in content_type or 'text/markdown' in content_type or uri.endswith(('.txt','.md')):
            # Fichier texte
            self.index_text_resource(uri, content, headers, content_type)
        elif 'application/pdf' in content_type or uri.endswith('.pdf'):
            self.index_text_resource(uri, content, headers, content_type)
        else:
            logger.info(f"Type de contenu non géré pour {uri}: {content_type}")

    def _guess_format(self, uri, content_type):
        """Devine le format RDF à partir de l'URI ou du content-type."""
        if uri.endswith('.ttl') or 'turtle' in content_type:
            return 'turtle'
        if uri.endswith('.n3') or 'n3' in content_type:
            return 'n3'
        if uri.endswith('.jsonld') or 'json-ld' in content_type:
            return 'json-ld'
        if uri.endswith('.rdf') or 'rdf+xml' in content_type:
            return 'xml'
        return 'turtle'  # fallback

    def list_container(self, uri, depth, content=None):
        """
        Liste les ressources d'un conteneur Solid.
        Si content est fourni, on l'utilise (c'est le body RDU du conteneur). Sinon, on le télécharge.
        """
        logger.info(f"Listage du conteneur {uri}")
            # Télécharger la représentation du conteneur (généralement en turtle)
        content, headers = self.fetch_resource(uri, accept_header="text/turtle")
        if content is None or headers is None:
            logger.error(f"Impossible de récupérer le contenu du conteneur {uri}")
            return
        # Vérifier le type de contenu
        content_type = headers.get('content-type', '').split(';')[0].strip()
        if 'text/turtle' not in content_type and 'application/ld+json' not in content_type and 'text/n3' not in content_type:
            logger.warning(f"Le conteneur {uri} n'est pas en RDF (type: {content_type}), on ignore son contenu")
            return


        # Parser le RDF pour trouver les membres (ldp:contains)
        graph = Graph()
        try:
            # Décoder le contenu en string si c'est bytes (optionnel)
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            graph.parse(data=content, format='turtle', publicID=uri)
            logger.info(f"Nombre de triplets total: {len(graph)}")
            count_subject = len(list(graph.triples((URIRef(uri), None, None))))
            logger.info(f"Triplets avec sujet {uri}: {count_subject}")
        except Exception as e:
            logger.error(f"Erreur parsing du conteneur {uri}: {e}")
            return

        # Chercher les triplets <uri> ldp:contains ?member
        ldp = rdflib.Namespace("http://www.w3.org/ns/ldp#")
        logger.info(f"ldp: {ldp}")
        for member in graph.objects(URIRef(uri), ldp.contains):
            member_uri = str(member)
            if member_uri.startswith(self.base_domain):
                logger.info(f"Membre trouvé : {member_uri}")
                self.process_resource(member_uri, depth+1)
            else:
                logger.debug(f"Membre hors domaine ignoré : {member_uri}")

        # Alternative : si le conteneur utilise un vocabulaire différent (ex: schema.org), on pourrait chercher d'autres prédicats.
        # On peut aussi simplement suivre tous les liens RDF de type Resource.
        # Pour plus de robustesse, on pourrait également chercher les sujets qui sont des conteneurs enfants.

    def run(self, start_url):
        """
        Lance l'indexation à partir d'une URL de départ (pod ou dossier).
        """
        logger.info(f"Démarrage de l'indexation depuis {start_url}")
        parsed = urlparse(start_url)
        self.base_domain = f"{parsed.scheme}://{parsed.netloc}"
        logger.info(f"Démarrage de l'indexation depuis {start_url} (domaine: {self.base_domain})")
        self.process_resource(start_url, depth=0, max_depth=5)
        count = self.collection.count()
        logger.info(f"Nombre total de documents dans la collection : {count}")
        self.save_visited()

# if __name__ == "__main__":  # remarquez les doubles underscores
#     indexer = SolidIndexer(collection_name="mon_pod", persist_directory="./chroma_storage") # À remplacer par l'URL de votre pod ou dossier Solid
#     # start = "https://votre-pod.solidcommunity.net/"
#     # start = "http://localhost:3000/david/profile/card#me"
#     # start = "http://localhost:3000/david/"
#     start = "http://localhost:3000/david/holacratie/"
#     indexer.run(start)
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Indexeur incrémental pour pods Solid")
    parser.add_argument("start_url", help="URL de départ (pod ou dossier) à indexer")
    parser.add_argument("--collection", default="mon_pod", help="Nom de la collection ChromaDB (défaut: mon_pod)")
    parser.add_argument("--persist", default="./chroma_storage", help="Répertoire de persistance ChromaDB (défaut: ./chroma_storage)")
    args = parser.parse_args()

    indexer = SolidIndexer(collection_name=args.collection, persist_directory=args.persist)
    indexer.run(args.start_url)