import logging
from datetime import datetime
from urllib.parse import urljoin
import rdflib
from rdflib import Graph, URIRef, Literal, Namespace
import time

logger = logging.getLogger(__name__)

EX = Namespace("http://example.org/ns#")
DCT = Namespace("http://purl.org/dc/terms/")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

class SolidCRUDStore:
    def __init__(self, session, base_container, webid):
        self.session = session
        self.base_container = base_container.rstrip('/') + '/'
        self.webid = webid
        logger.info(f"CRUD Store initialisé avec base: {self.base_container}")

    def _set_acl(self, uri):
        # Ne pas enlever le slash final : l'ACL d'un conteneur doit être uri/.acl
        acl_uri = uri + '.acl'
        acl_template = """@prefix : <#>.
    @prefix acl: <http://www.w3.org/ns/auth/acl#>.
    @prefix foaf: <http://xmlns.com/foaf/0.1/>.
    @prefix c: <{webid}>.

    :ControlReadWrite
        a acl:Authorization;
        acl:accessTo <./>;
        acl:agent <{webid}>;
        acl:default <./>;
        acl:mode acl:Control, acl:Read, acl:Write, acl:Append.

    :Read
        a acl:Authorization;
        acl:accessTo <./>;
        acl:agentClass foaf:Agent;
        acl:default <./>;
        acl:mode acl:Read.
    """
        acl_content = acl_template.format(webid=self.webid)
        resp = self.session.request('PUT', acl_uri, data=acl_content,
                                    headers={'Content-Type': 'text/turtle'})
        if resp.status_code in (200, 201, 205):
            logger.info(f"✅ ACL créé pour {uri}")
            return (f"✅ ACL créé pour {uri}")
        else:
            logger.error(f"❌ Échec création ACL pour {uri}: {resp.status_code}")
            return (f"❌ Échec création ACL pour {uri}: {resp.status_code}")

    def _ensure_container(self, container_uri):
        resp = self.session.request('HEAD', container_uri)
        if resp.status_code == 404:
            logger.info(f"Création du conteneur {container_uri}")
            resp = self.session.request('PUT', container_uri,
                headers={'Content-Type': 'text/turtle',
                         'Link': '<http://www.w3.org/ns/ldp#BasicContainer>; rel="type"'})
            if resp.status_code in (200, 201):
                logger.info(f"✅ Conteneur {container_uri} créé")
                acl_result = self._set_acl(container_uri)
                time.sleep(1)  # laisser l'ACL s'appliquer
                return (f"✅ Conteneur {container_uri} créé, {acl_result}")
            else:
                logger.error(f"❌ Échec création conteneur {container_uri}: {resp.status_code}")
                return (f"❌ Échec création conteneur {container_uri}: {resp.status_code}")
        elif resp.status_code != 200:
            logger.warning(f"HEAD sur {container_uri} a retourné {resp.status_code}")
            return (f"HEAD sur {container_uri} a retourné {resp.status_code}")

    def create_note(self, uri, name, content, predicates=None, **extra):
        """
        Crée une note dans le conteneur de base.
        name: slug (ex: "ma-note")
        content: texte de la note
        predicates: dictionnaire de prédicats supplémentaires
        extra: paires clé-valeur pour métadonnées supplémentaires (ex: tags="tag1,tag2")
        Retourne l'URI de la note.
        """
        container_result = self._ensure_container(uri or self.base_container)

        note_uri = urljoin(uri or self.base_container, name + '.ttl')

        g = Graph()
        g.add((URIRef(note_uri), RDF.type, EX.Note))
        g.add((URIRef(note_uri), EX.content, Literal(content)))
        g.add((URIRef(note_uri), DCT.created, Literal(datetime.utcnow().isoformat() + 'Z',
                    datatype=URIRef("http://www.w3.org/2001/XMLSchema#dateTime"))))
        if predicates:
            for pred, value in predicates.items():
                g.add((URIRef(note_uri), URIRef(pred), Literal(value)))
        for k, v in extra.items():
            g.add((URIRef(note_uri), EX[k], Literal(v)))

        data = g.serialize(format='turtle')
        resp = self.session.request('PUT', note_uri, data=data,
                                    headers={'Content-Type': 'text/turtle'})
        if resp.status_code in (200, 201, 205):
            logger.info(f"✅ Note créée : {note_uri}")
            # self._set_acl(note_uri)
            return note_uri
        else:
            logger.error(f"❌ Échec création note {note_uri}: {resp.status_code}")
            return f("❌ Échec création note {note_uri}: {resp.status_code}, container creation result : {container_result}")

    def update_note(self, uri, new_content, predicates=None, **extra):
        g = Graph()
        g.add((URIRef(uri), RDF.type, EX.Note))
        g.add((URIRef(uri), EX.content, Literal(new_content)))
        g.add((URIRef(uri), DCT.modified, Literal(datetime.utcnow().isoformat() + 'Z',
                    datatype=URIRef("http://www.w3.org/2001/XMLSchema#dateTime"))))
        if predicates:
            for pred, value in predicates.items():
                g.add((URIRef(uri), URIRef(pred), Literal(value)))
        for k, v in extra.items():
            g.add((URIRef(uri), EX[k], Literal(v)))
        data = g.serialize(format='turtle')
        resp = self.session.request('PUT', uri, data=data,
                                    headers={'Content-Type': 'text/turtle'})
        if resp.status_code in (200, 201, 205):
            logger.info(f"✅ Note mise à jour : {uri}")
            return True
        else:
            logger.error(f"❌ Échec mise à jour {uri}: {resp.status_code}")
            return False

    def read_note(self, uri):
        resp = self.session.request('GET', uri, headers={'Accept': 'text/turtle'})
        if resp.status_code != 200:
            logger.error(f"Lecture échouée {uri}: {resp.status_code}")
            return None
        g = Graph().parse(data=resp.text, format='turtle')
        result = {"uri": uri}
        for s, p, o in g.triples((URIRef(uri), None, None)):
            pred = str(p).split('/')[-1].split('#')[-1]
            val = str(o)
            result[pred] = val
        return result

    # def update_note(self, uri, new_content, **extra):
    #     g = Graph()
    #     g.add((URIRef(uri), RDF.type, EX.Note))
    #     g.add((URIRef(uri), EX.content, Literal(new_content)))
    #     g.add((URIRef(uri), DCT.modified, Literal(datetime.utcnow().isoformat() + 'Z',
    #                 datatype=URIRef("http://www.w3.org/2001/XMLSchema#dateTime"))))
    #     for k, v in extra.items():
    #         g.add((URIRef(uri), EX[k], Literal(v)))
    #     data = g.serialize(format='turtle')
    #     resp = self.session.request('PUT', uri, data=data,
    #                                 headers={'Content-Type': 'text/turtle'})
    #     if resp.status_code in (200, 201, 205):
    #         logger.info(f"✅ Note mise à jour : {uri}")
    #         return True
    #     else:
    #         logger.error(f"❌ Échec mise à jour {uri}: {resp.status_code}")
    #         return False

    def delete_note(self, uri):
        resp = self.session.request('DELETE', uri)
        if resp.status_code == 404:
            logger.info(f"✅ La resource n'existe pas : {uri}")
            return True
        elif resp.status_code in (200, 204, 205):
            logger.info(f"✅ Note supprimée : {uri}")
            return True
        else:
            logger.error(f"❌ Échec suppression {uri}: {resp.status_code}")
            return False

    def list_notes(self, uri):
        container_uri = uri or self.base_container
        resp = self.session.request('GET', container_uri, headers={'Accept': 'text/turtle'})
        if resp.status_code != 200:
            logger.error(f"Impossible de lister le conteneur {container_uri}: {resp.status_code}")
            return []
        g = rdflib.Graph().parse(data=resp.text, format='turtle', publicID=container_uri)
        ldp = rdflib.Namespace("http://www.w3.org/ns/ldp#")
        notes = []
        for member in g.objects(rdflib.URIRef(container_uri), ldp.contains):
            member_uri = str(member)
            if member_uri.endswith('.ttl'):
                notes.append(member_uri)
        # Log pour déboguer
        logger.info(f"Membres trouvés dans {container_uri}: {notes}")
        return notes