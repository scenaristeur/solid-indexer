import os
import time
from datetime import datetime
import rdflib
from rdflib import Graph, URIRef, Literal, Namespace
from urllib.parse import urljoin, urlparse
import requests
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Namespaces
EX = Namespace("http://example.org/ns#")
DCT = Namespace("http://purl.org/dc/terms/")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

class SolidVersionedStore:
    def __init__(self, session, base_container, webid):
        """
        session : instance de SolidAuthenticatedSession
        base_container : URI du conteneur racine pour les ressources (ex: http://localhost:3000/david/notes/)
        """
        self.session = session
        self.base_container = base_container.rstrip('/') + '/'
        self.webid = webid
        logger.info(f"Store initialisé avec WebID: {webid}")

    def _timestamp(self):
        return datetime.utcnow().strftime("%Y%m%dT%H%M%S")

    def _resource_uri(self, name):
        """Génère l'URI d'une ressource logique à partir d'un nom (slug)."""
        return urljoin(self.base_container, name)

    def _versions_container(self, resource_uri):
        """Retourne l'URI du conteneur de versions pour une ressource."""
        return resource_uri.rstrip('/') + '/versions/'

    def _version_uri(self, resource_uri, timestamp):
        """URI d'une version spécifique."""
        return urljoin(self._versions_container(resource_uri), timestamp)

    def _set_acl(self, uri, acl_template=None):
        """
        Crée un fichier ACL pour la ressource/dossier uri.
        Utilise un modèle par défaut si non fourni.
        """
        if acl_template is None:
            # Modèle par défaut avec des placeholders à remplacer
            acl_template = """@prefix : <#>.
    @prefix acl: <http://www.w3.org/ns/auth/acl#>.
    @prefix foaf: <http://xmlns.com/foaf/0.1/>.
    @prefix c: <{webid}>.

    :ControlReadWrite
        a acl:Authorization;
        acl:accessTo <./>;
        acl:agent <{webid}>;
        acl:default <./>;
        acl:mode acl:Control, acl:Read, acl:Write.

    :Read
        a acl:Authorization;
        acl:accessTo <./>;
        acl:agentClass foaf:Agent;
        acl:default <./>;
        acl:mode acl:Read.
    """
        # Remplacer {webid} par le WebID de l'utilisateur
        # Le WebID peut être obtenu à partir de la session (par exemple self.session.webid)
        # Mais notre classe SolidAuthenticatedSession n'a pas encore cette info. On peut la passer en paramètre ou la stocker lors de l'initialisation.
        # Pour l'instant, on suppose que le WebID est disponible via une variable d'instance ou on le demande.
        if not hasattr(self, 'webid'):
            # On peut le récupérer depuis la session (si elle a une méthode pour cela)
            # Exemple : on pourrait faire un GET sur l'IDP pour obtenir le WebID associé au token.
            # Mais pour simplifier, on le passe en paramètre du constructeur.
            raise ValueError("WebID non défini, impossible de créer l'ACL")

        acl_content = acl_template.format(webid=self.webid)

        acl_uri = uri.rstrip('/') + '.acl'
        resp = self.session.request('PUT', acl_uri, data=acl_content,
                                    headers={'Content-Type': 'text/turtle'})
        if resp.status_code in (200, 201):
            logger.info(f"✅ ACL créé pour {uri}")
        else:
            logger.error(f"❌ Échec création ACL pour {uri}: {resp.status_code}")

    def create_resource(self, name, content, rdf_type=EX.Note, **extra_triples):
        """
        Crée une nouvelle ressource logique et sa première version.
        - name : slug (ex: "ma-note")
        - content : contenu textuel (ou graphe RDF ?)
        - rdf_type : type RDF de la ressource
        - extra_triples : dictionnaire de propriétés supplémentaires à ajouter à la ressource principale
        Retourne l'URI de la ressource logique.
        """
        resource_uri = self._resource_uri(name)
        versions_container = self._versions_container(resource_uri)
        timestamp = self._timestamp()
        version_uri = self._version_uri(resource_uri, timestamp)

        # 1. Créer le conteneur de versions (si nécessaire)
        # On peut faire un PUT sur le conteneur avec un LDP container
        self._ensure_container(versions_container)

        # 2. Créer la version
        version_graph = Graph()
        version_graph.add((URIRef(version_uri), RDF.type, EX.Version))
        version_graph.add((URIRef(version_uri), DCT.created, Literal(datetime.utcnow().isoformat() + 'Z', datatype=URIRef("http://www.w3.org/2001/XMLSchema#dateTime"))))
        version_graph.add((URIRef(version_uri), EX.content, Literal(content)))
        version_graph.add((URIRef(version_uri), EX.versionOf, URIRef(resource_uri)))
        # Ajouter d'autres triplets si besoin

        # Sérialiser en Turtle
        version_data = version_graph.serialize(format='turtle')
        resp = self.session.request('PUT', version_uri, data=version_data, headers={'Content-Type': 'text/turtle'})
        if resp.status_code in (200, 201):
            self._set_acl(resource_uri)  # ACL pour la ressource elle-même

        # 3. Créer ou mettre à jour la ressource logique
        # On va faire un PUT sur resource_uri avec un graphe contenant le type, latestVersion, et extra_triples
        resource_graph = Graph()
        resource_graph.add((URIRef(resource_uri), RDF.type, rdf_type))
        resource_graph.add((URIRef(resource_uri), EX.latestVersion, URIRef(version_uri)))
        for k, v in extra_triples.items():
            resource_graph.add((URIRef(resource_uri), EX[k], Literal(v)))
        resource_data = resource_graph.serialize(format='turtle')
        resp2 = self.session.request('PUT', resource_uri, data=resource_data, headers={'Content-Type': 'text/turtle'})
        if resp2.status_code in (200, 201):
            self._set_acl(resource_uri)  # ACL pour la ressource elle-même

        return resource_uri

    def update_resource(self, resource_uri, new_content):
        """
        Met à jour une ressource existante en créant une nouvelle version.
        Retourne l'URI de la nouvelle version.
        """
        # Récupérer la ressource logique pour connaître la dernière version
        resp = self.session.request('GET', resource_uri, headers={'Accept': 'text/turtle'})
        if resp.status_code != 200:
            raise Exception(f"Ressource {resource_uri} introuvable")
        graph = Graph().parse(data=resp.text, format='turtle')

        # Trouver la dernière version
        latest = None
        for s, p, o in graph.triples((URIRef(resource_uri), EX.latestVersion, None)):
            latest = str(o)
            break
        if not latest:
            raise Exception("Pas de version trouvée")

        # Créer une nouvelle version
        timestamp = self._timestamp()
        new_version_uri = self._version_uri(resource_uri, timestamp)

        # Récupérer l'ancienne version (pour éventuellement copier des infos)
        # On peut juste créer la nouvelle version avec un lien previousVersion
        version_graph = Graph()
        version_graph.add((URIRef(new_version_uri), RDF.type, EX.Version))
        version_graph.add((URIRef(new_version_uri), DCT.created, Literal(datetime.utcnow().isoformat() + 'Z')))
        version_graph.add((URIRef(new_version_uri), EX.content, Literal(new_content)))
        version_graph.add((URIRef(new_version_uri), EX.versionOf, URIRef(resource_uri)))
        version_graph.add((URIRef(new_version_uri), EX.previousVersion, URIRef(latest)))
        version_data = version_graph.serialize(format='turtle')
        self.session.request('PUT', new_version_uri, data=version_data, headers={'Content-Type': 'text/turtle'})

        # Mettre à jour le lien latestVersion dans la ressource logique
        # On fait un PATCH pour ne modifier que ce triple ? Plus simple : récupérer le graphe existant, le modifier et PUT
        # Ici on va faire un PUT complet pour simplifier
        # On pourrait faire un PATCH avec SPARQL Update, mais on va rester simple
        resp = self.session.request('GET', resource_uri, headers={'Accept': 'text/turtle'})
        graph = Graph().parse(data=resp.text, format='turtle')
        # Supprimer l'ancien latestVersion et ajouter le nouveau
        graph.remove((URIRef(resource_uri), EX.latestVersion, None))
        graph.add((URIRef(resource_uri), EX.latestVersion, URIRef(new_version_uri)))
        # Mettre à jour la date de modification si souhaité
        graph.set((URIRef(resource_uri), DCT.modified, Literal(datetime.utcnow().isoformat() + 'Z')))
        new_data = graph.serialize(format='turtle')
        self.session.request('PUT', resource_uri, data=new_data, headers={'Content-Type': 'text/turtle'})

        return new_version_uri

    def delete_resource(self, resource_uri):
        """
        Marque une ressource comme supprimée en créant une version spéciale et en mettant à jour le statut.
        """
        # Créer une version "deleted" avec un contenu vide ou un marqueur
        timestamp = self._timestamp()
        version_uri = self._version_uri(resource_uri, timestamp)

        # Récupérer la dernière version pour lier previousVersion
        resp = self.session.request('GET', resource_uri, headers={'Accept': 'text/turtle'})
        graph = Graph().parse(data=resp.text, format='turtle')
        latest = None
        for s, p, o in graph.triples((URIRef(resource_uri), EX.latestVersion, None)):
            latest = str(o)
            break

        version_graph = Graph()
        version_graph.add((URIRef(version_uri), RDF.type, EX.Version))
        version_graph.add((URIRef(version_uri), DCT.created, Literal(datetime.utcnow().isoformat() + 'Z')))
        version_graph.add((URIRef(version_uri), EX.content, Literal("")))
        version_graph.add((URIRef(version_uri), EX.versionOf, URIRef(resource_uri)))
        version_graph.add((URIRef(version_uri), EX.status, EX.deleted))
        if latest:
            version_graph.add((URIRef(version_uri), EX.previousVersion, URIRef(latest)))
        version_data = version_graph.serialize(format='turtle')
        self.session.request('PUT', version_uri, data=version_data, headers={'Content-Type': 'text/turtle'})

        # Mettre à jour la ressource logique : changer latestVersion et ajouter status=deleted
        graph.set((URIRef(resource_uri), EX.latestVersion, URIRef(version_uri)))
        graph.add((URIRef(resource_uri), EX.status, EX.deleted))
        # On peut aussi supprimer le contenu principal ? Non, on garde juste le statut.
        new_data = graph.serialize(format='turtle')
        self.session.request('PUT', resource_uri, data=new_data, headers={'Content-Type': 'text/turtle'})

        # Optionnel : déplacer la ressource dans /historique ? On peut le faire mais cela change l'URI.
        # On préfère garder l'URI et juste changer le statut.

    # def _ensure_container(self, container_uri):
    #     """Crée un conteneur LDP s'il n'existe pas."""
    #     # On peut faire un HEAD pour vérifier, sinon un PUT avec les bons headers
    #     resp = self.session.request('HEAD', container_uri)
    #     if resp.status_code == 404:
    #         # Créer un conteneur BasicContainer
    #         self.session.request('PUT', container_uri, headers={'Content-Type': 'text/turtle', 'Link': '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'})
    def _ensure_container(self, container_uri):
        resp = self.session.request('HEAD', container_uri)
        if resp.status_code == 404:
            logger.info(f"Création du conteneur {container_uri}")
            resp = self.session.request('PUT', container_uri,
                headers={'Content-Type': 'text/turtle',
                        'Link': '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'})
            if resp.status_code in (200, 201):
                logger.info(f"Conteneur {container_uri} créé avec succès")
                self._set_acl(container_uri)  # Ajout ACL
            else:
                logger.error(f"Échec création conteneur {container_uri}: {resp.status_code}")
        elif resp.status_code != 200:
            logger.warning(f"HEAD sur {container_uri} a retourné {resp.status_code}")