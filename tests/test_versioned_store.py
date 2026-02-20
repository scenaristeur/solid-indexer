# https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../')

import os
import logging
from dotenv import load_dotenv
from solid_auth import SolidAuthenticatedSession
from solid_versioned_store import SolidVersionedStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def test_crud():
    # Initialisation
    session = SolidAuthenticatedSession(
        idp_url=os.getenv("SOLID_IDP_URL"),
        client_id=os.getenv("SOLID_CLIENT_ID"),
        client_secret=os.getenv("SOLID_CLIENT_SECRET")
    )
    # À ajuster selon votre pod
    webid =  "http://localhost:3000/david/profile/card#me"  # À récupérer depuis la session
    store = SolidVersionedStore(session, base_container="http://localhost:3000/david/notes/", webid=webid)

    # 1. Créer une note
    logger.info("Création d'une note...")
    uri = store.create_resource(
        name="test-note",
        content="Ceci est une note de test.",
        tags="test, demo"
    )
    logger.info(f"Note créée : {uri}")

    # 2. Lire la ressource logique
    resp = session.request('GET', uri, headers={'Accept': 'text/turtle'})
    if resp.status_code == 200:
        logger.info("✅ Ressource logique accessible.")
        logger.debug("Contenu : " + resp.text[:200])
    else:
        logger.error(f"❌ Erreur lecture ressource logique: {resp.status_code}")

    # 3. Lister les versions
    versions_container = store._versions_container(uri)
    resp = session.request('GET', versions_container, headers={'Accept': 'text/turtle'})
    if resp.status_code == 200:
        logger.info("✅ Conteneur de versions accessible.")
    else:
        logger.error(f"❌ Erreur lecture conteneur versions: {resp.status_code}")

    # 4. Mettre à jour la note
    logger.info("Mise à jour de la note...")
    new_version = store.update_resource(uri, "Nouveau contenu après mise à jour.")
    logger.info(f"Nouvelle version créée : {new_version}")

    # 5. Vérifier que la ressource logique pointe vers la nouvelle version
    resp = session.request('GET', uri, headers={'Accept': 'text/turtle'})
    if resp.status_code == 200:
        logger.info("✅ Ressource logique mise à jour.")
    else:
        logger.error("❌ Erreur après mise à jour")

    # 6. Supprimer (archiver) la note
    logger.info("Suppression de la note...")
    store.delete_resource(uri)
    logger.info("Note supprimée (archivée).")

    # 7. Vérifier le statut deleted
    resp = session.request('GET', uri, headers={'Accept': 'text/turtle'})
    if resp.status_code == 200:
        logger.info("✅ Ressource logique toujours accessible avec statut deleted.")
    else:
        logger.error("❌ Ressource logique inaccessible après suppression ?")

    # 8. Recréer la même note (devrait fonctionner)
    logger.info("Recréation de la note...")
    uri2 = store.create_resource(
        name="test-note",
        content="Nouvelle note après suppression.",
        tags="test"
    )
    logger.info(f"Nouvelle note créée : {uri2}")

if __name__ == "__main__":
    test_crud()