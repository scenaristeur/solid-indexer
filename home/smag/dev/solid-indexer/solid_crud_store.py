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
    if resp.status_code in (200, 201):
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