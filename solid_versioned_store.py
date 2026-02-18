import os
import time
from datetime import datetime
import rdflib
from rdflib import Graph, URIRef, Literal, Namespace
from urllib.parse import urljoin, urlparse
import requests
import logging

logger = logging.getLogger(__name__)

# Namespaces
EX = Namespace("http://example.org/ns#")
DCT = Namespace("http://purl.org/dc/terms/")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

class SolidVersionedStore:
    def __init__(self, session, base_container, webid):
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

    def _set_acl(self, uri):
        """
        Crée un fichier ACL pour la ressource/dossier uri.
        Utilise le modèle fourni.
        """
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
        acl_content = acl_template.format(webid=self.webid)
        acl_uri = uri.rstrip('/') + '.acl'
        resp = self.session.request('PUT', acl_uri, data=acl_content,
                                    headers={'Content-Type': 'text/turtle'})
        if resp.status_code in (200, 201, 205):  # 205 Reset Content est aussi un succès
            logger.info(f"✅ ACL créé pour {uri}")
        else:
            logger.error(f"❌ Échec création ACL pour {uri}: {resp.status_code}")

    def _ensure_container(self, container_uri):
        """Crée un conteneur LDP s'il n'existe pas, avec ACL."""
        resp = self.session.request('HEAD', container_uri)
        if resp.status_code == 404:
            logger.info(f"Création du conteneur {container_uri}")
            resp = self.session.request('PUT', container_uri,
                headers={'Content-Type': 'text/turtle',
                         'Link': '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'})
            if resp.status_code in (200, 201):
                logger.info(f"✅ Conteneur {container_uri} créé")
                self._set_acl(container_uri)
            else:
                logger.error(f"❌ Échec création conteneur {container_uri}: {resp.status_code}")
        elif resp.status_code != 200:
            logger.warning(f"HEAD sur {container_uri} a retourné {resp.status_code}")

    def create_resource(self, name, content, rdf_type=EX.Note, **extra_triples):
        """
        Crée une nouvelle ressource versionnée.
        - name : slug (ex: "ma-note")
        - content : contenu textuel de la première version
        - rdf_type : type RDF de la ressource (par défaut Note)
        - extra_triples : dictionnaire de propriétés à ajouter à la ressource logique (tags, etc.)
        Retourne l'URI de la ressource logique.
        """
        resource_uri = self._resource_uri(name)
        versions_container = self._versions_container(resource_uri)
        timestamp = self._timestamp()
        version_uri = self._version_uri(resource_uri, timestamp)

        # 1. S'assurer que le conteneur de base existe
        self._ensure_container(self.base_container)

        # 2. Créer la ressource logique en tant que conteneur (sans latestVersion pour l'instant)
        resource_graph = Graph()
        resource_graph.add((URIRef(resource_uri), RDF.type, rdf_type))
        for k, v in extra_triples.items():
            resource_graph.add((URIRef(resource_uri), EX[k], Literal(v)))
        resource_data = resource_graph.serialize(format='turtle')
        headers = {
            'Content-Type': 'text/turtle',
            'Link': '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'
        }
        resp = self.session.request('PUT', resource_uri, data=resource_data, headers=headers)
        if resp.status_code not in (200, 201):
            logger.error(f"❌ Échec création conteneur {resource_uri}: {resp.status_code}")
            return None
        self._set_acl(resource_uri)

        # 3. Créer le conteneur de versions à l'intérieur
        self._ensure_container(versions_container)

        # 4. Créer la première version
        version_graph = Graph()
        version_graph.add((URIRef(version_uri), RDF.type, EX.Version))
        version_graph.add((URIRef(version_uri), DCT.created, Literal(datetime.utcnow().isoformat() + 'Z',
                            datatype=URIRef("http://www.w3.org/2001/XMLSchema#dateTime"))))
        version_graph.add((URIRef(version_uri), EX.content, Literal(content)))
        version_graph.add((URIRef(version_uri), EX.versionOf, URIRef(resource_uri)))
        version_data = version_graph.serialize(format='turtle')
        resp = self.session.request('PUT', version_uri, data=version_data,
                                    headers={'Content-Type': 'text/turtle'})
        if resp.status_code not in (200, 201):
            logger.error(f"❌ Échec création version {version_uri}: {resp.status_code}")
            return None
        # Optionnel : ACL pour la version (héritée du conteneur, donc pas nécessaire)

        # 5. Mettre à jour la ressource logique avec le lien latestVersion
        # On récupère le graphe actuel, on ajoute le triple, on remet
        resp = self.session.request('GET', resource_uri, headers={'Accept': 'text/turtle'})
        if resp.status_code != 200:
            logger.error(f"Impossible de lire {resource_uri} pour mise à jour: {resp.status_code}")
            return None
        graph = Graph().parse(data=resp.text, format='turtle')
        graph.add((URIRef(resource_uri), EX.latestVersion, URIRef(version_uri)))
        new_data = graph.serialize(format='turtle')
        resp = self.session.request('PUT', resource_uri, data=new_data,
                                    headers={'Content-Type': 'text/turtle',
                                             'Link': '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'})
        if resp.status_code not in (200, 201):
            logger.error(f"❌ Échec mise à jour de {resource_uri} avec latestVersion: {resp.status_code}")
            return None

        logger.info(f"✅ Ressource créée : {resource_uri}")
        return resource_uri

    def update_resource(self, resource_uri, new_content):
        """
        Met à jour une ressource existante en créant une nouvelle version.
        Retourne l'URI de la nouvelle version.
        """
        # 1. Récupérer la ressource logique pour connaître la dernière version
        resp = self.session.request('GET', resource_uri, headers={'Accept': 'text/turtle'})
        if resp.status_code != 200:
            raise Exception(f"Ressource {resource_uri} introuvable (code {resp.status_code})")
        graph = Graph().parse(data=resp.text, format='turtle')

        # Trouver la dernière version
        latest = None
        for s, p, o in graph.triples((URIRef(resource_uri), EX.latestVersion, None)):
            latest = str(o)
            break
        if not latest:
            raise Exception("Pas de version trouvée")

        # 2. Créer une nouvelle version
        timestamp = self._timestamp()
        new_version_uri = self._version_uri(resource_uri, timestamp)

        version_graph = Graph()
        version_graph.add((URIRef(new_version_uri), RDF.type, EX.Version))
        version_graph.add((URIRef(new_version_uri), DCT.created, Literal(datetime.utcnow().isoformat() + 'Z')))
        version_graph.add((URIRef(new_version_uri), EX.content, Literal(new_content)))
        version_graph.add((URIRef(new_version_uri), EX.versionOf, URIRef(resource_uri)))
        version_graph.add((URIRef(new_version_uri), EX.previousVersion, URIRef(latest)))
        version_data = version_graph.serialize(format='turtle')
        resp = self.session.request('PUT', new_version_uri, data=version_data,
                                    headers={'Content-Type': 'text/turtle'})
        if resp.status_code not in (200, 201):
            logger.error(f"❌ Échec création nouvelle version {new_version_uri}: {resp.status_code}")
            return None

        # 3. Mettre à jour le lien latestVersion dans la ressource logique
        # On récupère à nouveau le graphe (au cas où il aurait changé)
        resp = self.session.request('GET', resource_uri, headers={'Accept': 'text/turtle'})
        graph = Graph().parse(data=resp.text, format='turtle')
        # Supprimer l'ancien latestVersion et ajouter le nouveau
        graph.remove((URIRef(resource_uri), EX.latestVersion, None))
        graph.add((URIRef(resource_uri), EX.latestVersion, URIRef(new_version_uri)))
        graph.set((URIRef(resource_uri), DCT.modified, Literal(datetime.utcnow().isoformat() + 'Z')))
        new_data = graph.serialize(format='turtle')
        resp = self.session.request('PUT', resource_uri, data=new_data,
                                    headers={'Content-Type': 'text/turtle',
                                             'Link': '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'})
        if resp.status_code not in (200, 201):
            logger.error(f"❌ Échec mise à jour ressource logique {resource_uri}: {resp.status_code}")
            return None

        logger.info(f"✅ Nouvelle version créée : {new_version_uri}")
        return new_version_uri

    def delete_resource(self, resource_uri):
        """
        Marque une ressource comme supprimée en créant une version spéciale et en mettant à jour le statut.
        """
        # Récupérer la dernière version
        resp = self.session.request('GET', resource_uri, headers={'Accept': 'text/turtle'})
        if resp.status_code != 200:
            raise Exception(f"Ressource {resource_uri} introuvable (code {resp.status_code})")
        graph = Graph().parse(data=resp.text, format='turtle')

        latest = None
        for s, p, o in graph.triples((URIRef(resource_uri), EX.latestVersion, None)):
            latest = str(o)
            break

        # Créer une version "deleted"
        timestamp = self._timestamp()
        version_uri = self._version_uri(resource_uri, timestamp)

        version_graph = Graph()
        version_graph.add((URIRef(version_uri), RDF.type, EX.Version))
        version_graph.add((URIRef(version_uri), DCT.created, Literal(datetime.utcnow().isoformat() + 'Z')))
        version_graph.add((URIRef(version_uri), EX.content, Literal("")))
        version_graph.add((URIRef(version_uri), EX.versionOf, URIRef(resource_uri)))
        version_graph.add((URIRef(version_uri), EX.status, EX.deleted))
        if latest:
            version_graph.add((URIRef(version_uri), EX.previousVersion, URIRef(latest)))
        version_data = version_graph.serialize(format='turtle')
        resp = self.session.request('PUT', version_uri, data=version_data,
                                    headers={'Content-Type': 'text/turtle'})
        if resp.status_code not in (200, 201):
            logger.error(f"❌ Échec création version de suppression {version_uri}: {resp.status_code}")
            return

        # Mettre à jour la ressource logique
        graph.set((URIRef(resource_uri), EX.latestVersion, URIRef(version_uri)))
        graph.add((URIRef(resource_uri), EX.status, EX.deleted))
        graph.set((URIRef(resource_uri), DCT.modified, Literal(datetime.utcnow().isoformat() + 'Z')))
        new_data = graph.serialize(format='turtle')
        resp = self.session.request('PUT', resource_uri, data=new_data,
                                    headers={'Content-Type': 'text/turtle',
                                             'Link': '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'})
        if resp.status_code not in (200, 201):
            logger.error(f"❌ Échec mise à jour après suppression {resource_uri}: {resp.status_code}")
        else:
            logger.info(f"✅ Ressource {resource_uri} marquée comme supprimée")